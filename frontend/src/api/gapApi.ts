import api from '../lib/axios';

export interface AnalyzeGapRequest {
  target_role: string;
  company_type: string;
  experience_level_years: number;
}

export const gapApi = {
  analyzeGap: async (data: AnalyzeGapRequest) => {
    const response = await api.post('/gap/analyze', data);
    return response.data;
  },

  getGapHistory: async () => {
    const response = await api.get('/gap/history');
    return response.data;
  }
};
