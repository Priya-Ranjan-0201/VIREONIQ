import api from '../lib/axios';

export interface SyllabusOptimization {
  industry_gold: {
    topic: string;
    why_it_matters: string;
    real_world_application: string;
    priority: string;
  }[];
  academic_filler: {
    topic: string;
    industry_replacement: string;
    reason: string;
  }[];
  career_roadmap: {
    phase: string;
    target_skill: string;
    industry_milestone: string;
  }[];
  overall_relevance_score: number;
}

export const learningApi = {
  optimizeSyllabus: async (file: File): Promise<SyllabusOptimization> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/syllabus/optimize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
};
