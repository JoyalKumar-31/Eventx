import apiClient from "./client";

export const judgeApi = {
  assignJudge: async (data) => {
    const res = await apiClient.post("/judges/assign", data);
    return res.data;
  },
  getMyAssignedEvents: async () => {
    const res = await apiClient.get("/judges/my-events");
    return res.data;
  },
  getEventJudgeAssignments: async (eventId) => {
    const res = await apiClient.get(`/judges/event/${eventId}/assignments`);
    return res.data;
  },
  unassignJudge: async (assignmentId) => {
    const res = await apiClient.delete(`/judges/assignments/${assignmentId}`);
    return res.data;
  },
  createCriteria: async (data) => {
    const res = await apiClient.post("/judges/criteria", data);
    return res.data;
  },
  deleteCriteria: async (criteriaId) => {
    const res = await apiClient.delete(`/judges/criteria/${criteriaId}`);
    return res.data;
  },
  getEventCriteria: async (eventId) => {
    const res = await apiClient.get(`/judges/criteria/${eventId}`);
    return res.data;
  },
  submitScores: async (eventId, data) => {
    const res = await apiClient.post(`/scores/event/${eventId}`, data);
    return res.data;
  },
  getEventScores: async (eventId, registrationId) => {
    const res = await apiClient.get(`/scores/event/${eventId}?registration_id=${registrationId}`);
    return res.data;
  },
  getLeaderboard: async (eventId, roundId = null) => {
    const url = roundId ? `/results/leaderboard/${eventId}?round_id=${roundId}` : `/results/leaderboard/${eventId}`;
    const res = await apiClient.get(url);
    return res.data;
  },
  publishResults: async (eventId, roundId = null) => {
    const url = roundId ? `/results/publish/${eventId}?round_id=${roundId}` : `/results/publish/${eventId}`;
    const res = await apiClient.post(url);
    return res.data;
  },
  getPublicResults: async (eventId) => {
    const res = await apiClient.get(`/results/public/${eventId}`);
    return res.data;
  },
  getAllPublicResults: async () => {
    const res = await apiClient.get("/results/public");
    return res.data;
  },
};
