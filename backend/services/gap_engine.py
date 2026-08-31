import json
import logging
from typing import Dict, Any, List, Tuple
from db.models import TargetRole
from core.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

def _calculate_severity(score: float) -> str:
    if score >= 80: return "None"
    if score >= 60: return "Minor"
    if score >= 40: return "Moderate"
    return "Critical"

GAP_ANALYSIS_SYSTEM_PROMPT = """
You are a Principal Technical Recruiter and Career Coach.
Analyze the candidate's parsed resume against their target role and company type.
You must perform a 5-Dimensional Gap Analysis and generate actionable 30/60/90-day recommendations.

CANDIDATE RESUME SUMMARY:
{resume_data}

TARGET ROLE: {target_role}
TARGET COMPANY TYPE: {company_type}
REQUIRED SKILLS FOR ROLE: {required_skills}
MINIMUM PROJECTS EXPECTED: {min_projects}
MINIMUM EXPERIENCE EXPECTED (Years): {min_experience}

OUTPUT FORMAT:
You MUST return ONLY a valid JSON object. No markdown block, no preamble. Follow this exact schema:
{{
  "technical_gap_score": float (0-100),
  "communication_gap_score": float (0-100, estimate from resume clarity and structure),
  "project_gap_score": float (0-100),
  "confidence_gap_score": float (0-100, estimate from action verbs and quantifiable achievements),
  "consistency_gap_score": float (0-100, estimate from career trajectory or education consistency),
  "overall_readiness_score": float (0-100),
  "missing_skills": ["skill1", "skill2"],
  "placement_probability": float (0-100),
  "recommendations": [
    {{
      "time_horizon_days": int (30, 60, or 90),
      "dimension": "string (technical, project, communication, confidence, or consistency)",
      "task_description": "string (Specific actionable task, e.g., 'Build a Redis clone in Go')",
      "resources": ["url1", "url2"]
    }}
  ]
}}
"""

from fastapi import HTTPException, status
from core.security import check_prompt_injection

async def analyze_gap(parsed_resume: dict, target_role: TargetRole, company_type: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    # 1. Compress resume
    resume_summary = json.dumps({
        "skills": parsed_resume.get("skills", []),
        "experience": str(parsed_resume.get("experience", ""))[:1500],
        "projects": str(parsed_resume.get("projects", ""))[:1000],
        "education": parsed_resume.get("education", [])
    })
    
    # 2. Security Check: Prompt Injection
    inputs_to_check = [resume_summary, target_role.role_name, company_type]
    if any(check_prompt_injection(inp) for inp in inputs_to_check):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security validation failed: Potential prompt injection detected in user inputs or resume data."
        )

    llm = get_llm_provider()

    system_prompt = GAP_ANALYSIS_SYSTEM_PROMPT.format(
        resume_data=resume_summary,
        target_role=target_role.role_name,
        company_type=company_type,
        required_skills=", ".join(target_role.required_skills) if target_role.required_skills else "General software engineering skills",
        min_projects=target_role.min_projects,
        min_experience=float(target_role.min_experience_years) if target_role.min_experience_years else 0.0
    )


    try:
        result = await llm.generate_json(
            messages=[{"role": "user", "content": "Analyze the candidate's gap profile and provide the 5-dimensional scores and recommendations."}],
            system_prompt=system_prompt
        )
    except Exception as e:
        logger.error(f"LLM Gap Analysis failed: {e}. Falling back to heuristics.")
        return _fallback_analyze_gap(parsed_resume, target_role, company_type)

    tech = result.get("technical_gap_score", 50.0)
    comm = result.get("communication_gap_score", 50.0)
    proj = result.get("project_gap_score", 50.0)
    conf = result.get("confidence_gap_score", 50.0)
    cons = result.get("consistency_gap_score", 50.0)
    overall = result.get("overall_readiness_score", (tech + comm + proj + conf + cons) / 5)

    base_salary = float(target_role.salary_band_base) if target_role.salary_band_base else 50000.0
    multiplier = overall / 100.0
    if company_type.lower() == "product": multiplier *= 1.5
    elif company_type.lower() == "startup": multiplier *= 1.2
    
    expected_salary = base_salary * multiplier
    salary_band = f"${int(expected_salary * 0.9):,} - ${int(expected_salary * 1.1):,}"

    analysis_data = {
        "technical_gap_score": round(tech, 2),
        "communication_gap_score": round(comm, 2),
        "project_gap_score": round(proj, 2),
        "confidence_gap_score": round(conf, 2),
        "consistency_gap_score": round(cons, 2),
        "overall_readiness_score": round(overall, 2),
        
        "technical_gap_severity": _calculate_severity(tech),
        "communication_gap_severity": _calculate_severity(comm),
        "project_gap_severity": _calculate_severity(proj),
        "confidence_gap_severity": _calculate_severity(conf),
        "consistency_gap_severity": _calculate_severity(cons),
        
        "missing_skills": result.get("missing_skills", []),
        "placement_probability": round(result.get("placement_probability", 50.0), 2),
        "expected_salary_band": salary_band
    }

    recommendations = result.get("recommendations", [])
    
    return analysis_data, recommendations

def _fallback_analyze_gap(parsed_resume: dict, target_role: TargetRole, company_type: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    skills_text = str(parsed_resume.get("skills", "")).lower()
    required_skills = target_role.required_skills or []
    missing_skills = [skill for skill in required_skills if skill.lower() not in skills_text]
    
    match_ratio = (len(required_skills) - len(missing_skills)) / len(required_skills) if required_skills else 1.0
    technical_score = match_ratio * 100.0
    
    project_score = 60.0
    communication_score = 70.0
    confidence_score = 65.0
    consistency_score = 80.0
    
    overall_readiness = (technical_score * 0.4) + (project_score * 0.2) + (communication_score * 0.15) + (confidence_score * 0.15) + (consistency_score * 0.1)
    placement_probability = overall_readiness * 0.8
    
    analysis_data = {
        "technical_gap_score": round(technical_score, 2),
        "communication_gap_score": round(communication_score, 2),
        "project_gap_score": round(project_score, 2),
        "confidence_gap_score": round(confidence_score, 2),
        "consistency_gap_score": round(consistency_score, 2),
        "overall_readiness_score": round(overall_readiness, 2),
        
        "technical_gap_severity": _calculate_severity(technical_score),
        "communication_gap_severity": _calculate_severity(communication_score),
        "project_gap_severity": _calculate_severity(project_score),
        "confidence_gap_severity": _calculate_severity(confidence_score),
        "consistency_gap_severity": _calculate_severity(consistency_score),
        
        "missing_skills": missing_skills,
        "placement_probability": round(placement_probability, 2),
        "expected_salary_band": "$50,000 - $70,000"
    }
    
    recommendations = [
        {
            "time_horizon_days": 30,
            "dimension": "technical",
            "task_description": f"Master the missing core technologies.",
            "resources": []
        }
    ]
    return analysis_data, recommendations
