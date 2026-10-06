import apiClient from "./client";

export const announcementApi = {
  getAnnouncements: async (target = null) => {
    const params = target ? { target } : {};
    const res = await apiClient.get("/announcements", { params });
    return res.data;
  },
  createAnnouncement: async (data) => {
    const res = await apiClient.post("/announcements", data);
    return res.data;
  },
  deleteAnnouncement: async (id) => {
    const res = await apiClient.delete(`/announcements/${id}`);
    return res.data;
  },
};
