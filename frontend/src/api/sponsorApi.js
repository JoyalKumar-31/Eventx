import apiClient from "./client";

export const sponsorApi = {
  getPlans: async () => {
    const res = await apiClient.get("/sponsors/plans");
    return res.data;
  },
  createPlan: async (planData) => {
    const res = await apiClient.post("/sponsors/plans", planData);
    return res.data;
  },
  selectPlan: async (data) => {
    const res = await apiClient.post("/sponsors/select-plan", data);
    return res.data;
  },
  getMySponsorships: async () => {
    const res = await apiClient.get("/sponsors/my-sponsorships");
    return res.data;
  },
  createPromotion: async (promoData) => {
    const res = await apiClient.post("/sponsors/promotions", promoData);
    return res.data;
  },
  getActivePromotions: async () => {
    const res = await apiClient.get("/sponsors/promotions/active");
    return res.data;
  },
  trackClick: async (slotId) => {
    const res = await apiClient.post(`/sponsors/promotions/${slotId}/track-click`);
    return res.data;
  },
  getMetrics: async () => {
    const res = await apiClient.get("/sponsors/metrics");
    return res.data;
  },
};
