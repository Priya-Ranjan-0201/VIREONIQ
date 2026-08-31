import client from "./client";

export const logActivity = async (eventType: string, metadata: any = {}) => {
  try {
    await client.post("/analytics/log", {
      event_type: eventType,
      metadata_json: metadata
    });
  } catch (e) {
    console.error("Failed to log activity", e);
  }
};

export const joinWaitlist = async (email: string, fullName: string) => {
  const { data } = await client.post("/waitlist/join", { email, full_name: fullName });
  return data;
};
