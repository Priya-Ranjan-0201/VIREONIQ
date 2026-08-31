import api from '../lib/axios';

export interface Candidate {
  id: string;
  name: string;
  role: string;
  ats_score: number;
  readiness_score: number;
  status: string;
}

export const recruiterApi = {
  searchCandidates: async (params?: { role?: string; min_ats?: number; min_readiness?: number }): Promise<Candidate[]> => {
    const response = await api.get('/recruiter/candidates', { params });
    return response.data;
  },
  
  getCandidateReport: async (id: string) => {
    const response = await api.get(`/recruiter/candidates/${id}/report`);
    return response.data;
  }
};
