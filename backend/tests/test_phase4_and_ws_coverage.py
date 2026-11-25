import hashlib
import hmac
import uuid
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.websockets import WebSocketDisconnect

from api.api_v1.endpoints import matchmaker
from api.deps import require_roles, user_has_role
from core.config import settings
from core.security import create_access_token, create_refresh_token
from db.models import (
    Application,
    CareerReadinessScore,
    CognitiveProfile,
    Resume,
    ResumeScore,
    Role,
    SkillEvidence,
    User,
)
from db.session import get_db
from main import app
from services import code_execution_service, plagiarism_guard
from services.code_execution_service import CodeResult


async def _seed_user(db: AsyncSession, role_name: str = "candidate") -> User:
    role = (await db.execute(select(Role).where(Role.name == role_name))).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name=role_name, description=f"{role_name} role")
        db.add(role)
        await db.flush()

    user = User(
        id=uuid.uuid4(),
        email=f"{role_name}_{uuid.uuid4().hex[:8]}@vireoniq.com",
        password_hash="!unusable-test-account",
        role_id=role.id,
        is_active=True,
        is_email_verified=True,
    )
    db.add(user)
    await db.commit()
    loaded = (
        await db.execute(
            select(User).options(selectinload(User.role)).where(User.id == user.id)
        )
    ).scalar_one()
    return loaded


