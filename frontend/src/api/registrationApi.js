import apiClient from "./client";

export const registrationApi = {
  register: async (data) => {
    const res = await apiClient.post("/registrations", data);
    return res.data;
  },
  getMyRegistrations: async () => {
    const res = await apiClient.get("/registrations/my");
    return res.data;
  },
  getQREntryPass: async (registrationId) => {
    const res = await apiClient.get(`/registrations/${registrationId}/pass`);
    return res.data;
  },
  getEventParticipants: async (eventId) => {
    const res = await apiClient.get(`/registrations/event/${eventId}`);
    return res.data;
  },
};
