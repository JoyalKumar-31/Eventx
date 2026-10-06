import React, { useState, useEffect, useRef } from "react";
import { X, Camera, CheckCircle2, AlertTriangle, AlertCircle, Scan, ArrowRight } from "lucide-react";
import { Html5Qrcode } from "html5-qrcode";
import { attendanceApi } from "../api/attendanceApi";

export const QRScannerModal = ({ isOpen, onClose, eventId = null, onScanSuccess }) => {
  const [manualCode, setManualCode] = useState("");
  const [scanning, setScanning] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const html5QrCodeRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      startCamera();
    } else {
      stopCamera();
      setLastResult(null);
      setManualCode("");
    }
    return () => {
      stopCamera();
    };
  }, [isOpen]);

  const startCamera = async () => {
    try {
      setScanning(true);
      const html5QrCode = new Html5Qrcode("qr-reader-container");
      html5QrCodeRef.current = html5QrCode;

      await html5QrCode.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        (decodedText) => {
          handleVerify(decodedText);
        },
        (errorMessage) => {
          // ignore scan frame errors
        }
      );
    } catch (err) {
      console.warn("Unable to start camera for QR scanner:", err);
      setScanning(false);
    }
  };

  const stopCamera = async () => {
    if (html5QrCodeRef.current && html5QrCodeRef.current.isScanning) {
      try {
        await html5QrCodeRef.current.stop();
        html5QrCodeRef.current.clear();
      } catch (err) {
        console.warn("Error stopping scanner:", err);
      }
    }
  };

  const handleVerify = async (payload) => {
    if (loading) return;
    setLoading(true);

    try {
      const res = await attendanceApi.scanQR({
        qr_payload: payload,
        event_id: eventId,
      });
      setLastResult({
        status: "VALID",
        message: "Attendance confirmed! Entry granted.",
        participant: res.participant_name,
        email: res.participant_email,
        event: res.event_title,
        time: new Date().toLocaleTimeString(),
      });
      if (onScanSuccess) onScanSuccess(res);
    } catch (err) {
      const errData = err.response?.data;
      if (err.response?.status === 409) {
        setLastResult({
          status: "DUPLICATE",
          message: errData?.message || "Duplicate entry attempt! Pass has already been used.",
          participant: errData?.participant_name || "Unknown",
          event: errData?.event_title || "",
          time: new Date().toLocaleTimeString(),
        });
      } else {
        setLastResult({
          status: "INVALID",
          message: errData?.message || "Invalid or unrecognized pass code.",
          time: new Date().toLocaleTimeString(),
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleManualSubmit = (e) => {
    e.preventDefault();
    if (!manualCode.trim()) return;
    handleVerify(manualCode.trim());
    setManualCode("");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-lg rounded-3xl border border-slate-700 bg-slate-900 p-6 md:p-8 shadow-2xl my-8">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2 text-indigo-400">
            <Scan className="w-5 h-5" />
            <h3 className="text-lg font-bold text-white">Live Attendance QR Scanner</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Camera Viewport */}
        <div className="mt-6 flex flex-col items-center">
          <div
            id="qr-reader-container"
            className="w-full h-64 rounded-2xl overflow-hidden bg-black border border-slate-700 shadow-inner flex items-center justify-center"
          />

          {!scanning && (
            <p className="mt-2 text-xs text-slate-400 text-center">
              Camera unavailable or permission denied. Use manual code entry below.
            </p>
          )}
        </div>

        {/* Scan Status / Result Banner */}
        {lastResult && (
          <div
            className={`mt-6 p-4 rounded-2xl border transition-all ${
              lastResult.status === "VALID"
                ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300"
                : lastResult.status === "DUPLICATE"
                ? "bg-amber-500/10 border-amber-500/40 text-amber-300"
                : "bg-rose-500/10 border-rose-500/40 text-rose-300"
            }`}
          >
            <div className="flex items-start gap-3">
              {lastResult.status === "VALID" && <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />}
              {lastResult.status === "DUPLICATE" && <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />}
              {lastResult.status === "INVALID" && <AlertCircle className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />}

              <div className="flex-1">
                <h4 className="text-sm font-bold">{lastResult.message}</h4>
                {lastResult.participant && (
                  <p className="mt-1 text-xs text-slate-200">
                    Attendee: <strong className="font-semibold text-white">{lastResult.participant}</strong>
                  </p>
                )}
                {lastResult.event && (
                  <p className="text-xs text-slate-300">Event: {lastResult.event}</p>
                )}
                <span className="text-xs text-slate-400 mt-1 inline-block">Timestamp: {lastResult.time}</span>
              </div>
            </div>
          </div>
        )}

        {/* Manual Code Fallback */}
        <form onSubmit={handleManualSubmit} className="mt-6 pt-4 border-t border-slate-800">
          <label className="text-xs font-semibold text-slate-300">
            Manual Registration Number or Token Entry
          </label>
          <div className="mt-2 flex items-center gap-2">
            <input
              type="text"
              value={manualCode}
              onChange={(e) => setManualCode(e.target.value)}
              placeholder="e.g. REG-001-A1B2C3"
              className="flex-1 px-4 py-2.5 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              disabled={loading || !manualCode.trim()}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition-all shadow-md shadow-indigo-600/20 cursor-pointer flex items-center gap-1.5"
            >
              <span>Validate</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QRScannerModal;
