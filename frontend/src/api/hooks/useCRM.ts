import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import client from "@/api/client";

export const useApplications = () => {
  return useQuery({
    queryKey: ["applications"],
    queryFn: async () => {
      const { data } = await client.get("/crm/applications");
      return data;
    },
  });
};

export const useUpdateAppStage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ appId, status }: { appId: string; status: string }) => {
      const { data } = await client.patch(`/crm/applications/${appId}`, { status });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
};

export const useAddAppEvent = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ appId, event }: { appId: string; event: any }) => {
      const { data } = await client.post(`/crm/applications/${appId}/events`, event);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
};

export const useAddOffer = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (offer: any) => {
      const { data } = await client.post("/crm/offers", offer);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
};

export const useCompareOffers = () => {
  return useQuery({
    queryKey: ["offers-comparison"],
    queryFn: async () => {
      const { data } = await client.get("/crm/offers/compare");
      return data;
    },
  });
};

export const useFunnelAnalytics = () => {
  return useQuery({
    queryKey: ["funnel-analytics"],
    queryFn: async () => {
      const { data } = await client.get("/crm/analytics/funnel");
      return data;
    },
  });
};
