import { create } from 'zustand';
import { offerApi } from '../api/offerApi';
import type { MockOffer } from '../api/offerApi';

interface OfferState {
  currentOffer: MockOffer | null;
  isLoading: boolean;
  error: string | null;
  
  generateOffer: (sessionId: string) => Promise<void>;
}

export const useOfferStore = create<OfferState>((set) => ({
  currentOffer: null,
  isLoading: false,
  error: null,

  generateOffer: async (sessionId) => {
    set({ isLoading: true, error: null });
    try {
      const data = await offerApi.generateOffer(sessionId);
      set({ currentOffer: data, isLoading: false });
    } catch (error: any) {
      console.error('Failed to generate mock offer:', error);
      set({ error: error.response?.data?.detail || 'Failed to generate offer', isLoading: false });
    }
  }
}));
