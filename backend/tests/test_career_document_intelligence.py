"""
Tests for VIREONIQ Career Document Intelligence & Developer Profile Signals.
Evaluates:
  - Comprehensive ATS Compatibility Scoring
  - Multi-Factor JD Semantic & Lexical Matching
  - Section-by-Section STAR Action Verb Rewriting
  - Work History Trajectory Anomaly Detection
  - Knowledge Graph PageRank Implicit Skill Inference
  - Regional Purchasing-Power-Parity Salary Prediction
  - Curated Learning Intervention Resources
  - Multi-Platform Developer Signals (GitHub, LeetCode, LinkedIn)
"""

import pytest
import uuid
from services.resume_scorer import compute_ats_compatibility_score
from services.role_comparison_service import match_job_description
from services.resume_builder_service import rewrite_resume_section
from services.evidence_graph_service import analyze_developer_profiles, detect_work_history_anomalies
from services.canonical_skill_service import infer_implicit_skills_from_graph
from services.market_intelligence import predict_salary_range
from services.career_intervention_engine import get_curated_intervention_resources


def test_ats_scoring_comprehensive():
    sample_cv = """
    Professional Summary
    Results-driven Backend Engineer with 3+ years experience designing scalable microservices.
    
    Work Experience
    Senior Software Engineer at TechCorp (2022 - Present)
    - Architected distributed caching layer with Redis, reducing API response times by 45%.
    - Built FastAPI asynchronous REST services handling 10,000 requests per minute.
    
    Key Projects
    Distributed Telemetry Pipeline
    - Containerized with Docker and deployed on AWS ECS with automated CI/CD.
    
    Education
    B.S. in Computer Science, University of Technology, 2021
    """
    skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Redis", "Git"]
    res = compute_ats_compatibility_score(sample_cv, skills)

    assert "score" in res
    assert res["score"] >= 75
    assert "Section Completeness" in res["categories"]
    assert "Skill Keyword Density" in res["categories"]
    assert "Formatting & Readability" in res["categories"]
    assert res["categories"]["Section Completeness"] == 100
    assert len(res["recommendations"]) > 0


def test_jd_semantic_matching():
    sample_cv = "Experienced Python developer with strong background in FastAPI, PostgreSQL, Docker, and AWS microservices."
    sample_jd = """
    We are seeking a Backend Engineer skilled in Python, FastAPI, PostgreSQL, Docker, AWS, and Kubernetes.
    Experience with Redis and distributed systems is a plus.
    """
    candidate_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]

    res = match_job_description(sample_cv, sample_jd, candidate_skills)

    assert "match_percentage" in res
    assert res["match_percentage"] >= 60.0
    assert "Python" in res["matching_skills"] or "FastAPI" in res["matching_skills"]
    assert "Kubernetes" in res["missing_skills"]
    assert res["keyword_overlap_percentage"] > 0
    assert len(res["suggestions"]) > 0


def test_resume_section_rewriter():
    raw_experience = "worked on user authentication and made API endpoints for payments."
    res = rewrite_resume_section("experience", raw_experience, target_role="Backend Engineer")

    assert "suggestions" in res
    assert len(res["suggestions"]) >= 2
    first_suggestion = res["suggestions"][0].lower()
    assert "spearheaded" in first_suggestion or "engineered" in first_suggestion
    assert len(res["tips"]) >= 2


def test_work_history_anomaly_detection():
    normal = detect_work_history_anomalies(years_experience=5.0, seniority_score=3.5, title="Senior SDE")
    assert not normal["is_anomalous"]
    assert normal["risk_score"] < 40.0

    anomalous = detect_work_history_anomalies(years_experience=0.5, seniority_score=9.0, title="VP of Engineering")
    assert anomalous["is_anomalous"]
    assert anomalous["risk_score"] >= 60.0
    assert len(anomalous["flags"]) > 0


def test_graph_skill_inference_pagerank():
    explicit = ["Python", "FastAPI", "React"]
    inferred = infer_implicit_skills_from_graph(explicit, threshold=0.4)

    assert isinstance(inferred, list)
    inferred_names = [s["skill_name"] for s in inferred]
    assert any(name in ["JavaScript", "PostgreSQL", "Docker", "HTML", "CSS", "Linux"] for name in inferred_names)


def test_salary_prediction_estimation():
    res = predict_salary_range(
        role="Backend Engineer",
        experience_years=3,
        location="Bangalore",
        skills=["Python", "FastAPI", "Docker", "AWS", "PostgreSQL"]
    )

    assert "predicted_range" in res
    assert "₹" in res["currency"]
    assert "disclaimer" in res
    assert res["confidence"] == "HIGH"
    assert len(res["key_drivers"]) >= 3
    assert res["raw_bounds"]["high"] > res["raw_bounds"]["low"]


def test_curated_skill_gap_resources():
    gaps = ["Docker", "FastAPI", "PostgreSQL"]
    resources = get_curated_intervention_resources(gaps)

    assert len(resources) == 3
    for r in resources:
        assert "url" in r
        assert "title" in r
        assert "provider" in r
        assert r["url"].startswith("http")


@pytest.mark.asyncio
async def test_developer_portfolio_analysis(db_session):
    test_user_id = uuid.uuid4()
    portfolio = await analyze_developer_profiles(
        user_id=test_user_id,
        github_url="https://github.com/vireoniq-dev",
        leetcode_user="vireoniq_solver",
        linkedin_url="https://linkedin.com/in/vireoniq",
        db=db_session
    )

    assert portfolio["overall_grade"] in ("A", "B")
    assert portfolio["strength_score"] >= 50
    assert portfolio["platform_signals"]["github"]["verified"] is True
    assert portfolio["platform_signals"]["leetcode"]["verified"] is True
    assert len(portfolio["strengths"]) >= 2
    assert "Python" in portfolio["ingested_evidence_skills"]
