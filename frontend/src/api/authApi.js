import apiClient from "./client";

export const authApi = {
  login: async (credentials) => {
    const res = await apiClient.post("/auth/login", credentials);
    return res.data;
  },
  register: async (userData) => {
    const res = await apiClient.post("/auth/register", userData);
    return res.data;
  },
  getMe: async () => {
    const res = await apiClient.get("/auth/me");
    return res.data;
  },
  logout: async () => {
    try {
      await apiClient.post("/auth/logout");
    } finally {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }
  },
  applyCoordinator: async (data) => {
    const res = await apiClient.post("/auth/apply/coordinator", data);
    return res.data;
  },
  applyJudge: async (data) => {
    const res = await apiClient.post("/auth/apply/judge", data);
    return res.data;
  },
  checkApplicationStatus: async (email) => {
    const res = await apiClient.get("/auth/application/status", { params: { email } });
    return res.data;
  },
};
