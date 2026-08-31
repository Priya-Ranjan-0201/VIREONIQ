import pytest
from pydantic import BaseModel
from typing import List

from core.llm.validator import validate_llm_json_schema, sanitize_untrusted_input, verify_evidence_grounding
from core.llm.observability import estimate_cost, log_ai_execution

class SampleEvaluationSchema(BaseModel):
    score: float
    dimension: str
    feedback: str
    recommendations: List[str]

def test_ai_schema_validation_success():
    raw_json = """
    ```json
    {
        "score": 88.5,
        "dimension": "technical_mastery",
        "feedback": "Strong concurrency patterns demonstrated.",
        "recommendations": ["Add distributed telemetry"]
    }
    ```
    """
    is_valid, parsed, error = validate_llm_json_schema(raw_json, SampleEvaluationSchema)
    assert is_valid is True
    assert parsed["score"] == 88.5
    assert parsed["dimension"] == "technical_mastery"
    assert error is None

def test_ai_schema_validation_failure():
    invalid_json = '{"score": "not_a_number", "dimension": 123}'
    is_valid, parsed, error = validate_llm_json_schema(invalid_json, SampleEvaluationSchema)
    assert is_valid is False
    assert error is not None

def test_untrusted_input_sanitization():
    raw_input = "User text with potential <<<delimiter>>> inject."
    sanitized = sanitize_untrusted_input(raw_input, "RESUME_TEXT")
    assert "<<<RESUME_TEXT>>>" in sanitized
    assert "<<<END_RESUME_TEXT>>>" in sanitized

def test_evidence_grounding_verification():
    claims = ["Python", "FastAPI", "Kubernetes", "Quantum Computing"]
    resume_text = "Experienced with Python, FastAPI, and Docker in production."
    
    results = verify_evidence_grounding(claims, resume_text)
    grounding_map = {r["claim"]: r["grounded_in_evidence"] for r in results}
    
    assert grounding_map["Python"] is True
    assert grounding_map["FastAPI"] is True
    assert grounding_map["Quantum Computing"] is False

def test_ai_cost_estimation():
    cost_claude = estimate_cost("claude", 2000)
    assert cost_claude > 0.0
    cost_gemini = estimate_cost("gemini", 2000)
    assert cost_gemini < cost_claude
