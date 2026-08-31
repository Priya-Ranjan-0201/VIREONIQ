import pytest
from services.role_intelligence_service import get_role_definition, get_all_roles, STANDARD_ROLES

def test_standard_roles_completeness():
    roles = get_all_roles()
    assert len(roles) >= 9
    
    role_names = [r["role_name"] for r in roles]
    assert "Backend Engineer" in role_names
    assert "Full Stack Engineer" in role_names
    assert "Frontend Engineer" in role_names
    assert "AI/ML Engineer" in role_names
    assert "Data Engineer" in role_names
    assert "DevOps Engineer" in role_names
    assert "Cloud Engineer" in role_names
    assert "Cybersecurity Engineer" in role_names
    assert "Product Manager" in role_names

def test_role_competency_structure():
    backend_role = get_role_definition("Backend Engineer")
    assert backend_role["role_code"] == "BACKEND_ENG"
    assert len(backend_role["required_skills"]) >= 5
    
    req_names = [s["name"] for s in backend_role["required_skills"]]
    assert "Python" in req_names
    assert "PostgreSQL" in req_names
    assert "System Design" in req_names

def test_custom_role_fallback():
    custom_role = get_role_definition("Blockchain Quantum Architect")
    assert custom_role["role_code"] == "CUSTOM_ROLE"
    assert len(custom_role["required_skills"]) >= 2
