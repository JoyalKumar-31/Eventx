import apiClient from "./client";

export const certificateApi = {
  getMyCertificates: async () => {
    const res = await apiClient.get("/certificates/my");
    return res.data;
  },
  downloadCertificatePdf: async (certificateId, certNumber) => {
    const res = await apiClient.get(`/certificates/${certificateId}/download`, {
      responseType: "blob",
    });
    // Trigger browser file download
    const url = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${certNumber || "certificate"}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  verifyCertificate: async (hashOrNumber) => {
    const res = await apiClient.get(`/certificates/verify/${encodeURIComponent(hashOrNumber)}`);
    return res.data;
  },
};
