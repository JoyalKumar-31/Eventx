import apiClient from "./client";

export const agentsApi = {
  chat: async ({ question, role, event_context = {}, history = [] }) => {
    const res = await apiClient.post("/agents/chat", {
      question,
      role,
      event_context,
      history,
    });
    return res.data;
  },

  getSuggestions: async (role = "student") => {
    const res = await apiClient.get("/agents/suggestions", {
      params: { role },
    });
    return res.data;
  },

  getStatus: async () => {
    const res = await apiClient.get("/agents/status");
    return res.data;
  },
};
