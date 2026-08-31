import { create } from 'zustand';
import { analyticsApi } from '../api/analyticsApi';
import type { DashboardOverview } from '../api/analyticsApi';

interface AnalyticsState {
  overview: DashboardOverview | null;
  isLoading: boolean;
  error: string | null;
  
  fetchOverview: () => Promise<void>;
}

export const useAnalyticsStore = create<AnalyticsState>((set) => ({
  overview: null,
  isLoading: false,
  error: null,

  fetchOverview: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await analyticsApi.getOverview();
      set({ overview: data, isLoading: false });
    } catch (error: any) {
      console.error('Failed to fetch dashboard overview:', error);
      set({ error: error.response?.data?.detail || 'Failed to fetch dashboard data', isLoading: false });
    }
  }
}));
