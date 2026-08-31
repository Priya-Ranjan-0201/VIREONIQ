import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "@/api/client";

export const useCreateOrder = () => {
  return useMutation({
    mutationFn: async (planId: string) => {
      const { data } = await client.post(`/payments/order?plan_id=${planId}`);
      return data;
    },
  });
};

export const useVerifyPayment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { order_id: string; payment_id: string; signature: string; plan_id: string }) => {
      const { data } = await client.post(`/payments/verify`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });
};

export const useSubscription = () => {
  return useQuery({
    queryKey: ["subscription"],
    queryFn: async () => {
      const { data } = await client.get("/auth/me"); // Assuming subscription is part of user profile
      return data.subscription;
    },
  });
};
