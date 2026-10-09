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
  getCoordinatorApplications: async (status) => {
    const params = status ? { status } : {};
    const res = await apiClient.get("/admin/applications/coordinators", { params });
    return res.data;
  },
  approveCoordinatorApplication: async (id, notes) => {
    const res = await apiClient.post(`/admin/applications/coordinators/${id}/approve`, { admin_notes: notes });
    return res.data;
  },
  rejectCoordinatorApplication: async (id, notes) => {
    const res = await apiClient.post(`/admin/applications/coordinators/${id}/reject`, { admin_notes: notes });
    return res.data;
  },
  getJudgeApplications: async (status) => {
    const params = status ? { status } : {};
    const res = await apiClient.get("/admin/applications/judges", { params });
    return res.data;
  },
  approveJudgeApplication: async (id, notes) => {
    const res = await apiClient.post(`/admin/applications/judges/${id}/approve`, { admin_notes: notes });
    return res.data;
  },
  rejectJudgeApplication: async (id, notes) => {
    const res = await apiClient.post(`/admin/applications/judges/${id}/reject`, { admin_notes: notes });
    return res.data;
  },
  createInvitation: async (data) => {
    const res = await apiClient.post("/admin/invitations", data);
    return res.data;
  },
  getInvitations: async (params = {}) => {
    const res = await apiClient.get("/admin/invitations", { params });
    return res.data;
  },
  revokeInvitation: async (id) => {
    const res = await apiClient.delete(`/admin/invitations/${id}`);
    return res.data;
  },
};
