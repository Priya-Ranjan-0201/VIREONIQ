import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import client from "@/api/client";

export const useRecommendations = () => {
  return useQuery({
    queryKey: ["recommendations"],
    queryFn: async () => {
      const { data } = await client.get("/recommendations/jobs");
      return data;
    },
  });
};

export const useEmployabilityStats = () => {
  return useQuery({
    queryKey: ["employability-stats"],
    queryFn: async () => {
      const { data } = await client.get("/recommendations/stats");
      return data;
    },
  });
};

export const useTrackApplication = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ jobId, status }: { jobId: string; status: string }) => {
      const { data } = await client.post(`/crm/applications?job_id=${jobId}&status=${status}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
};
