import apiClient from "./client";

export const teamApi = {
  createTeam: async (data) => {
    const res = await apiClient.post("/teams", data);
    return res.data;
  },
  joinTeam: async (data) => {
    const res = await apiClient.post("/teams/join", data);
    return res.data;
  },
  getMyTeams: async () => {
    const res = await apiClient.get("/teams/my");
    return res.data;
  },
  getTeamDetail: async (id) => {
    const res = await apiClient.get(`/teams/${id}`);
    return res.data;
  },
};
