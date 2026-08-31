import { create } from 'zustand';
import { gapApi } from '../api/gapApi';
import type { AnalyzeGapRequest } from '../api/gapApi';

interface GapState {
  analysis: any | null;
  history: any[];
  isLoading: boolean;
  error: string | null;
  
  analyzeGap: (params: AnalyzeGapRequest) => Promise<void>;
  fetchHistory: () => Promise<void>;
}

export const useGapStore = create<GapState>((set) => ({
  analysis: null,
  history: [],
  isLoading: false,
  error: null,

  analyzeGap: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const data = await gapApi.analyzeGap(params);
      set({ analysis: data, isLoading: false });
    } catch (error: any) {
      console.error('Failed to analyze gap:', error);
      set({ error: error.response?.data?.detail || 'Analysis failed', isLoading: false });
    }
  },

  fetchHistory: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await gapApi.getGapHistory();
      set({ history: data.analyses || [], isLoading: false });
    } catch (error: any) {
      console.error('Failed to fetch history:', error);
      set({ error: error.response?.data?.detail || 'Failed to fetch history', isLoading: false });
    }
  }
}));
