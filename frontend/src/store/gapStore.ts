import { create } from 'zustand';
import { extractApiErrorMessage } from '../lib/errors';
import type { AnalyzeGapRequest, GapAnalysisReport } from '../api/gapApi';
import { gapApi } from '../api/gapApi';

interface GapState {
  analysis: GapAnalysisReport | null;
  history: GapAnalysisReport[];
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
    } catch (error: unknown) {
      set({ error: extractApiErrorMessage(error, 'Analysis failed'), isLoading: false });
    }
  },

  fetchHistory: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await gapApi.getGapHistory();
      set({ history: data.analyses || [], isLoading: false });
    } catch (error: unknown) {
      set({ error: extractApiErrorMessage(error, 'Failed to fetch history'), isLoading: false });
    }
  },
}));
