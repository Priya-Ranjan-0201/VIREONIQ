"""
Enterprise Feature Flag and Kill-Switch Engine (Phase L1 / Staged Launch).

Provides hierarchical feature gating across launch tiers:
- Tier 1 (Public Beta): Core candidate features (Resume, ATS, Interview, Readiness)
- Tier 2 (Invite-Only): Flagged candidate features (Career Simulator, GPS, Smart Apply)
- Tier 3 (Review Gated): High-risk features (Recruiter ranking, Minor/Parent, Employer reviews)

Supports per-user, plan-based, regional, and percentage-based rollouts,
with instantaneous kill switches and audit-logged overrides.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LaunchTier(str, Enum):
    TIER_1_PUBLIC_BETA = "tier_1_public_beta"
    TIER_2_INVITE_ONLY = "tier_2_invite_only"
    TIER_3_REVIEW_GATED = "tier_3_review_gated"


@dataclass
class FeatureFlag:
    key: str
    description: str
    tier: LaunchTier
    enabled: bool = True
    kill_switch: bool = False
    rollout_percentage: int = 100
    allowed_plans: List[str] = field(default_factory=list)
    allowed_regions: List[str] = field(default_factory=list)
    allowed_user_ids: List[str] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_by: str = "system"


# Default feature flag catalog matching Part D launch recommendations
DEFAULT_FLAGS: Dict[str, FeatureFlag] = {
    # Tier 1: Public Beta (Enabled by default)
    "ats_resume_studio": FeatureFlag(
        key="ats_resume_studio",
        description="6-dimension deterministic ATS rubric scorer and builder",
        tier=LaunchTier.TIER_1_PUBLIC_BETA,
        enabled=True,
    ),
    "jd_matcher": FeatureFlag(
        key="jd_matcher",
        description="Job description keyword alignment analysis",
        tier=LaunchTier.TIER_1_PUBLIC_BETA,
        enabled=True,
    ),
    "interview_studio": FeatureFlag(
        key="interview_studio",
        description="AI interview simulation and Python AST complexity analysis",
        tier=LaunchTier.TIER_1_PUBLIC_BETA,
        enabled=True,
    ),
    "career_readiness_engine": FeatureFlag(
        key="career_readiness_engine",
        description="Multi-dimensional career readiness scoring (without outcome claims)",
        tier=LaunchTier.TIER_1_PUBLIC_BETA,
        enabled=True,
    ),
    "bullet_section_rewriter": FeatureFlag(
        key="bullet_section_rewriter",
        description="Action-verb and XYZ heuristic bullet optimization",
        tier=LaunchTier.TIER_1_PUBLIC_BETA,
        enabled=True,
    ),

    # Tier 2: Invite-Only / Beta Flagged (Controlled Rollout)
    "career_simulator": FeatureFlag(
        key="career_simulator",
        description="What-if career trajectory counterfactual simulator (Experimental)",
        tier=LaunchTier.TIER_2_INVITE_ONLY,
        enabled=True,
        rollout_percentage=100,
    ),
    "career_gps": FeatureFlag(
        key="career_gps",
        description="Step-by-step career path recommendations",
        tier=LaunchTier.TIER_2_INVITE_ONLY,
        enabled=True,
    ),
    "smart_apply_tracker": FeatureFlag(
        key="smart_apply_tracker",
        description="Application tracking and follow-up reminders",
        tier=LaunchTier.TIER_2_INVITE_ONLY,
        enabled=True,
    ),
    "talent_passport": FeatureFlag(
        key="talent_passport",
        description="HMAC-signed verifiable skill credentials",
        tier=LaunchTier.TIER_2_INVITE_ONLY,
        enabled=True,
    ),
    "gamification_system": FeatureFlag(
        key="gamification_system",
        description="XP, badges, streaks, and leaderboards",
        tier=LaunchTier.TIER_2_INVITE_ONLY,
        enabled=True,
    ),
    "paid_monetization_plans": FeatureFlag(
        key="paid_monetization_plans",
        description="Razorpay billing and subscription tiers (Gated pending Phase L10)",
        tier=LaunchTier.TIER_2_INVITE_ONLY,
        enabled=False,  # Kept disabled per Rule L10 until entitlements verified
    ),

    # Tier 3: Review Gated / Hidden (Disabled Until Counsel & Compliance Sign-Off)
    "recruiter_war_room": FeatureFlag(
        key="recruiter_war_room",
        description="Recruiter intelligence, candidate discovery and ranking (EU AI Act high risk)",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "workforce_intelligence": FeatureFlag(
        key="workforce_intelligence",
        description="Organizational capability matrix and workforce analytics",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "parent_dashboard": FeatureFlag(
        key="parent_dashboard",
        description="Minor student monitoring dashboard (Requires parental consent mechanism)",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "highschool_trajectory": FeatureFlag(
        key="highschool_trajectory",
        description="Early trajectory planning for high school minors (<18)",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "employer_truth_score": FeatureFlag(
        key="employer_truth_score",
        description="User-generated employer reviews (Requires defamation moderation)",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "community_hub": FeatureFlag(
        key="community_hub",
        description="Peer community discussion boards (Requires UGC moderation)",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "psychometric_dna": FeatureFlag(
        key="psychometric_dna",
        description="Psychometric profiling and personality-career fit",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "developer_platform": FeatureFlag(
        key="developer_platform",
        description="Public API key issuance and third-party webhook integrations",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "p2p_mock_interview": FeatureFlag(
        key="p2p_mock_interview",
        description="Peer-to-peer real-time video/audio mock sessions",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
    "cognitive_load_telemetry": FeatureFlag(
        key="cognitive_load_telemetry",
        description="Keystroke cognitive load telemetry (Flagged as Preview Demo only)",
        tier=LaunchTier.TIER_3_REVIEW_GATED,
        enabled=False,
    ),
}


class FeatureFlagManager:
    """In-memory feature flag manager with audit trail and override support."""

    def __init__(self, flags: Optional[Dict[str, FeatureFlag]] = None):
        self._flags: Dict[str, FeatureFlag] = flags or {k: FeatureFlag(**asdict(v)) for k, v in DEFAULT_FLAGS.items()}
        self._audit_log: List[Dict[str, Any]] = []

    @property
    def flags(self) -> Dict[str, FeatureFlag]:
        return dict(self._flags)

    def is_enabled(
        self,
        flag_key: str,
        user_id: Optional[str] = None,
        plan: Optional[str] = None,
        region: Optional[str] = None,
    ) -> bool:
        flag = self._flags.get(flag_key)
        if not flag:
            # Unknown flags fail closed
            return False

        # 1. Kill switch immediately halts feature
        if flag.kill_switch:
            return False

        # 2. Hard flag disabled
        if not flag.enabled:
            return False

        # 3. Explicit user whitelist bypasses percentage
        if user_id and flag.allowed_user_ids:
            if user_id in flag.allowed_user_ids:
                return True

        # 4. Plan restrictions
        if flag.allowed_plans:
            if not plan or plan.lower() not in [p.lower() for p in flag.allowed_plans]:
                return False

        # 5. Region restrictions
        if flag.allowed_regions:
            if not region or region.upper() not in [r.upper() for r in flag.allowed_regions]:
                return False

        # 6. Percentage rollout (deterministic hash of user_id + flag_key)
        if flag.rollout_percentage < 100:
            if not user_id:
                return False
            bucket_val = self._hash_to_percentage(f"{flag_key}:{user_id}")
            return bucket_val <= flag.rollout_percentage

        return True

    def get_user_flags(
        self,
        user_id: Optional[str] = None,
        plan: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Dict[str, bool]:
        """Returns map of feature flags and active boolean state for a given user context."""
        return {
            k: self.is_enabled(k, user_id=user_id, plan=plan, region=region)
            for k in self._flags.keys()
        }

    def set_kill_switch(self, flag_key: str, killed: bool, actor: str) -> bool:
        """Instantly activates or deactivates a kill switch, recording audit evidence."""
        flag = self._flags.get(flag_key)
        if not flag:
            return False

        old_state = flag.kill_switch
        flag.kill_switch = killed
        flag.updated_at = datetime.now(timezone.utc).isoformat()
        flag.updated_by = actor

        self._audit_log.append({
            "timestamp": flag.updated_at,
            "actor": actor,
            "action": "KILL_SWITCH_ENGAGED" if killed else "KILL_SWITCH_DISENGAGED",
            "flag_key": flag_key,
            "previous_state": old_state,
            "new_state": killed,
        })
        logger.warning(f"Feature flag kill switch changed for '{flag_key}': {old_state} -> {killed} by {actor}")
        return True

    def set_flag_state(self, flag_key: str, enabled: bool, actor: str) -> bool:
        flag = self._flags.get(flag_key)
        if not flag:
            return False

        old_state = flag.enabled
        flag.enabled = enabled
        flag.updated_at = datetime.now(timezone.utc).isoformat()
        flag.updated_by = actor

        self._audit_log.append({
            "timestamp": flag.updated_at,
            "actor": actor,
            "action": "FLAG_STATE_CHANGED",
            "flag_key": flag_key,
            "previous_state": old_state,
            "new_state": enabled,
        })
        return True

    def get_audit_log(self) -> List[Dict[str, Any]]:
        return list(self._audit_log)

    @staticmethod
    def _hash_to_percentage(identifier: str) -> int:
        h = hashlib.sha256(identifier.encode("utf-8")).hexdigest()
        return (int(h[:8], 16) % 100) + 1


# Global singleton instance
feature_flag_engine = FeatureFlagManager()
