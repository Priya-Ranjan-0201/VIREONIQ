"""
Role Alignment & Comparison Service.
Provides:
  1. Candidate <-> Role Alignment with strict distinction between MATCHED, PARTIAL, GAP, and UNKNOWN (Insufficient Evidence).
  2. Multi-Role Comparison Engine (e.g. Backend Engineer vs AI/ML Engineer) computing skill overlaps, unique requirements, and readiness delta.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import SkillEvidence, User
from services.canonical_skill_service import normalize_skill_name, derive_proficiency_level
from services.role_intelligence_service import get_role_definition

logger = logging.getLogger(__name__)

async def compute_candidate_role_alignment(
    user_id: uuid.UUID,
    role_name: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Evaluates candidate evidence against role requirements.
    Classifies competencies into:
      - MATCHED (candidate proficiency >= expected proficiency)
      - PARTIAL (candidate has demonstrated baseline, but below expected level)
      - GAP (requirement exists, but candidate has low/unverified performance)
      - UNKNOWN (INSUFFICIENT EVIDENCE - never marked as a weakness)
    """
    role_def = get_role_definition(role_name)
    req_skills = role_def.get("required_skills", [])

    # Fetch candidate skills
    stmt = select(SkillEvidence).where(SkillEvidence.user_id == user_id)
    cand_skills = list((await db.execute(stmt)).scalars().all())
    cand_skill_map = {normalize_skill_name(s.skill_name): s for s in cand_skills}

    matched = []
    partial = []
    gaps = []
    unknown = []

    for req in req_skills:
        req_name = normalize_skill_name(req["name"])
        importance = req.get("importance", 80)
        expected_level = req.get("expected_proficiency", 3) # 1-5 scale

        cand_ev = cand_skill_map.get(req_name)

        if not cand_ev:
            # Crucial: If no evidence exists, mark as UNKNOWN (Insufficient Evidence), not a zero/weakness
            unknown.append({
                "skill_name": req_name,
                "importance": importance,
                "expected_level": expected_level,
                "status": "UNKNOWN",
                "reasoning": "Insufficient evidence recorded. Candidate has not yet claimed, demonstrated, or been assessed on this competency.",
                "suggested_action": f"Add project evidence or take a baseline assessment in {req_name}."
            })
            continue

        tier = cand_ev.evidence_tier
        score = float(cand_ev.score or 0.0)
        prof_level, prof_desc = derive_proficiency_level(tier, score, cand_ev.evidence_count or 1)

        comp_data = {
            "skill_name": req_name,
            "importance": importance,
            "expected_level": expected_level,
            "candidate_level": prof_level,
            "candidate_tier": tier,
            "candidate_score": score,
            "freshness": float(cand_ev.freshness_score or 100.0)
        }

        if prof_level >= expected_level:
            comp_data["status"] = "MATCHED"
            comp_data["reasoning"] = f"Proficiency ({prof_desc}) meets or exceeds role expectation (Level {expected_level})."
            matched.append(comp_data)
        elif prof_level >= max(1, expected_level - 1):
            comp_data["status"] = "PARTIAL"
            comp_data["reasoning"] = f"Proficiency ({prof_desc}) provides foundational baseline, approaching expected Level {expected_level}."
            partial.append(comp_data)
        else:
            comp_data["status"] = "GAP"
            comp_data["reasoning"] = f"Current evidence ({prof_desc}) indicates growth required to satisfy Level {expected_level} requirement."
            gaps.append(comp_data)

    total_evaluated = len(req_skills)
    matched_score = (len(matched) * 1.0 + len(partial) * 0.5) / max(total_evaluated, 1) * 100.0

    return {
        "role_name": role_def.get("role_name", role_name),
        "overall_alignment_percentage": round(matched_score, 1),
        "summary": {
            "total_requirements": total_evaluated,
            "matched_count": len(matched),
            "partial_count": len(partial),
            "gap_count": len(gaps),
            "unknown_count": len(unknown)
        },
        "matched_competencies": matched,
        "partial_competencies": partial,
        "gap_competencies": gaps,
        "unknown_competencies": unknown
    }


