import apiClient from "./client";

export const invitationApi = {
  verifyInvitation: async (token) => {
    const res = await apiClient.get("/invitations/verify", { params: { token } });
    return res.data;
  },
  acceptInvitation: async (data) => {
    const res = await apiClient.post("/invitations/accept", data);
    return res.data;
  },
};
