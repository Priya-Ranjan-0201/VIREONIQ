"""
Role Intelligence Service.
Defines normalized target role requirements, weighted competencies, project expectations,
and assessment standards across standard technology disciplines.
"""

from typing import Dict, Any, List, Optional

STANDARD_ROLES: Dict[str, Dict[str, Any]] = {
    "Backend Engineer": {
        "role_code": "BACKEND_ENG",
        "description": "Designs and builds robust, scalable server-side systems, distributed services, and APIs.",
        "required_skills": [
            {"name": "Python", "importance": 0.95, "min_proficiency": 75, "hard_req": True},
            {"name": "FastAPI", "importance": 0.85, "min_proficiency": 70, "hard_req": False},
            {"name": "PostgreSQL", "importance": 0.90, "min_proficiency": 70, "hard_req": True},
            {"name": "Redis", "importance": 0.80, "min_proficiency": 65, "hard_req": False},
            {"name": "System Design", "importance": 0.90, "min_proficiency": 70, "hard_req": True},
            {"name": "Data Structures", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Docker", "importance": 0.75, "min_proficiency": 60, "hard_req": False},
            {"name": "REST APIs", "importance": 0.85, "min_proficiency": 75, "hard_req": True}
        ],
        "min_projects": 2,
        "min_experience_years": 1.0,
        "salary_band_base": 85000.0
    },
    "Full Stack Engineer": {
        "role_code": "FULLSTACK_ENG",
        "description": "Architects end-to-end web applications combining responsive frontends with high-performance backends.",
        "required_skills": [
            {"name": "TypeScript", "importance": 0.90, "min_proficiency": 75, "hard_req": True},
            {"name": "React", "importance": 0.90, "min_proficiency": 75, "hard_req": True},
            {"name": "Python", "importance": 0.85, "min_proficiency": 70, "hard_req": False},
            {"name": "PostgreSQL", "importance": 0.80, "min_proficiency": 65, "hard_req": True},
            {"name": "TailwindCSS", "importance": 0.75, "min_proficiency": 70, "hard_req": False},
            {"name": "REST APIs", "importance": 0.85, "min_proficiency": 75, "hard_req": True},
            {"name": "Git", "importance": 0.80, "min_proficiency": 70, "hard_req": True}
        ],
        "min_projects": 2,
        "min_experience_years": 1.0,
        "salary_band_base": 90000.0
    },
    "Frontend Engineer": {
        "role_code": "FRONTEND_ENG",
        "description": "Creates accessible, highly responsive, performance-optimized user interfaces and client architectures.",
        "required_skills": [
            {"name": "React", "importance": 0.95, "min_proficiency": 80, "hard_req": True},
            {"name": "TypeScript", "importance": 0.95, "min_proficiency": 80, "hard_req": True},
            {"name": "JavaScript", "importance": 0.95, "min_proficiency": 80, "hard_req": True},
            {"name": "HTML/CSS", "importance": 0.90, "min_proficiency": 80, "hard_req": True},
            {"name": "TailwindCSS", "importance": 0.85, "min_proficiency": 75, "hard_req": False},
            {"name": "Web Performance", "importance": 0.80, "min_proficiency": 65, "hard_req": False}
        ],
        "min_projects": 2,
        "min_experience_years": 1.0,
        "salary_band_base": 80000.0
    },
    "AI/ML Engineer": {
        "role_code": "AIML_ENG",
        "description": "Builds and deploys machine learning models, vector retrieval pipelines, and LLM-powered systems.",
        "required_skills": [
            {"name": "Python", "importance": 0.95, "min_proficiency": 80, "hard_req": True},
            {"name": "PyTorch", "importance": 0.90, "min_proficiency": 70, "hard_req": True},
            {"name": "Transformers", "importance": 0.85, "min_proficiency": 70, "hard_req": False},
            {"name": "Vector Databases", "importance": 0.80, "min_proficiency": 65, "hard_req": False},
            {"name": "LLM Orchestration", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Data Pipelines", "importance": 0.75, "min_proficiency": 65, "hard_req": False}
        ],
        "min_projects": 2,
        "min_experience_years": 1.5,
        "salary_band_base": 105000.0
    },
    "Data Engineer": {
        "role_code": "DATA_ENG",
        "description": "Designs scalable ETL pipelines, streaming architectures, and analytical storage infrastructure.",
        "required_skills": [
            {"name": "SQL", "importance": 0.95, "min_proficiency": 85, "hard_req": True},
            {"name": "Python", "importance": 0.90, "min_proficiency": 75, "hard_req": True},
            {"name": "Apache Spark", "importance": 0.80, "min_proficiency": 65, "hard_req": False},
            {"name": "Data Warehousing", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Kafka", "importance": 0.75, "min_proficiency": 60, "hard_req": False}
        ],
        "min_projects": 2,
        "min_experience_years": 1.0,
        "salary_band_base": 95000.0
    },
    "DevOps Engineer": {
        "role_code": "DEVOPS_ENG",
        "description": "Manages automated CI/CD pipelines, container orchestration, cloud infrastructure, and site reliability.",
        "required_skills": [
            {"name": "Docker", "importance": 0.95, "min_proficiency": 80, "hard_req": True},
            {"name": "Kubernetes", "importance": 0.90, "min_proficiency": 70, "hard_req": True},
            {"name": "CI/CD", "importance": 0.90, "min_proficiency": 75, "hard_req": True},
            {"name": "Terraform", "importance": 0.80, "min_proficiency": 65, "hard_req": False},
            {"name": "Linux", "importance": 0.85, "min_proficiency": 75, "hard_req": True}
        ],
        "min_projects": 2,
        "min_experience_years": 1.5,
        "salary_band_base": 100000.0
    },
    "Cloud Engineer": {
        "role_code": "CLOUD_ENG",
        "description": "Architects secure, scalable, cost-effective infrastructure across major public cloud providers.",
        "required_skills": [
            {"name": "AWS", "importance": 0.95, "min_proficiency": 75, "hard_req": True},
            {"name": "Infrastructure as Code", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Cloud Security", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Serverless", "importance": 0.75, "min_proficiency": 65, "hard_req": False}
        ],
        "min_projects": 2,
        "min_experience_years": 1.0,
        "salary_band_base": 95000.0
    },
    "Cybersecurity Engineer": {
        "role_code": "CYBER_ENG",
        "description": "Conducts threat modeling, security architecture audits, penetration testing, and defense engineering.",
        "required_skills": [
            {"name": "Application Security", "importance": 0.95, "min_proficiency": 80, "hard_req": True},
            {"name": "Cryptography", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Threat Modeling", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Network Security", "importance": 0.80, "min_proficiency": 65, "hard_req": False}
        ],
        "min_projects": 2,
        "min_experience_years": 2.0,
        "salary_band_base": 110000.0
    },
    "Product Manager": {
        "role_code": "PRODUCT_MGR",
        "description": "Drives product strategy, technical discovery, requirement specs, roadmapping, and user outcomes.",
        "required_skills": [
            {"name": "Product Strategy", "importance": 0.95, "min_proficiency": 80, "hard_req": True},
            {"name": "Technical Architecture Literacy", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Data Analytics", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "User Research", "importance": 0.80, "min_proficiency": 75, "hard_req": False}
        ],
        "min_projects": 2,
        "min_experience_years": 1.5,
        "salary_band_base": 100000.0
    }
}

def get_role_definition(role_name: str) -> Dict[str, Any]:
    """
    Looks up a standard role definition or creates an intelligent default.
    """
    for name, details in STANDARD_ROLES.items():
        if name.lower() == role_name.lower() or name.lower() in role_name.lower():
            return details
            
    # Default custom role
    return {
        "role_code": "CUSTOM_ROLE",
        "description": f"Custom technical role: {role_name}",
        "required_skills": [
            {"name": "Core Technology", "importance": 0.90, "min_proficiency": 70, "hard_req": True},
            {"name": "System Architecture", "importance": 0.85, "min_proficiency": 70, "hard_req": True},
            {"name": "Data Structures", "importance": 0.80, "min_proficiency": 65, "hard_req": True}
        ],
        "min_projects": 2,
        "min_experience_years": 1.0,
        "salary_band_base": 80000.0
    }

def get_all_roles() -> List[Dict[str, Any]]:
    """
    Returns list of all available role definitions.
    """
    return [
        {"role_name": k, **v} for k, v in STANDARD_ROLES.items()
    ]


def analyze_skill_transferability(
    current_role: str = "Backend Engineer",
    target_role: str = "Data Engineer",
    candidate_skills: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes grounded skill transferability graph between two roles:
    Identifies shared competencies, transferable foundations, missing critical skills, and minimal learning bridge.
    """
    curr_def = get_role_definition(current_role)
    target_def = get_role_definition(target_role)

    curr_skill_map = {s["name"].lower(): s for s in curr_def.get("required_skills", [])}
    target_skills = target_def.get("required_skills", [])
    user_skills = candidate_skills or {s["name"]: 80.0 for s in curr_def.get("required_skills", [])}
    user_skill_map = {k.lower(): float(v) for k, v in user_skills.items()}

    transferable = []
    missing = []
    total_target_weight = sum(s.get("importance", 0.8) for s in target_skills) or 1.0
    transferable_weight = 0.0

    for s in target_skills:
        s_name = s["name"]
        s_lower = s_name.lower()
        w = s.get("importance", 0.8)

        # Check if candidate has direct skill or shared foundation
        if s_lower in user_skill_map and user_skill_map[s_lower] >= 60.0:
            score = user_skill_map[s_lower]
            transferable.append({
                "skill_name": s_name,
                "proficiency_score": score,
                "importance": w,
                "status": "IMMEDIATELY_TRANSFERABLE",
                "transfer_confidence": "HIGH"
            })
            transferable_weight += w
        elif s_lower in curr_skill_map:
            transferable.append({
                "skill_name": s_name,
                "proficiency_score": 70.0,
                "importance": w,
                "status": "CONCEPTUAL_OVERLAP",
                "transfer_confidence": "MEDIUM"
            })
            transferable_weight += (w * 0.7)
        else:
            missing.append({
                "skill_name": s_name,
                "min_proficiency": s.get("min_proficiency", 70),
                "importance": w,
                "hard_req": s.get("hard_req", False),
                "status": "BRIDGE_REQUIRED"
            })

    transfer_percentage = round((transferable_weight / total_target_weight) * 100.0, 1)

    if transfer_percentage >= 70.0:
        bridge_difficulty = "LOW_FRICTION"
        bridge_weeks = 3
    elif transfer_percentage >= 50.0:
        bridge_difficulty = "MODERATE"
        bridge_weeks = 6
    else:
        bridge_difficulty = "STEEP"
        bridge_weeks = 12

    why_transition = (
        f"Transitioning from {current_role} to {target_role} leverages {len(transferable)} shared competency foundations, "
        f"providing a {transfer_percentage}% immediate skill transfer index."
    )

    return {
        "current_role": current_role,
        "target_role": target_role,
        "transferability_percentage": transfer_percentage,
        "bridge_difficulty": bridge_difficulty,
        "estimated_bridge_time_weeks": bridge_weeks,
        "transferable_skills": transferable,
        "missing_critical_skills": missing,
        "explanations": {
            "why_this_transition": why_transition,
            "what_already_transfers": [f"{t['skill_name']} ({t['status']})" for t in transferable[:4]],
            "what_is_missing": [m["skill_name"] for m in missing],
            "minimal_learning_bridge": f"Focus on {len(missing)} missing competencies ({', '.join(m['skill_name'] for m in missing[:3])}) over {bridge_weeks} weeks."
        }
    }


def compute_career_transition_bridges(
    current_role: str = "Backend Engineer",
    candidate_skills: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Ranks all potential target role transitions by minimal skill bridge difficulty and transferability.
    """
    results = []
    for role_name in STANDARD_ROLES.keys():
        if role_name.lower() == current_role.lower():
            continue
        transfer_data = analyze_skill_transferability(current_role, role_name, candidate_skills)
        results.append({
            "target_role": role_name,
            "transferability_percentage": transfer_data["transferability_percentage"],
            "bridge_difficulty": transfer_data["bridge_difficulty"],
            "estimated_weeks": transfer_data["estimated_bridge_time_weeks"],
            "missing_skills_count": len(transfer_data["missing_critical_skills"]),
            "why_transition": transfer_data["explanations"]["why_this_transition"]
        })

    # Sort by highest transferability
    results.sort(key=lambda x: x["transferability_percentage"], reverse=True)
    return results
