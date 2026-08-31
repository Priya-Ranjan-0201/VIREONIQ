import api from '../lib/axios';

export interface SkillDecayItem {
  topic: string;
  retention: number; // 0.0 to 1.0
  mastery: number;   // 0.0 to 1.0
  stability_days: number;
  days_since_practice: number;
  alert: boolean;
  category?: string;
  lastTestedDate?: string;
}

export interface PracticeResult {
  topic: string;
  retention: number;
  mastery: number;
  stability_days: number;
  days_since_practice: number;
  alert: boolean;
  status: string;
}

export const skillDecayApi = {
  getSkillDecayStatus: async (): Promise<SkillDecayItem[]> => {
    const response = await api.get('/skill-decay/status');
    return response.data;
  },

  practiceTopic: async (topic: string, score: number = 0.95): Promise<PracticeResult> => {
    const response = await api.post('/skill-decay/practice', { topic, score });
    return response.data;
  }
};
