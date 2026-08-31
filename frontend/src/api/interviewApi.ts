import api from '../lib/axios';

export interface StartInterviewRequest {
  target_role: string;
  difficulty_level: number;
  session_mode: string;
}

export interface AnswerSubmission {
  answer_text: string;
}

export const interviewApi = {
  startSession: async (data: StartInterviewRequest) => {
    const response = await api.post('/interview/start', data);
    return response.data;
  },

  submitAnswer: async (sessionId: string, data: AnswerSubmission) => {
    const response = await api.post(`/interview/${sessionId}/answer`, data);
    return response.data;
  },

  getScorecard: async (sessionId: string) => {
    const response = await api.get(`/interview/${sessionId}/scorecard`);
    return response.data;
  }
};
