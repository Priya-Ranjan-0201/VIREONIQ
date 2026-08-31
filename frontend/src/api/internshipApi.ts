import api from '../lib/axios';

export interface InternshipTask {
  id: string;
  company: string;
  role: string;
  title: string;
  description: string;
  skills: string[];
  reward_xp: number;
  difficulty: string;
  category?: string;
  deadline_hours?: number;
  starter_code?: string;
  architecture_spec?: string;
  eval_criteria?: string[];
}

export interface TaskEvaluationResult {
  score: number;
  strengths: string[];
  improvements: string[];
  feedback: string;
  passed: boolean;
  certificate_id?: string | null;
  verified_badge?: string;
  xp_earned: number;
  company?: string;
  task_title?: string;
  difficulty?: string;
}

export const internshipApi = {
  getTasks: async (): Promise<InternshipTask[]> => {
    const response = await api.get('/internships/tasks');
    return response.data;
  },
  
  submitTask: async (taskId: string, solution: string): Promise<TaskEvaluationResult> => {
    const response = await api.post(`/internships/tasks/${taskId}/submit`, { solution });
    return response.data;
  }
};
