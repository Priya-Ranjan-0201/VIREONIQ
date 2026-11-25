from eval.model_gate import ModelGateAuditor
from services.rag_coach import RAGCareerCoach


def test_rag_career_coach_answers_with_citations():
    coach = RAGCareerCoach(abstention_threshold=0.40)
    chunks = [
        {
            "id": "exp_chunk_1",
            "source_title": "Distributed Systems",
            "text": "Built high-throughput Kafka event streaming pipeline handling 10k eps.",
            "relevance": 0.88,
        },
        {
            "id": "exp_chunk_2",
            "source_title": "Database Optimization",
            "text": "Optimized PostgreSQL indexes reducing query p95 from 2s to 80ms.",
            "relevance": 0.72,
        },
    ]

    result = coach.answer_career_inquiry(
        query="How can I prepare for Senior Backend role?",
        retrieved_evidence_chunks=chunks,
        candidate_profile_text="Candidate resume text summary",
    )

    assert result["status"] == "ANSWERED"
    assert result["confidence"] == 0.88
    assert len(result["citations"]) == 2
    assert result["citations"][0]["chunk_id"] == "exp_chunk_1"
    assert result["fenced_context_length"] > 0


def test_rag_career_coach_abstains_on_weak_evidence():
    coach = RAGCareerCoach(abstention_threshold=0.50)

    # Low relevance chunks below threshold
    weak_chunks = [
        {
            "id": "weak_1",
            "source_title": "Hobby Project",
            "text": "Made a basic calculator in HTML",
            "relevance": 0.20,
        }
    ]

    result = coach.answer_career_inquiry(
        query="What cloud architecture patterns should I design?",
        retrieved_evidence_chunks=weak_chunks,
    )

    assert result["status"] == "ABSTAIN"
    assert "below the required threshold" in result["answer"]
    assert len(result["citations"]) == 0

    # Empty chunks also abstains cleanly
    empty_result = coach.answer_career_inquiry(
        query="Anything",
        retrieved_evidence_chunks=[],
    )
    assert empty_result["status"] == "ABSTAIN"
    assert len(empty_result["citations"]) == 0


def test_model_gate_audit_approves_compliant_model():
    compliant_metrics = {
        "model_score": 0.84,
        "baseline_score": 0.65,
        "entity_overlap_count": 0,
        "temporal_leakage": False,
        "repeatability_variance": 0.0002,
        "demographic_disparity": 0.02,
        "max_formatting_delta": 0.01,
        "ece": 0.08,
        "p95_latency_ms": 120.0,
        "latency_budget_ms": 200.0,
    }

    result = ModelGateAuditor.audit_model("career_readiness_v2", compliant_metrics)
    assert result.overall_passed is True
    assert len(result.criteria) == 8
    assert all(c.passed for c in result.criteria)


def test_model_gate_audit_rejects_non_compliant_model():
    non_compliant_metrics = {
        "model_score": 0.55,
        "baseline_score": 0.60,      # Fails 1: Baseline beat
        "entity_overlap_count": 12,    # Fails 2: Entity leakage
        "temporal_leakage": True,      # Fails 3: Temporal leakage
        "repeatability_variance": 0.05, # Fails 4: High variance
        "demographic_disparity": 0.18, # Fails 5: Unfair disparity
        "max_formatting_delta": 0.12,  # Fails 6: Formatting sensitive
        "ece": 0.32,                   # Fails 7: Poorly calibrated
        "p95_latency_ms": 450.0,       # Fails 8: Latency exceeded
        "latency_budget_ms": 200.0,
    }

    result = ModelGateAuditor.audit_model("uncalibrated_experimental_model", non_compliant_metrics)
    assert result.overall_passed is False
    # All 8 should have failed
    failed_criteria = [c for c in result.criteria if not c.passed]
    assert len(failed_criteria) == 8
