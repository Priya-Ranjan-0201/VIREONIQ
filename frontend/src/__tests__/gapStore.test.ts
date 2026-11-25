import { describe, it, expect, vi, beforeEach } from 'vitest';
import { gapApi } from '@/api/gapApi';
import type { GapAnalysisReport } from '@/api/gapApi';
import { useGapStore } from '@/store/gapStore';

vi.mock('@/api/gapApi', () => ({
  gapApi: {
    analyzeGap: vi.fn(),
    getGapHistory: vi.fn(),
  },
}));

const sampleReport: GapAnalysisReport = {
  target_role_name: 'Backend Engineer',
  company_type: 'Product',
  overall_readiness_score: 78,
  technical_gap_score: 80,
  technical_gap_severity: 'Minor',
  project_gap_score: 75,
  project_gap_severity: 'Moderate',
  communication_gap_score: 82,
  communication_gap_severity: 'Minor',
  confidence_gap_score: 79,
  confidence_gap_severity: 'Minor',
  consistency_gap_score: 74,
  consistency_gap_severity: 'Moderate',
  placement_probability: 72,
  expected_salary_band: '18-24 LPA',
  missing_skills: ['Kubernetes'],
  recommendations: [],
};

describe('useGapStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useGapStore.setState({ analysis: null, history: [], isLoading: false, error: null });
  });

  it('stores gap analysis report on success', async () => {
    vi.mocked(gapApi.analyzeGap).mockResolvedValueOnce(sampleReport);

    await useGapStore.getState().analyzeGap({
      target_role: 'Backend Engineer',
      company_type: 'Product',
      experience_level_years: 2,
    });

    expect(useGapStore.getState().analysis).toEqual(sampleReport);
    expect(useGapStore.getState().error).toBeNull();
    expect(useGapStore.getState().isLoading).toBe(false);
  });

  it('captures API error details on failure without leaving loading stuck', async () => {
    vi.mocked(gapApi.analyzeGap).mockRejectedValueOnce({
      response: { data: { detail: 'No parsed resume found' } },
    });

    await useGapStore.getState().analyzeGap({
      target_role: 'Backend Engineer',
      company_type: 'Product',
      experience_level_years: 2,
    });

    expect(useGapStore.getState().analysis).toBeNull();
    expect(useGapStore.getState().error).toBe('No parsed resume found');
    expect(useGapStore.getState().isLoading).toBe(false);
  });
});
