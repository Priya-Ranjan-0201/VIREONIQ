"""
Three-Valued Evidence Ontology & Requirement Verification.

Enforces:
1. Three-valued states: SUPPORTED, CONTRADICTED, UNKNOWN.
2. Missing evidence is explicitly classified as UNKNOWN (never scored as negative).
3. Verbatim span attribution for supported/contradicted requirements.
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class EvidenceState(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"


class RequirementEvaluation:
    """
    Evaluates individual role requirements against extracted candidate evidence.
    """

    @staticmethod
    def evaluate_requirement(
        requirement: str,
        document_text: str,
        known_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Classifies whether a requirement is SUPPORTED, CONTRADICTED, or UNKNOWN.
        """
        req_lower = requirement.lower()
        doc_lower = document_text.lower()
        known = [s.lower() for s in (known_skills or [])]

        # 1. Contradicted check (negation markers must be evaluated first)
        negation_markers = [
            f"no {req_lower}",
            f"not familiar with {req_lower}",
            f"without {req_lower}",
            f"lack {req_lower}",
            f"lacking {req_lower}",
        ]
        for neg in negation_markers:
            if neg in doc_lower:
                return {
                    "requirement": requirement,
                    "state": EvidenceState.CONTRADICTED.value,
                    "confidence": 0.85,
                    "cited_span": neg,
                    "is_negative": True,
                }

        # 2. Supported check (direct mention or skill match without negation)
        if req_lower in doc_lower or any(req_lower in s for s in known):
            start_idx = doc_lower.find(req_lower)
            span = ""
            if start_idx != -1:
                span = document_text[max(0, start_idx - 20) : min(len(document_text), start_idx + len(requirement) + 20)]
            else:
                span = f"Matched in verified skills: {requirement}"

            return {
                "requirement": requirement,
                "state": EvidenceState.SUPPORTED.value,
                "confidence": 0.90,
                "cited_span": span.strip(),
                "is_negative": False,
            }

        # 3. Missing evidence is explicitly UNKNOWN (non-negative)
        return {
            "requirement": requirement,
            "state": EvidenceState.UNKNOWN.value,
            "confidence": 0.0,
            "cited_span": None,
            "is_negative": False,
            "action_needed": "Request candidate clarification",
        }
