import api from '../lib/axios';

export interface BenchmarkReport {
  user_metrics: any;
  global_averages: any;
  percentile_ranking: number;
  readiness_summary: string;
  peer_comparison: {
    ats: number;
    technical: number;
    communication: number;
  };
}

export const reportApi = {
  getBenchmarkReport: async (): Promise<BenchmarkReport> => {
    const response = await api.get('/reports/benchmark');
    return response.data;
  }
};
