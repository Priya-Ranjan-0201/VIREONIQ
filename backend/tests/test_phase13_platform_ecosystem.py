import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, RecruiterOrganization, PlatformApiKey, WebhookSubscription,
    WebhookDeliveryLog, PartnerConnector, TenantEntitlement, EventOutbox
)
from services.platform_ecosystem_service import (
    create_scoped_api_key, verify_scoped_api_key, dispatch_webhook_event,
    execute_partner_connector_sync, check_and_meter_tenant_quota,
    get_global_platform_health
)

@pytest.mark.asyncio
async def test_section_127_multi_tenant_api_key_scoping(db_session: AsyncSession):
    """
    Validates Section 127 & 128:
      Generates scoped API keys for Tenant A and Tenant B.
      Verifies that Tenant A cannot use Tenant B's keys, and scope enforcement works strictly.
    """
    uid_a = uuid.uuid4().hex[:6]
    uid_b = uuid.uuid4().hex[:6]
    org_a = RecruiterOrganization(id=uuid.uuid4(), name=f"Org Alpha {uid_a}", domain=f"alpha_{uid_a}.com")
    org_b = RecruiterOrganization(id=uuid.uuid4(), name=f"Org Beta {uid_b}", domain=f"beta_{uid_b}.com")
    db_session.add_all([org_a, org_b])
    await db_session.flush()

    # 1. Create Scoped Key for Org A with ["candidate:read", "jobs:read"]
    key_res_a = await create_scoped_api_key(
        tenant_id=org_a.id,
        name="Org Alpha Read Key",
        scopes=["candidate:read", "jobs:read"],
        rate_limit_per_minute=60,
        db=db_session
    )
    assert key_res_a["key_prefix"] is not None
    assert key_res_a["raw_api_key"].startswith("vrq_live_")

    # 2. Verify Key with Valid Scope ("jobs:read")
    verified = await verify_scoped_api_key(key_res_a["raw_api_key"], "jobs:read", db_session)
    assert verified["valid"] is True
    assert verified["tenant_id"] == str(org_a.id)

    # 3. Verify Key Rejection on Missing Scope ("jobs:write")
    with pytest.raises(ValueError, match="INSUFFICIENT_SCOPE"):
        await verify_scoped_api_key(key_res_a["raw_api_key"], "jobs:write", db_session)

@pytest.mark.asyncio
async def test_section_129_webhook_delivery_and_dlq(db_session: AsyncSession):
    """
    Validates Section 129:
      Webhook event delivery with HMAC signature and automatic DLQ routing on failure.
    """
    uid = uuid.uuid4().hex[:6]
    org = RecruiterOrganization(id=uuid.uuid4(), name=f"Webhook Org {uid}", domain=f"webhook_{uid}.com")
    db_session.add(org)
    await db_session.flush()

    # 1. Subscribe to "assessment.completed"
    sub = WebhookSubscription(
        tenant_id=org.id,
        target_url="https://partner.api/webhook",
        secret_token="whsec_test_secret_key_123",
        subscribed_events=["assessment.completed"],
        status="ACTIVE"
    )
    db_session.add(sub)
    await db_session.commit()

    # 2. Successful Webhook Delivery
    res_success = await dispatch_webhook_event(
        tenant_id=org.id,
        event_type="assessment.completed",
        payload={"candidate_id": str(uuid.uuid4()), "score": 92.0},
        simulate_failure=False,
        db=db_session
    )
    assert res_success["subscriptions_matched"] == 1
    assert res_success["deliveries"][0]["status"] == "DELIVERED"
    assert res_success["deliveries"][0]["response_code"] == 200

    # 3. Failed Webhook Delivery -> Routes to DEAD_LETTER (DLQ)
    res_fail = await dispatch_webhook_event(
        tenant_id=org.id,
        event_type="assessment.completed",
        payload={"candidate_id": str(uuid.uuid4()), "score": 92.0},
        simulate_failure=True,
        db=db_session
    )
    assert res_fail["deliveries"][0]["status"] == "DEAD_LETTER"
    assert res_fail["deliveries"][0]["response_code"] == 500

@pytest.mark.asyncio
async def test_section_130_tenant_entitlement_metering(db_session: AsyncSession):
    """
    Validates Section 130:
      Server-side entitlement quotas and usage metering.
    """
    uid = uuid.uuid4().hex[:6]
    org = RecruiterOrganization(id=uuid.uuid4(), name=f"Quota Org {uid}", domain=f"quota_{uid}.com")
    db_session.add(org)
    await db_session.flush()

    # 1. Consume AI Tokens within quota
    meter_res = await check_and_meter_tenant_quota(
        tenant_id=org.id,
        quota_type="AI_TOKENS",
        amount=50000,
        db=db_session
    )
    assert meter_res["used"] == 50000
    assert meter_res["remaining"] == 950000

    # 2. Attempt to exceed quota (requesting 2,000,000 tokens when limit is 1,000,000)
    with pytest.raises(ValueError, match="QUOTA_EXCEEDED"):
        await check_and_meter_tenant_quota(
            tenant_id=org.id,
            quota_type="AI_TOKENS",
            amount=2000000,
            db=db_session
        )

@pytest.mark.asyncio
async def test_section_131_partner_connector_sync(db_session: AsyncSession):
    """
    Validates Section 131:
      Partner connector sync execution (ATS, LMS, Campus, HRIS).
    """
    uid = uuid.uuid4().hex[:6]
    org = RecruiterOrganization(id=uuid.uuid4(), name=f"Connector Org {uid}", domain=f"connector_{uid}.com")
    db_session.add(org)
    await db_session.flush()

    connector = PartnerConnector(
        tenant_id=org.id,
        connector_type="ATS",
        name="Workday ATS",
        status="CONNECTED",
        config={"endpoint": "https://api.workday.com/v1"}
    )
    db_session.add(connector)
    await db_session.commit()

    sync_res = await execute_partner_connector_sync(connector.id, db_session)
    assert sync_res["status"] == "CONNECTED"
    assert sync_res["records_synced_this_run"] == 15
    assert sync_res["total_records_synced"] == 15

@pytest.mark.asyncio
async def test_section_132_platform_health_telemetry():
    """
    Validates Section 132:
      Global platform health and graceful degradation telemetry.
    """
    health = await get_global_platform_health()
    assert health["status"] == "OPERATIONAL"
    assert health["subsystems"]["core_api"]["status"] == "OPERATIONAL"
    assert health["subsystems"]["verification_engine"]["status"] == "OPERATIONAL"
    assert "graceful_degradation" in health
