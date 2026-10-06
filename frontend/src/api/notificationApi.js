import apiClient from "./client";

export const notificationApi = {
  getNotifications: async (params = {}) => {
    const res = await apiClient.get("/notifications", { params });
    return res.data;
  },
  markRead: async (notificationIds = null) => {
    const res = await apiClient.post("/notifications/mark-read", {
      notification_ids: notificationIds,
    });
    return res.data;
  },
  getUnreadCount: async () => {
    const res = await apiClient.get("/notifications/unread-count");
    return res.data;
  },
};
