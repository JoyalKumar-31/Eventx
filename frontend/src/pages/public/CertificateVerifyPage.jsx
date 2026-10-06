import React, { useState, useEffect } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import {
  ShieldCheck,
  ShieldAlert,
  Search,
  Download,
  Calendar,
  Award,
  CheckCircle2,
  FileText,
  User,
  ExternalLink,
} from "lucide-react";
import { certificateApi } from "../../api/certificateApi";

export default function CertificateVerifyPage() {
  const { hash: paramHash } = useParams();
  const [searchParams] = useSearchParams();
  const initialHash = paramHash || searchParams.get("id") || "";

  const [inputHash, setInputHash] = useState(initialHash);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (initialHash) {
      verify(initialHash);
    }
  }, [initialHash]);

  const verify = async (code) => {
    const cleanCode = code.trim();
    if (!cleanCode) return;
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const data = await certificateApi.verifyCertificate(cleanCode);
      setResult(data);
    } catch (err) {
      console.error("Verification failed", err);
      setError(
        err.response?.data?.detail ||
          "Certificate not found. Please double-check the Certificate ID or Verification Hash."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    verify(inputHash);
  };

  const handleDownload = async () => {
    if (!result?.id) return;
    try {
      setDownloading(true);
      await certificateApi.downloadCertificatePdf(result.id, result.certificate_number);
    } catch (err) {
      console.error("Download failed", err);
      alert("Failed to download PDF. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5" /> Official Verification Registry
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
            Verify Certificate
          </h1>
          <p className="text-slate-400 text-sm sm:text-base">
            Instantly validate cryptographic authenticity for student awards and participation credentials issued by the Fest Committee.
          </p>
        </div>

        {/* Verification Input Form */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex flex-col sm:flex-row items-center gap-3 p-2 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl">
            <div className="relative w-full">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Enter Certificate Number (e.g. CERT-2026-...) or Hash"
                value={inputHash}
                onChange={(e) => setInputHash(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !inputHash.trim()}
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-sm transition-all whitespace-nowrap shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <ShieldCheck className="w-4 h-4" />
              )}
              Verify Now
            </button>
          </div>
        </form>

        {/* Error message */}
        {error && (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-center space-y-2">
            <ShieldAlert className="w-8 h-8 text-rose-400 mx-auto" />
            <h4 className="font-bold text-white text-base">Invalid or Unregistered Certificate</h4>
            <p className="text-xs text-rose-300/80">{error}</p>
          </div>
        )}

        {/* Verified Result Card */}
        {result && (
          <div className="p-6 sm:p-8 rounded-3xl bg-slate-900/90 border border-emerald-500/40 shadow-2xl space-y-6 relative overflow-hidden">
            <div className="absolute -top-12 -right-12 w-40 h-40 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />

            {/* Verification Status */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-5">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                    Authentic & Validated Credential
                  </div>
                  <h3 className="text-lg font-bold text-white">Verified Official Record</h3>
                </div>
              </div>
              <span className="text-[11px] font-mono text-slate-400 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
                {result.certificate_type || "PARTICIPATION"}
              </span>
            </div>

            {/* Details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1">
                  <User className="w-3.5 h-3.5" /> Issued To
                </span>
                <p className="text-base font-bold text-white">
                  {result.user?.full_name || "Participant"}
                </p>
                <p className="text-xs text-slate-400">{result.user?.email}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1">
                  <Award className="w-3.5 h-3.5" /> Event Title
                </span>
                <p className="text-base font-bold text-white">
                  {result.event?.title || "College Fest Event"}
                </p>
                <p className="text-xs text-slate-400">
                  Category: {result.event?.category?.name || "General"}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1">
                  <FileText className="w-3.5 h-3.5" /> Certificate Number
                </span>
                <p className="text-xs font-mono font-bold text-emerald-300 break-all">
                  {result.certificate_number}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" /> Issue Date
                </span>
                <p className="text-xs text-slate-300">
                  {result.issued_at
                    ? new Date(result.issued_at).toLocaleDateString(undefined, {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })
                    : "Verified"}
                </p>
              </div>
            </div>

            {/* Cryptographic Hash */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-400 break-all space-y-1">
              <span className="text-slate-500 block uppercase text-[10px] font-bold">
                Verification Hash (SHA-256)
              </span>
              <span className="text-slate-300">{result.verification_hash}</span>
            </div>

            {/* Action buttons */}
            <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
              <button
                onClick={handleDownload}
                disabled={downloading}
                className="w-full sm:flex-1 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition-all shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2"
              >
                {downloading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                Download Official Certificate PDF
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