def _auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(user.id, str(uuid.uuid4()))
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_auth_me_logout_and_role_dependencies(db_session: AsyncSession):
    candidate = await _seed_user(db_session, "candidate")
    recruiter = await _seed_user(db_session, "Recruiter")

    assert user_has_role(candidate, ["CANDIDATE"]) is True
    assert user_has_role(candidate, ["admin", "recruiter"]) is False

    recruiter_dep = require_roles(["recruiter", "admin"])
    assert await recruiter_dep(current_user=recruiter) == recruiter
    with pytest.raises(HTTPException) as exc_info:
        await recruiter_dep(current_user=candidate)
    assert exc_info.value.status_code == 403

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Missing token -> 401
            assert (await ac.get("/api/v1/auth/me")).status_code == 401

            # Refresh token passed as Bearer access token -> rejected with 401
            refresh_tok = create_refresh_token(candidate.id, str(uuid.uuid4()))
            assert (
                await ac.get(
                    "/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {refresh_tok}"},
                )
            ).status_code == 401

            # Valid access token -> /auth/me succeeds and /auth/logout succeeds
            headers = _auth_headers(candidate)
            me_res = await ac.get("/api/v1/auth/me", headers=headers)
            assert me_res.status_code == 200
            assert me_res.json()["email"] == candidate.email

            logout_res = await ac.post("/api/v1/auth/logout", headers=headers)
            assert logout_res.status_code == 200
            assert logout_res.json()["message"] == "Successfully logged out"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_payment_order_and_hmac_verification_lifecycle(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
):
    candidate = await _seed_user(db_session, "candidate")
    headers = _auth_headers(candidate)
    monkeypatch.setattr(settings, "RAZORPAY_KEY_SECRET", "unit-test-razorpay-secret")

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            bad_plan = await ac.post("/api/v1/payments/order?plan_id=nonexistent", headers=headers)
            assert bad_plan.status_code == 400

            order_res = await ac.post("/api/v1/payments/order?plan_id=growth", headers=headers)
            assert order_res.status_code == 200
            order_data = order_res.json()
            assert order_data["amount"] == 29900
            order_id = order_data["order_id"]

            # Wrong HMAC signature must be rejected
            bad_sig_res = await ac.post(
                "/api/v1/payments/verify",
                params={
                    "order_id": order_id,
                    "payment_id": "pay_test_001",
                    "signature": "0" * 64,
                    "plan_id": "growth",
                },
                headers=headers,
            )
            assert bad_sig_res.status_code == 400

            # Valid HMAC signature completes upgrade cleanly
            payment_id = "pay_test_001"
            sig = hmac.new(
                b"unit-test-razorpay-secret",
                f"{order_id}|{payment_id}".encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            ok_res = await ac.post(
                "/api/v1/payments/verify",
                params={
                    "order_id": order_id,
                    "payment_id": payment_id,
                    "signature": sig,
                    "plan_id": "growth",
                },
                headers=headers,
            )
            assert ok_res.status_code == 200
            assert ok_res.json() == {"status": "success", "plan": "growth"}

            # Replay of already verified transaction returns 409 Conflict
            replay_res = await ac.post(
                "/api/v1/payments/verify",
                params={
                    "order_id": order_id,
                    "payment_id": payment_id,
                    "signature": sig,
                    "plan_id": "growth",
                },
                headers=headers,
            )
            assert replay_res.status_code == 409
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_privacy_preferences_export_fairness_and_delete(db_session: AsyncSession):
    candidate = await _seed_user(db_session, "candidate")
    headers = _auth_headers(candidate)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            pref_res = await ac.get("/api/v1/privacy-security/preferences", headers=headers)
            assert pref_res.status_code == 200
            assert pref_res.json()["user_id"] == str(candidate.id)

            upd_res = await ac.put(
                "/api/v1/privacy-security/preferences",
                json={"updates": {"allow_recruiter_discovery": False}},
                headers=headers,
            )
            assert upd_res.status_code == 200

            fair_res = await ac.get("/api/v1/privacy-security/fairness-audit", headers=headers)
            assert fair_res.status_code == 200

            export_res = await ac.get("/api/v1/privacy-security/export", headers=headers)
            assert export_res.status_code == 200
            assert export_res.json()["export_metadata"]["user_id"] == str(candidate.id)

            del_res = await ac.post("/api/v1/privacy-security/account/delete", headers=headers)
            assert del_res.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_phase4_db_backed_analytics_gamification_observability_and_telemetry(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
):
    candidate = await _seed_user(db_session, "candidate")
    other_user = await _seed_user(db_session, "candidate")
    headers = _auth_headers(candidate)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. Empty states return 0 / empty rather than hardcoded fake fixtures
            obs_empty = await ac.get("/api/v1/ai-observability/metrics", headers=headers)
            assert obs_empty.status_code == 200
            assert obs_empty.json()["data_status"] == "empty"
            assert obs_empty.json()["total_requests"] == 0

            twin_ev = await ac.get("/api/v1/career-twin/evidence", headers=headers)
            assert twin_ev.status_code == 200
            assert twin_ev.json()["total_evidence_items"] == 0
            assert twin_ev.json()["evidence_items"] == []

            ov_empty = await ac.get("/api/v1/analytics/overview", headers=headers)
            assert ov_empty.status_code == 200
            assert ov_empty.json()["ats_score"] == 0.0
            assert ov_empty.json()["applications"] == {"total": 0, "active": 0, "offers": 0}
            assert ov_empty.json()["dna_archetype"] == "Unassessed"

            prog_empty = await ac.get("/api/v1/outcomes/candidate/progress", headers=headers)
            assert prog_empty.status_code == 200
            assert prog_empty.json()["current_readiness"] == 0.0

            # 2. Populate real DB records and verify queries reflect them
            resume = Resume(
                id=uuid.uuid4(),
                user_id=candidate.id,
                storage_key=f"resumes/{uuid.uuid4().hex}.pdf",
                mime_type="application/pdf",
            )
            db_session.add(resume)
            await db_session.flush()
            db_session.add(
                ResumeScore(
                    id=uuid.uuid4(),
                    resume_id=resume.id,
                    overall_score=91.5,
                )
            )
            db_session.add(
                Application(
                    id=str(uuid.uuid4()),
                    user_id=candidate.id,
                    status="offer",
                )
            )
            db_session.add(
                CognitiveProfile(
                    id=uuid.uuid4(),
                    user_id=candidate.id,
                    dominant_archetype="Architect",
                )
            )
            db_session.add(
                SkillEvidence(
                    id=uuid.uuid4(),
                    user_id=candidate.id,
                    skill_name="Python",
                    source_type="INTERVIEW",
                    evidence_tier="VERIFIED",
                    score=88.0,
                )
            )
            db_session.add(
                CareerReadinessScore(
                    id=uuid.uuid4(),
                    user_id=candidate.id,
                    target_role="Backend Engineer",
                    overall_readiness=84.5,
                )
            )
            await db_session.commit()

            ov_pop = await ac.get("/api/v1/analytics/overview", headers=headers)
            assert ov_pop.status_code == 200
            assert ov_pop.json()["ats_score"] == 91.5
            assert ov_pop.json()["applications"] == {"total": 1, "active": 0, "offers": 1}
            assert ov_pop.json()["dna_archetype"] == "Architect"

            prog_pop = await ac.get(
                "/api/v1/outcomes/candidate/progress?target_role=Backend+Engineer",
                headers=headers,
            )
            assert prog_pop.status_code == 200
            assert prog_pop.json()["current_readiness"] == 84.5

            # 3. Gamification profile & XP awarding without UUID/arg mismatch
            gam_empty = await ac.get("/api/v1/gamification/profile", headers=headers)
            assert gam_empty.status_code == 200
            assert gam_empty.json()["total_xp"] == 0
            assert gam_empty.json()["rank_global"] == 1

            xp_res = await ac.post(
                "/api/v1/gamification/award-xp",
                json={"event": "session_completed"},
                headers=headers,
            )
            assert xp_res.status_code == 200
            assert xp_res.json()["xp_awarded"] == 50
            assert xp_res.json()["new_total"] == 50

            lb_res = await ac.get("/api/v1/gamification/leaderboard", headers=headers)
            assert lb_res.status_code == 200
            assert lb_res.json()["rankings"][0]["total_xp"] == 50

            # 4. CareerOS automation preferences DB persistence
            pref_res = await ac.get("/api/v1/career-os/preferences", headers=headers)
            assert pref_res.status_code == 200
            assert pref_res.json()["autonomy_level"] == 3
            assert pref_res.json()["kill_switch_active"] is False

            # 5. Cognitive load summary telemetry endpoint (Phase 4 signature fix)
            cog_res = await ac.post(
                "/api/v1/interview/cognitive-load",
                json={
                    "session_id": str(uuid.uuid4()),
                    "question_number": 1,
                    "backspace_rate": 0.2,
                    "average_delay_ms": 1400.0,
                    "long_pauses_count": 2,
                    "word_count": 25,
                },
                headers=headers,
            )
            assert cog_res.status_code == 200
            assert 0.0 <= cog_res.json()["load_score"] <= 1.0

            # 6. Advanced modes: adversarial session ownership + code execution review
            adv_start = await ac.post(
                "/api/v1/advanced/adversarial/start",
                json={"role_profile": "Backend Engineer", "difficulty": 7},
                headers=headers,
            )
            assert adv_start.status_code == 200
            adv_sid = adv_start.json()["session_id"]

            # Bad UUID -> 400; another user's session -> 404
            bad_uuid = await ac.get("/api/v1/advanced/reverse-interview/not-a-uuid/scorecard", headers=headers)
            assert bad_uuid.status_code == 400
            idor = await ac.get(
                f"/api/v1/advanced/reverse-interview/{adv_sid}/scorecard",
                headers=_auth_headers(other_user),
            )
            assert idor.status_code == 404

            async def _fake_submit(**kwargs):
                return CodeResult(
                    stdout="42\n",
                    stderr=None,
                    compile_output=None,
                    time_ms=12.0,
                    memory_kb=1024.0,
                    status_id=3,
                    status_desc="Accepted",
                    passed=True,
                    test_results=[{"case": 1, "expected": "42", "actual": "42", "passed": True}],
                    integrity_signals={},
                )

            monkeypatch.setattr(code_execution_service, "submit_code_for_execution", _fake_submit)
            exec_res = await ac.post(
                "/api/v1/advanced/code/execute",
                json={"source_code": "def solve(n):\n    return n * 2\n", "language": "python"},
                headers=headers,
            )
            assert exec_res.status_code == 200
            exec_body = exec_res.json()
            assert exec_body["passed"] is True
            assert exec_body["ai_review"]["code_quality_score"] >= 70.0
            assert "O(" in exec_body["ai_review"]["time_complexity"]
    finally:
        app.dependency_overrides.clear()


def test_websocket_matchmaker_and_adversarial_auth_enforcement():
    matchmaker.manager.active_connections.clear()
    matchmaker.manager.waiting_queue.clear()

    user_1 = uuid.uuid4()
    user_2 = uuid.uuid4()
    tok_1 = create_access_token(user_1, str(uuid.uuid4()))
    tok_2 = create_access_token(user_2, str(uuid.uuid4()))

    try:
        with TestClient(app) as client:
            # Missing token rejected immediately with 1008
            with pytest.raises(WebSocketDisconnect) as exc_missing:
                with client.websocket_connect(f"/api/v1/ws/matchmaker/{user_1}"):
                    pass
            assert exc_missing.value.code == 1008

            # Token sub != path user_id rejected (IDOR prevention)
            with pytest.raises(WebSocketDisconnect) as exc_idor:
                with client.websocket_connect(f"/api/v1/ws/matchmaker/{user_2}?token={tok_1}"):
                    pass
            assert exc_idor.value.code == 1008

            # Adversarial stream rejects unauthenticated / invalid token with 1008
            with pytest.raises(WebSocketDisconnect) as exc_adv:
                with client.websocket_connect(
                    f"/api/v1/advanced/adversarial/{uuid.uuid4()}/stream?token=invalid-jwt"
                ):
                    pass
            assert exc_adv.value.code == 1008

            # Two authenticated peers connect and get matched into the same room
            with client.websocket_connect(f"/api/v1/ws/matchmaker/{user_1}?token={tok_1}") as ws1:
                ws1.send_json({"type": "find_match"})
                queued = ws1.receive_json()
                assert queued == {"type": "waiting_in_queue"}

                with client.websocket_connect(f"/api/v1/ws/matchmaker/{user_2}?token={tok_2}") as ws2:
                    ws2.send_json({"type": "find_match"})
                    msg2 = ws2.receive_json()
                    msg1 = ws1.receive_json()

                    assert msg1["type"] == "match_found"
                    assert msg2["type"] == "match_found"
                    assert msg1["room_id"] == msg2["room_id"]
                    assert msg1["partner_id"] == str(user_2)
                    assert msg2["partner_id"] == str(user_1)
                    assert {msg1["role"], msg2["role"]} == {"candidate", "interviewer"}
    finally:
        matchmaker.manager.active_connections.clear()
        matchmaker.manager.waiting_queue.clear()


@pytest.mark.asyncio
async def test_plagiarism_guard_fallback_detection():
    empty_res = await plagiarism_guard.check_plagiarism("   ")
    assert empty_res.detected is False
    assert empty_res.similarity_score == 0.0

    with patch.object(plagiarism_guard, "get_embedding_model", return_value=None):
        textbook = (
            "Caching is the process of storing data in a temporary storage area "
            "to serve future requests faster."
        )
        res = await plagiarism_guard.check_plagiarism(textbook)
        assert res.detected is True
        assert res.similarity_score >= 0.72
        assert res.matched_pattern == "sys_caching"
        assert res.coaching_note
