import pytest
from services.assessment_blueprint_service import get_blueprint_questions
from services.code_execution_service import analyze_python_ast_complexity
from services.assessment_integrity_service import evaluate_interaction_integrity

def test_hidden_tests_never_exposed_in_client_prompts():
    questions = get_blueprint_questions("Backend Engineer")
    for q in questions:
        # Prompt must never contain the hidden test answers directly
        prompt = q["prompt"]
        for ht in q.get("hidden_tests", []):
            assert ht["expected"] not in prompt or len(ht["expected"]) <= 4

def test_ast_complexity_analyzer_precision():
    # 1. Constant time
    c1 = analyze_python_ast_complexity("def get_first(lst):\n    return lst[0]\n")
    assert c1.time_complexity_static == "O(1)"

    # 2. Linear time
    c2 = analyze_python_ast_complexity("def sum_items(lst):\n    tot = 0\n    for x in lst:\n        tot += x\n    return tot\n")
    assert c2.time_complexity_static == "O(N)"

    # 3. Quadratic time
    c3 = analyze_python_ast_complexity("def bubble(lst):\n    for i in range(len(lst)):\n        for j in range(len(lst)):\n            pass\n")
    assert c3.time_complexity_static == "O(N^2)"

def test_assessment_integrity_signals():
    # 1. Rapid paste burst anomaly (> 400 chars in 1.2s)
    telemetry_burst = evaluate_interaction_integrity(
        submission_text="def complex_solution():\n" + ("    x = 1\n" * 40),
        duration_seconds=1.2,
        paste_event_count=1,
        paste_character_count=420
    )
    assert telemetry_burst["integrity_status"] in ("FLAGGED_REVIEW", "AUDIT_REQUIRED")
    assert telemetry_burst["signals_count"] >= 1
    assert any(s["signal_type"] == "RAPID_SUBMISSION_BURST" for s in telemetry_burst["signals"])

    # 2. Normal organic typing (500 chars in 75s)
    telemetry_organic = evaluate_interaction_integrity(
        submission_text="def normal_solution():\n" + ("    x = 1\n" * 40),
        duration_seconds=75.0,
        paste_event_count=0,
        paste_character_count=0
    )
    assert telemetry_organic["integrity_status"] == "VERIFIED"
    assert telemetry_organic["integrity_score"] == 100.0
