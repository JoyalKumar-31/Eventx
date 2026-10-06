import apiClient from "./client";

export const eventApi = {
  getEvents: async (params = {}) => {
    const res = await apiClient.get("/events", { params });
    return res.data;
  },
  getEventById: async (id) => {
    const res = await apiClient.get(`/events/${id}`);
    return res.data;
  },
  getMyCoordinatedEvents: async () => {
    const res = await apiClient.get("/events/coordinator/my-events");
    return res.data;
  },
  createEvent: async (eventData) => {
    const res = await apiClient.post("/events", eventData);
    return res.data;
  },
  updateEvent: async (id, eventData) => {
    const res = await apiClient.put(`/events/${id}`, eventData);
    return res.data;
  },
  publishEvent: async (id) => {
    const res = await apiClient.post(`/events/${id}/publish`);
    return res.data;
  },
  unpublishEvent: async (id) => {
    const res = await apiClient.post(`/events/${id}/unpublish`);
    return res.data;
  },
  deleteEvent: async (id) => {
    const res = await apiClient.delete(`/events/${id}`);
    return res.data;
  },
  // Real Event Media Upload
  uploadEventMedia: async (eventId, file, isPrimary = true) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await apiClient.post(`/events/${eventId}/media?is_primary=${isPrimary}`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },
  deleteEventMedia: async (eventId, mediaId) => {
    const res = await apiClient.delete(`/events/${eventId}/media/${mediaId}`);
    return res.data;
  },
  setPrimaryMedia: async (eventId, mediaId) => {
    const res = await apiClient.put(`/events/${eventId}/media/${mediaId}/primary`);
    return res.data;
  },
  getCategories: async () => {
    const res = await apiClient.get("/events/categories");
    return res.data;
  },
  createCategory: async (data) => {
    const res = await apiClient.post("/events/categories", data);
    return res.data;
  },
  getVenues: async () => {
    const res = await apiClient.get("/events/venues");
    return res.data;
  },
  createVenue: async (data) => {
    const res = await apiClient.post("/events/venues", data);
    return res.data;
  },
  updateVenue: async (id, data) => {
    const res = await apiClient.put(`/events/venues/${id}`, data);
    return res.data;
  },
};
