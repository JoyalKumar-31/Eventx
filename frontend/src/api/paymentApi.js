import apiClient from "./client";

export const paymentApi = {
  createOrder: async (registrationId) => {
    const res = await apiClient.post("/payments/create-order", { registration_id: registrationId });
    return res.data;
  },
  verifyPayment: async (verificationData) => {
    const res = await apiClient.post("/payments/verify", verificationData);
    return res.data;
  },
  getMyPayments: async () => {
    const res = await apiClient.get("/payments/my");
    return res.data;
  },
  getInvoice: async (invoiceNumber) => {
    const res = await apiClient.get(`/payments/invoices/${invoiceNumber}`);
    return res.data;
  },
  getAllPayments: async () => {
    const res = await apiClient.get("/payments/all");
    return res.data;
  },
};
