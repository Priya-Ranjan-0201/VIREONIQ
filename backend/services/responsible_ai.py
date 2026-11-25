"""
Responsible AI, Dual Audit & Autonomy Guard Engine.

Implements:
1. Dual Validation: Audits competence discernment alongside demographic parity
   to prevent the 'Illusion of Neutrality' (F3: arXiv:2507.11548).
2. Autonomous Agency Guards: Enforces Level 3 Human-in-the-Loop constraints
   blocking high-impact actions without explicit candidate confirmation.
3. Reviewer Oversight Telemetry: Measures reviewer override rates and human-AI agreement.
"""

from typing import Any, Dict, List, Optional, Set


# High-impact actions that mandate explicit user confirmation
HIGH_IMPACT_ACTIONS: Set[str] = {
    "APPLY_JOB",
    "MESSAGE_RECRUITER",
    "PUBLISH_CREDENTIAL",
    "CHANGE_GOAL",
    "DELETE_DATA",
}


class AutonomyGuardError(PermissionError):
    """Raised when an autonomous agent attempts a high-impact action without human confirmation."""
    pass


class ResponsibleAIEngine:
    """
    Evaluates algorithmic fairness, competence discernment, and agency boundaries.
    """

    @staticmethod
    def audit_competence_and_fairness(
        qualified_scores: List[float],
        unqualified_control_scores: List[float],
        group_a_scores: List[float],
        group_b_scores: List[float],
        pass_threshold: float = 70.0,
    ) -> Dict[str, Any]:
        """
        Runs Dual Validation:
        1. Discernment: Qualified candidates must score significantly higher than unqualified controls.
        2. Fairness: Adverse Impact Ratio (AIR) between demographic groups must satisfy four-fifths rule (> 0.80).
        3. Illusion of Neutrality Check: Flags models that appear neutral only because discernment is near zero.
        """
        mean_qual = sum(qualified_scores) / len(qualified_scores) if qualified_scores else 0.0
        mean_unqual = sum(unqualified_control_scores) / len(unqualified_control_scores) if unqualified_control_scores else 0.0

        discernment_delta = mean_qual - mean_unqual
        has_competence = discernment_delta >= 15.0  # At least 15 points separation

        # Selection rates
        rate_a = sum(1 for s in group_a_scores if s >= pass_threshold) / len(group_a_scores) if group_a_scores else 0.0
        rate_b = sum(1 for s in group_b_scores if s >= pass_threshold) / len(group_b_scores) if group_b_scores else 0.0

        higher_rate = max(rate_a, rate_b)
        lower_rate = min(rate_a, rate_b)
        air = (lower_rate / higher_rate) if higher_rate > 0.0 else 1.0

        # Illusion of neutrality occurs when parity is high (AIR >= 0.8) but discernment is absent
        illusion_of_neutrality = (air >= 0.80) and (not has_competence)

        return {
            "mean_qualified": round(mean_qual, 2),
            "mean_unqualified": round(mean_unqual, 2),
            "discernment_delta": round(discernment_delta, 2),
            "competence_discernment_passed": has_competence,
            "group_a_selection_rate": round(rate_a, 4),
            "group_b_selection_rate": round(rate_b, 4),
            "adverse_impact_ratio": round(air, 4),
            "four_fifths_rule_passed": air >= 0.80,
            "illusion_of_neutrality_flagged": illusion_of_neutrality,
            "overall_audit_passed": has_competence and (air >= 0.80) and (not illusion_of_neutrality),
        }

    @staticmethod
    def enforce_agency_guard(
        action_name: str,
        user_confirmed: bool = False,
        confirmation_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Guards high-impact actions. Requires user confirmation before execution.
        """
        norm_action = action_name.upper().strip()

        if norm_action in HIGH_IMPACT_ACTIONS:
            if not user_confirmed and not confirmation_token:
                raise AutonomyGuardError(
                    f"Action '{norm_action}' is a high-impact operation requiring explicit "
                    f"user confirmation. Execution blocked by Autonomy Guard."
                )

        return {
            "action": norm_action,
            "status": "APPROVED",
            "is_high_impact": norm_action in HIGH_IMPACT_ACTIONS,
            "confirmed_by_user": user_confirmed or bool(confirmation_token),
        }

    @staticmethod
    def compute_reviewer_telemetry(
        reviewer_decisions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Computes substantive human review metrics: override rate, human-AI agreement rate.
        """
        if not reviewer_decisions:
            return {"total_reviews": 0, "override_rate": 0.0, "agreement_rate": 1.0}

        total = len(reviewer_decisions)
        overrides = sum(1 for d in reviewer_decisions if d.get("overridden", False))
        agreements = total - overrides

        return {
            "total_reviews": total,
            "override_count": overrides,
            "agreement_count": agreements,
            "override_rate": round(overrides / total, 4),
            "agreement_rate": round(agreements / total, 4),
        }
