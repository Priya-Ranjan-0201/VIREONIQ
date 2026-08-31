import api from '../lib/axios';

export interface MockOffer {
  base_salary: number;
  currency: string;
  joining_bonus: number;
  equity_text: string;
  benefits: string[];
  negotiation_leverage: 'High' | 'Medium' | 'Low';
  negotiation_tips: string[];
}

export const offerApi = {
  generateOffer: async (sessionId: string): Promise<MockOffer> => {
    const response = await api.post(`/offers/generate/${sessionId}`);
    return response.data;
  },
  
  getNegotiationTips: async (offerId: string) => {
    const response = await api.get(`/offers/${offerId}/negotiate`);
    return response.data;
  }
};
