import apiClient from "./client";

export const adminApi = {
  getAdminMetrics: async () => {
    const res = await apiClient.get("/admin/metrics");
    return res.data;
  },
  getCoordinatorMetrics: async () => {
    const res = await apiClient.get("/admin/coordinator-metrics");
    return res.data;
  },
  getJudgeMetrics: async () => {
    const res = await apiClient.get("/admin/judge-metrics");
    return res.data;
  },
  getAuditLogs: async (params = {}) => {
    const res = await apiClient.get("/admin/audit-logs", { params });
    return res.data;
  },
  getUsers: async (params = {}) => {
    const res = await apiClient.get("/users", { params });
    return res.data;
  },
  updateUserRole: async (userId, role) => {
    const res = await apiClient.put(`/users/${userId}/role`, { role });
    return res.data;
  },
  updateUserStatus: async (userId, isActive) => {
    const res = await apiClient.put(`/users/${userId}/status`, { is_active: isActive });
    return res.data;
  },
  getCoordinators: async () => {
    const res = await apiClient.get("/users/coordinators");
    return res.data;
  },
  getJudges: async () => {
    const res = await apiClient.get("/users/judges");
    return res.data;
  },
};
