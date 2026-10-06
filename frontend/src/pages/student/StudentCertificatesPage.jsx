import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Award, Download, ExternalLink, ShieldCheck, Calendar, Search } from "lucide-react";
import { certificateApi } from "../../api/certificateApi";
import EmptyState from "../../components/EmptyState";

export default function StudentCertificatesPage() {
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    fetchCertificates();
  }, []);

  const fetchCertificates = async () => {
    try {
      setLoading(true);
      const data = await certificateApi.getMyCertificates();
      setCertificates(data || []);
    } catch (err) {
      console.error("Failed to load certificates", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (cert) => {
    try {
      setDownloadingId(cert.id);
      await certificateApi.downloadCertificatePdf(cert.id, cert.certificate_number);
    } catch (err) {
      console.error("Failed to download PDF", err);
      alert("Failed to download certificate PDF. Please try again.");
    } finally {
      setDownloadingId(null);
    }
  };

  const getBadgeStyle = (type) => {
    switch (type) {
      case "WINNER":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40";
      case "RUNNER_UP":
        return "bg-slate-300/20 text-slate-200 border-slate-300/40";
      default:
        return "bg-indigo-500/20 text-indigo-300 border-indigo-500/40";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          My Certificates & Accreditations
        </h1>
        <p className="text-slate-400 text-sm">
          Download vector PDF certificates for your festival participation, accomplishments, and wins.
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-60 rounded-3xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : certificates.length === 0 ? (
        <EmptyState
          icon={Award}
          title="No Certificates Issued Yet"
          description="Certificates are generated automatically after event results are published by the coordinators."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {certificates.map((cert) => (
            <div
              key={cert.id}
              className="p-6 rounded-3xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between shadow-xl"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wider ${getBadgeStyle(
                      cert.certificate_type
                    )}`}
                  >
                    {cert.certificate_type}
                  </span>
                  <Award className="w-5 h-5 text-amber-400" />
                </div>

                <div>
                  <h3 className="text-xl font-bold text-white">
                    {cert.event?.title || `Event #${cert.event_id}`}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Issued: {new Date(cert.issued_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-400 space-y-1">
                  <span className="text-slate-500 uppercase text-[10px] block font-bold">
                    Certificate Number
                  </span>
                  <span className="text-slate-200 font-bold break-all">
                    {cert.certificate_number}
                  </span>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800 flex items-center gap-3">
                <button
                  onClick={() => handleDownload(cert)}
                  disabled={downloadingId === cert.id}
                  className="flex-1 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20"
                >
                  {downloadingId === cert.id ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                  Download PDF
                </button>

                <Link
                  to={`/verify/${cert.verification_hash || cert.certificate_number}`}
                  target="_blank"
                  className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all text-xs"
                  title="Verify Certificate"
                >
                  <ExternalLink className="w-4 h-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
