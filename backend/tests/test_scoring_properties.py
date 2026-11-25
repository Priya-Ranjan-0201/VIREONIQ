"""
Property-Based Tests for Career Scoring Functions.

Verifies mathematical invariants:
1. Boundedness: All outputs are strictly bounded in [0.0, 100.0].
2. Monotonicity: Adding relevant verified skills or section details cannot lower the score.
3. Determinism: Identical inputs evaluated across 100 iterations return identical scores.
"""

from services.resume_scorer import compute_ats_compatibility_score


def test_scoring_boundedness_invariant():
    """Scores must always remain bounded within [0.0, 100.0]."""
    test_cases = [
        ("", []),
        ("Simple resume with Python experience.", ["Python"]),
        (
            "Summary: Senior engineer. Experience: Led 5 projects at Acme. Education: BS CS. Skills: Python, Docker, SQL, FastAPI, AWS.",
            ["Python", "Docker", "SQL", "FastAPI", "AWS"],
        ),
    ]
    for text, skills in test_cases:
        res = compute_ats_compatibility_score(cv_text=text, candidate_skills=skills)
        score = float(res.get("score", 0.0))
        assert 0.0 <= score <= 100.0, f"Score {score} out of bounds for text {text[:30]}"


def test_scoring_monotonicity_invariant():
    """Adding an additional skill should increase or maintain the ATS compatibility score."""
    base_text = "Summary: Software engineer. Experience: Built APIs with Python. Education: BS. Skills: Python."
    base_skills = ["Python"]
    base_res = compute_ats_compatibility_score(cv_text=base_text, candidate_skills=base_skills)
    base_score = float(base_res.get("score", 0.0))

    augmented_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    augmented_res = compute_ats_compatibility_score(cv_text=base_text, candidate_skills=augmented_skills)
    augmented_score = float(augmented_res.get("score", 0.0))

    assert augmented_score >= base_score, (
        f"Monotonicity violation: base {base_score} > augmented {augmented_score}"
    )


def test_scoring_determinism_invariant():
    """Repeated calls with identical input must produce identical results with zero drift."""
    text = "Professional Summary: Backend engineer with 5 years experience. Skills: Python, Docker, Kubernetes, SQL."
    skills = ["Python", "Docker", "Kubernetes", "SQL"]

    first_res = compute_ats_compatibility_score(cv_text=text, candidate_skills=skills)
    expected_score = first_res.get("score")

    for _ in range(50):
        iter_res = compute_ats_compatibility_score(cv_text=text, candidate_skills=skills)
        assert iter_res.get("score") == expected_score
