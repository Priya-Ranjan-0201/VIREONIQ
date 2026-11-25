import api from '../lib/axios';

export interface AnalyzeGapRequest {
  target_role: string;
  company_type: string;
  experience_level_years: number;
}

export interface GapRecommendation {
  time_horizon_days: number;
  dimension: string;
  task_description: string;
  resources?: string[];
}

export interface GapAnalysisReport {
  target_role_name: string;
  company_type: string;
  overall_readiness_score: number;
  technical_gap_score: number;
  technical_gap_severity: string;
  project_gap_score: number;
  project_gap_severity: string;
  communication_gap_score: number;
  communication_gap_severity: string;
  confidence_gap_score: number;
  confidence_gap_severity: string;
  consistency_gap_score: number;
  consistency_gap_severity: string;
  placement_probability: number;
  expected_salary_band: string;
  missing_skills: string[];
  recommendations?: GapRecommendation[];
}

export interface GapHistoryResponse {
  analyses?: GapAnalysisReport[];
}

export const gapApi = {
  analyzeGap: async (data: AnalyzeGapRequest): Promise<GapAnalysisReport> => {
    const response = await api.post<GapAnalysisReport>('/gap/analyze', data);
    return response.data;
  },

  getGapHistory: async (): Promise<GapHistoryResponse> => {
    const response = await api.get<GapHistoryResponse>('/gap/history');
    return response.data;
  },
};
