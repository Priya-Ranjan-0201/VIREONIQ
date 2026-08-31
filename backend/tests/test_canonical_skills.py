import pytest
from services.canonical_skill_service import (
    normalize_skill_name, derive_proficiency_level, get_skill_relationships
)

def test_skill_name_normalization():
    assert normalize_skill_name("python3") == "Python"
    assert normalize_skill_name("python 3") == "Python"
    assert normalize_skill_name("py") == "Python"
    assert normalize_skill_name("fastapi framework") == "FastAPI"
    assert normalize_skill_name("postgres") == "PostgreSQL"
    assert normalize_skill_name("k8s") == "Kubernetes"
    assert normalize_skill_name("react.js") == "React"

def test_evidence_derived_proficiency_levels():
    # Claimed -> Familiar (1)
    lvl, desc = derive_proficiency_level("CLAIMED", 0.0)
    assert lvl == 1
    assert "Familiar" in desc

    # Inferred -> Beginner (2)
    lvl, desc = derive_proficiency_level("INFERRED", 50.0)
    assert lvl == 2
    assert "Beginner" in desc

    # Demonstrated -> Intermediate (3) with high score
    lvl, desc = derive_proficiency_level("DEMONSTRATED", 85.0)
    assert lvl == 3
    assert "Intermediate" in desc

    # Assessed -> Advanced (4) with 90+ score
    lvl, desc = derive_proficiency_level("ASSESSED", 94.0)
    assert lvl == 4
    assert "Advanced" in desc

    # Verified -> Expert (5) with high score and multi-source evidence
    lvl, desc = derive_proficiency_level("VERIFIED", 96.0, evidence_count=4)
    assert lvl == 5
    assert "Expert" in desc

def test_skill_relationships():
    fastapi_rels = get_skill_relationships("FastAPI")
    assert len(fastapi_rels) >= 1
    srcs = [r.get("source_skill") for r in fastapi_rels if "source_skill" in r]
    assert "Python" in srcs
