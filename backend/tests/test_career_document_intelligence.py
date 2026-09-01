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
from services.resume_builder_service import rewrite_resume_section, _heuristic_parse_resume, _rule_based_mnc_optimizer
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


def test_resume_parser_factual_fidelity():
    raw_cv = """
    John Doe
    john.doe@example.com
    +1 555-123-4567

    Professional Summary
    Junior Web Developer with passion for clean code.

    Experience
    Junior Developer at SmallBiz (2023 - 2024)
    - Built responsive landing pages using HTML, CSS, and vanilla JavaScript.
    - Fixed styling bugs across mobile devices.

    Education
    Diploma in Web Design, City College, 2023

    Skills
    HTML, CSS, JavaScript, Git
    """
    parsed = _heuristic_parse_resume(raw_cv, target_role="Cloud, DevOps & SRE Engineer")

    assert parsed["name"] == "John Doe"
    assert parsed["email"] == "john.doe@example.com"
    # Ensure it did NOT hallucinate Kubernetes, AWS, Terraform, or Docker
    assert "Kubernetes" not in parsed["skills"]["cloud_devops"]
    assert "AWS" not in parsed["skills"]["cloud_devops"]
    # Ensure it preserved the user's actual skills
    assert any("javascript" in s.lower() for s in parsed["skills"]["languages"])
    assert any("html" in s.lower() for s in parsed["skills"]["languages"])
    # Ensure job title was preserved from CV and not overwritten with target role
    assert parsed["experience"][0]["role"] != "Cloud, DevOps & SRE Engineer"


def test_rule_based_optimizer_no_fake_injection():
    user_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "experience": [
            {
                "company": "Local Agency",
                "role": "Frontend Intern",
                "duration": "2023",
                "location": "Remote",
                "bullets": ["wrote unit tests for signup flow"]
            }
        ],
        "skills": {
            "languages": ["Python"],
            "frameworks": [],
            "cloud_devops": [],
            "databases": [],
            "tools": []
        },
        "education": [
            {"institution": "State University", "degree": "B.A. Art", "year": "2022"}
        ],
        "projects": [],
        "certifications": []
    }

    optimized = _rule_based_mnc_optimizer(user_data, target_role="Backend Systems Engineer", target_company="Google")

    # Ensure authentic candidate details are intact
    assert optimized["name"] == "Jane Smith"
    assert optimized["email"] == "jane@example.com"
    assert optimized["education"][0]["institution"] == "State University"
    assert optimized["education"][0]["degree"] == "B.A. Art"

    # Ensure no fake Berkeley degrees, fake AWS certs, or fake projects were injected
    assert not any("Berkeley" in e.get("institution", "") for e in optimized["education"])
    assert not any("AWS Certified" in c.get("name", "") for c in optimized["certifications"])
    assert len(optimized["projects"]) == 0

