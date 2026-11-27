import { create } from 'zustand';
import api from './axios';

export type LaunchTier = 'tier_1_public_beta' | 'tier_2_invite_only' | 'tier_3_review_gated';

export interface FeatureFlagsMap {
  [key: string]: boolean;
}

// Client-side defaults matching Phase L1 launch tiers
export const DEFAULT_CLIENT_FLAGS: FeatureFlagsMap = {
  // Tier 1 (Public Beta - Enabled)
  ats_resume_studio: true,
  jd_matcher: true,
  interview_studio: true,
  career_readiness_engine: true,
  bullet_section_rewriter: true,

  // Tier 2 (Invite-Only / Flagged)
  career_simulator: true,
  career_gps: true,
  smart_apply_tracker: true,
  talent_passport: true,
  gamification_system: true,
  paid_monetization_plans: false,

  // Tier 3 (Review Gated / Hidden)
  recruiter_war_room: false,
  workforce_intelligence: false,
  parent_dashboard: false,
  highschool_trajectory: false,
  employer_truth_score: false,
  community_hub: false,
  psychometric_dna: false,
  developer_platform: false,
  p2p_mock_interview: false,
  cognitive_load_telemetry: false,
};

interface FeatureFlagStore {
  flags: FeatureFlagsMap;
  isLoaded: boolean;
  fetchFlags: () => Promise<void>;
  isEnabled: (flagKey: string) => boolean;
}

export const useFeatureFlagStore = create<FeatureFlagStore>((set, get) => ({
  flags: DEFAULT_CLIENT_FLAGS,
  isLoaded: false,
  fetchFlags: async () => {
    try {
      const res = await api.get('/system/features');
      if (res.data && res.data.flags) {
        set({ flags: { ...DEFAULT_CLIENT_FLAGS, ...res.data.flags }, isLoaded: true });
      }
    } catch {
      // Fall back to secure defaults
      set({ flags: DEFAULT_CLIENT_FLAGS, isLoaded: true });
    }
  },
  isEnabled: (flagKey: string) => {
    const flags = get().flags;
    return Boolean(flags[flagKey]);
  },
}));

export const isFeatureEnabled = (flagKey: string): boolean => {
  return Boolean(useFeatureFlagStore.getState().flags[flagKey]);
};
