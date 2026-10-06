import apiClient from "./client";

export const publicApi = {
  getStats: async () => {
    const res = await apiClient.get("/public/stats");
    return res.data;
  },
  getSchedules: async () => {
    const res = await apiClient.get("/public/schedules");
    return res.data;
  },
  getVenues: async () => {
    const res = await apiClient.get("/public/venues");
    return res.data;
  },
};