async def compare_roles(
    user_id: uuid.UUID,
    role_a_name: str,
    role_b_name: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Compares two career roles against candidate evidence:
    Calculates skill overlap, unique requirements, comparative alignment, and transition effort.
    """
    role_a_def = get_role_definition(role_a_name)
    role_b_def = get_role_definition(role_b_name)

    align_a = await compute_candidate_role_alignment(user_id, role_a_name, db)
    align_b = await compute_candidate_role_alignment(user_id, role_b_name, db)

    skills_a = {normalize_skill_name(s["name"]) for s in role_a_def.get("required_skills", [])}
    skills_b = {normalize_skill_name(s["name"]) for s in role_b_def.get("required_skills", [])}

    shared_skills = list(skills_a.intersection(skills_b))
    unique_to_a = list(skills_a - skills_b)
    unique_to_b = list(skills_b - skills_a)

    return {
        "role_a": {
            "name": role_a_name,
            "alignment_percentage": align_a["overall_alignment_percentage"],
            "matched_count": align_a["summary"]["matched_count"],
            "gap_count": align_a["summary"]["gap_count"],
            "unknown_count": align_a["summary"]["unknown_count"]
        },
        "role_b": {
            "name": role_b_name,
            "alignment_percentage": align_b["overall_alignment_percentage"],
            "matched_count": align_b["summary"]["matched_count"],
            "gap_count": align_b["summary"]["gap_count"],
            "unknown_count": align_b["summary"]["unknown_count"]
        },
        "comparison_metrics": {
            "shared_competencies_count": len(shared_skills),
            "shared_competencies": shared_skills,
            "unique_to_role_a": unique_to_a,
            "unique_to_role_b": unique_to_b,
            "recommended_primary_path": role_a_name if align_a["overall_alignment_percentage"] >= align_b["overall_alignment_percentage"] else role_b_name
        }
    }


def match_job_description(
    cv_text: str,
    job_description: str,
    candidate_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Computes a multi-factor Job Description (JD) match evaluating:
      1. Technical Skill Alignment (Candidate skills vs JD extracted skills)
      2. Lexical keyword overlap percentage
      3. Missing critical skills and tailoring suggestions
    """
    import re

    if not cv_text or not job_description:
        return {
            "match_percentage": 0.0,
            "matching_skills": [],
            "missing_skills": [],
            "keyword_overlap_percentage": 0,
            "suggestions": ["Please provide both resume text and job description to compute JD match."]
        }

    # Standard technical terms and architectural concepts to extract from JD
    TECH_VOCABULARY = {
        "python", "javascript", "typescript", "react", "node.js", "nodejs", "node", "java",
        "c++", "cpp", "c#", "go", "golang", "rust", "sql", "postgresql", "mysql", "mongodb",
        "redis", "docker", "kubernetes", "aws", "azure", "gcp", "fastapi", "django", "flask",
        "graphql", "rest", "grpc", "git", "ci/cd", "terraform", "pytorch", "tensorflow",
        "machine learning", "deep learning", "system design", "microservices", "linux",
        "html", "css", "tailwind", "next.js", "vue", "angular", "kafka", "rabbitmq",
        "qdrant", "vector database", "elasticsearch", "spark", "hadoop", "snowflake",
        "databricks", "llm", "langchain", "prompt engineering", "distributed systems",
        "data structures", "algorithms", "dynamodb", "serverless", "lambda", "ecs", "eks"
    }

    # Semantic proximity clusters (grants affinity credit for related tech stacks)
    SEMANTIC_CLUSTERS = {
        "fastapi": {"python", "rest", "api design", "backend development", "microservices"},
        "django": {"python", "postgresql", "orm", "backend development"},
        "react": {"javascript", "typescript", "frontend development", "html", "css"},
        "next.js": {"react", "javascript", "typescript", "frontend development"},
        "docker": {"containerization", "devops", "linux", "ci/cd", "microservices"},
        "kubernetes": {"docker", "containerization", "orchestration", "cloud computing", "devops"},
        "aws": {"cloud computing", "devops", "infrastructure", "serverless", "microservices"},
        "postgresql": {"sql", "relational database", "database design"},
        "redis": {"caching", "in-memory database", "distributed systems", "performance"},
        "kafka": {"event-driven", "messaging", "distributed systems", "streaming"},
        "pytorch": {"machine learning", "deep learning", "python", "ai"},
        "system design": {"distributed systems", "scalability", "microservices", "architecture"},
        "microservices": {"distributed systems", "system design", "rest", "backend development"},
        "distributed systems": {"microservices", "system design", "redis", "kafka"}
    }

    jd_words = set(re.findall(r"\b[a-zA-Z0-9+#.-]+\b", job_description.lower()))
    jd_extracted_skills = []

    for word in jd_words:
        if word in TECH_VOCABULARY:
            jd_extracted_skills.append(normalize_skill_name(word))

    # Also check multi-word terms
    jd_lower = job_description.lower()
    for multi_term in ["system design", "machine learning", "deep learning", "distributed systems", "vector database", "data structures"]:
        if multi_term in jd_lower:
            jd_extracted_skills.append(normalize_skill_name(multi_term))

    # Remove duplicates preserving order
    seen = set()
    jd_skills = []
    for s in jd_extracted_skills:
        if s.lower() not in seen:
            seen.add(s.lower())
            jd_skills.append(s)

    if not jd_skills:
        jd_skills = ["Software Engineering", "Problem Solving", "API Design", "System Architecture"]

    # Candidate skills & CV text
    cand_normalized = [normalize_skill_name(s) for s in (candidate_skills or []) if s]
    cand_lower = {s.lower() for s in cand_normalized}
    cv_words = set(re.findall(r"\b[a-zA-Z0-9+#.-]+\b", cv_text.lower()))
    cv_lower = cv_text.lower()

    # Build candidate semantic reach (direct skills + CV text tokens + cluster affinities)
    cand_semantic_reach = set(cand_lower).union(cv_words)
    for skill in list(cand_semantic_reach):
        if skill in SEMANTIC_CLUSTERS:
            cand_semantic_reach.update(SEMANTIC_CLUSTERS[skill])

    matched_skills = []
    semantic_affinity_skills = []
    missing_skills = []

    for skill in jd_skills:
        skill_norm = normalize_skill_name(skill)
        skill_l = skill_norm.lower()

        # Direct match in candidate skills or raw CV text
        if skill_l in cand_lower or skill_l in cv_words or skill_l in cv_lower:
            matched_skills.append(skill_norm)
        elif skill_l in cand_semantic_reach:
            # Semantic affinity match
            semantic_affinity_skills.append(skill_norm)
        else:
            missing_skills.append(skill_norm)

    total_jd_count = max(len(jd_skills), 1)
    direct_match_pct = (len(matched_skills) / total_jd_count) * 100.0
    affinity_credit_pct = (len(semantic_affinity_skills) / total_jd_count) * 60.0  # 60% partial credit for related stacks
    skill_alignment_pct = min(100.0, direct_match_pct + affinity_credit_pct)

    # Lexical overlap
    overlap = len(jd_words.intersection(cv_words))
    overlap_pct = min(100, int((overlap / max(len(jd_words), 1)) * 100))

    # Weight skill alignment 80%, keyword overlap 20%
    composite_match = round((skill_alignment_pct * 0.80) + (overlap_pct * 0.20), 1)

    suggestions = []
    if missing_skills:
        suggestions.append(f"Primary Skill Gaps: Focus on demonstrating experience with {', '.join(missing_skills[:4])}.")
    if semantic_affinity_skills:
        suggestions.append(f"Semantic Affinities Found: Your background with related stacks provides transferability to {', '.join(semantic_affinity_skills[:3])}. Explicitly highlight them in your project bullets.")
    if overlap_pct < 40:
        suggestions.append("Incorporate more industry-standard domain keywords from the target job posting.")
    else:
        suggestions.append("Strong technical vocabulary and semantic synergy with target role requirements.")

    return {
        "match_percentage": composite_match,
        "matching_skills": matched_skills,
        "semantic_affinity_skills": semantic_affinity_skills,
        "missing_skills": missing_skills,
        "keyword_overlap_percentage": overlap_pct,
        "skill_alignment_percentage": round(skill_alignment_pct, 1),
        "suggestions": suggestions
    }
