import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import client from "@/api/client";

export const useNotifications = () => {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      const { data } = await client.get("/notifications");
      return data;
    },
    refetchInterval: 30000, // Poll every 30 seconds
  });
};

export const useMarkRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await client.patch(`/notifications/${id}/read`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};

export const useCalendarStatus = () => {
  return useQuery({
    queryKey: ["calendar-status"],
    queryFn: async () => {
      const { data } = await client.get("/calendar/status");
      return data;
    },
  });
};

export const useSyncEvent = () => {
  return useMutation({
    mutationFn: async (eventId: string) => {
      const { data } = await client.post(`/calendar/sync-event/${eventId}`);
      return data;
    },
  });
};
