import apiClient from "./client";

export const attendanceApi = {
  scanQR: async (scanData) => {
    const res = await apiClient.post("/attendance/scan", scanData);
    return res.data;
  },
  getEventAttendance: async (eventId) => {
    const res = await apiClient.get(`/attendance/event/${eventId}`);
    return res.data;
  },
  getEventAttendanceStats: async (eventId) => {
    const res = await apiClient.get(`/attendance/stats/${eventId}`);
    return res.data;
  },
};
