import React, { useState, useEffect, useRef } from "react";
import {
  X,
  Camera,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Scan,
  ArrowRight,
  RefreshCw,
  SwitchCamera,
  Check,
} from "lucide-react";
import { Html5Qrcode } from "html5-qrcode";
import { attendanceApi } from "../api/attendanceApi";

export const QRScannerModal = ({ isOpen, onClose, eventId = null, onScanSuccess }) => {
  const [manualCode, setManualCode] = useState("");
  const [scanning, setScanning] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [activeCameraIndex, setActiveCameraIndex] = useState(0);

  const html5QrCodeRef = useRef(null);
  const isStartingRef = useRef(false);
  const isScanningRef = useRef(false);
  const lastScanRef = useRef({ code: "", time: 0 });

  useEffect(() => {
    if (isOpen) {
      initAndStartCamera();
    } else {
      stopCamera();
      setLastResult(null);
      setManualCode("");
    }
    return () => {
      stopCamera();
    };
  }, [isOpen]);

  const initAndStartCamera = async () => {
    if (isStartingRef.current || isScanningRef.current) return;
    isStartingRef.current = true;

    try {
      // Clean up any stale scanner instance or leftover DOM elements
      await stopCamera();

      const container = document.getElementById("qr-reader-container");
      if (container) {
        container.innerHTML = "";
      }

      // Discover camera devices
      let availableCameras = [];
      try {
        availableCameras = await Html5Qrcode.getCameras();
        setCameras(availableCameras || []);
      } catch (e) {
        console.warn("Could not enumerate camera devices:", e);
      }

      const html5QrCode = new Html5Qrcode("qr-reader-container");
      html5QrCodeRef.current = html5QrCode;

      const config = {
        fps: 10,
        qrbox: (viewfinderWidth, viewfinderHeight) => {
          const edge = Math.floor(Math.min(viewfinderWidth, viewfinderHeight) * 0.72);
          return { width: Math.max(160, edge), height: Math.max(160, edge) };
        },
        aspectRatio: 1.333333,
        disableFlip: false,
      };

      const onScanSuccessCallback = (decodedText) => {
        handleScannedCode(decodedText);
      };

      const onScanFailureCallback = () => {
        // frame scan error - ignore per-frame failures
      };

      // Select camera: preferred deviceId if available, otherwise environment facing mode
      let cameraSource = { facingMode: "environment" };
      if (availableCameras && availableCameras.length > 0) {
        // On laptops or mobile, choose back camera if available, or first camera
        const backCam = availableCameras.find(
          (c) =>
            c.label.toLowerCase().includes("back") ||
            c.label.toLowerCase().includes("rear") ||
            c.label.toLowerCase().includes("environment")
        );
        const chosen = backCam || availableCameras[activeCameraIndex % availableCameras.length];
        cameraSource = chosen.id;
      }

      try {
        await html5QrCode.start(
          cameraSource,
          config,
          onScanSuccessCallback,
          onScanFailureCallback
        );
      } catch (err1) {
        console.warn("Preferred camera start failed, falling back to default camera:", err1);
        // Fallback to default user-facing camera constraint
        await html5QrCode.start(
          { facingMode: "user" },
          config,
          onScanSuccessCallback,
          onScanFailureCallback
        );
      }

      isScanningRef.current = true;
      setScanning(true);
    } catch (err) {
      console.warn("Unable to start camera for QR scanner:", err);
      setScanning(false);
    } finally {
      isStartingRef.current = false;
    }
  };

  const stopCamera = async () => {
    isScanningRef.current = false;
    if (html5QrCodeRef.current) {
      try {
        if (html5QrCodeRef.current.isScanning) {
          await html5QrCodeRef.current.stop();
        }
        html5QrCodeRef.current.clear();
      } catch (err) {
        console.warn("Error stopping scanner:", err);
      } finally {
        html5QrCodeRef.current = null;
      }
    }
    const container = document.getElementById("qr-reader-container");
    if (container) {
      container.innerHTML = "";
    }
    setScanning(false);
  };

  const handleSwitchCamera = async () => {
    if (cameras.length <= 1) return;
    const nextIndex = (activeCameraIndex + 1) % cameras.length;
    setActiveCameraIndex(nextIndex);
    await stopCamera();
    setTimeout(() => {
      initAndStartCamera();
    }, 200);
  };

  const handleScannedCode = (decodedText) => {
    if (!decodedText || typeof decodedText !== "string") return;
    const cleanCode = decodedText.trim();
    if (!cleanCode) return;

    // Debounce duplicate scans of the exact same code within 4 seconds
    const now = Date.now();
    if (
      lastScanRef.current.code === cleanCode &&
      now - lastScanRef.current.time < 4000
    ) {
      return;
    }
    lastScanRef.current = { code: cleanCode, time: now };

    handleVerify(cleanCode);
  };

  const handleVerify = async (payload) => {
    if (loading) return;
    setLoading(true);

    try {
      const res = await attendanceApi.scanQR({
        qr_payload: payload,
        qr_hash: payload,
        event_id: eventId ? Number(eventId) : null,
      });

      const participantName =
        res.participant_name || res.registration?.user?.full_name || "Participant";
      const eventTitle = res.event_title || res.event?.title || "Festival Event";
      const regNumber = res.registration?.registration_number || res.registration_id;

      setLastResult({
        status: "VALID",
        title: "ATTENDANCE CONFIRMED • ENTRY GRANTED",
        message: `Welcome, ${participantName}! Verified for gate admission.`,
        participant: participantName,
        email: res.participant_email || res.registration?.user?.email,
        event: eventTitle,
        regNumber: regNumber,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
      });

      // Notify parent page so attendance count, statistics, and audit table update instantly
      if (onScanSuccess) {
        onScanSuccess(res);
      }
    } catch (err) {
      console.error("QR Scan verification error:", err);
      const errData = err.response?.data;
      const detail = errData?.detail;
      const message =
        typeof detail === "string"
          ? detail
          : detail?.message || errData?.message || "Invalid or unrecognized ticket pass.";
      const participant = typeof detail === "object" ? detail?.participant_name : null;
      const eventTitle = typeof detail === "object" ? detail?.event_title : null;

      if (err.response?.status === 409) {
        setLastResult({
          status: "DUPLICATE",
          title: "DUPLICATE ENTRY DETECTED",
          message: message || "Duplicate entry attempt! Pass has already been used.",
          participant: participant || "Attendee",
          event: eventTitle || "",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        });
      } else {
        setLastResult({
          status: "INVALID",
          title: "ENTRY PASS REJECTED",
          message: message,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
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
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5 text-amber-400">
            <Scan className="w-5 h-5 text-amber-400" />
            <h3 className="text-lg font-bold text-white tracking-tight">
              Live Attendance QR Scanner
            </h3>
          </div>
          <div className="flex items-center gap-2">
            {cameras.length > 1 && (
              <button
                type="button"
                onClick={handleSwitchCamera}
                className="px-2.5 py-1 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors flex items-center gap-1.5 border border-slate-700"
                title="Switch Camera Device"
              >
                <SwitchCamera className="w-3.5 h-3.5 text-amber-400" />
                <span>Camera ({activeCameraIndex + 1}/{cameras.length})</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Camera Viewport (Single unified feed, no flex-row splitting) */}
        <div className="mt-5 flex flex-col items-center">
          <div
            id="qr-reader-container"
            className="w-full min-h-[260px] h-[300px] rounded-2xl overflow-hidden bg-black border border-slate-700 shadow-inner relative block"
          />

          {!scanning && (
            <div className="mt-3 text-xs text-amber-400/90 text-center flex items-center justify-center gap-1.5">
              <Camera className="w-3.5 h-3.5" />
              <span>Camera starting... If prompted, allow camera permissions in your browser.</span>
            </div>
          )}

          {scanning && (
            <p className="mt-2 text-[11px] text-slate-400 text-center">
              Align attendee QR ticket code within the square frame to automatically record gate attendance.
            </p>
          )}
        </div>

        {/* Scan Status / Result Banner */}
        {lastResult && (
          <div
            className={`mt-4 p-4 rounded-2xl border transition-all ${
              lastResult.status === "VALID"
                ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300"
                : lastResult.status === "DUPLICATE"
                ? "bg-amber-500/10 border-amber-500/40 text-amber-300"
                : "bg-rose-500/10 border-rose-500/40 text-rose-300"
            }`}
          >
            <div className="flex items-start gap-3">
              {lastResult.status === "VALID" && (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
              )}
              {lastResult.status === "DUPLICATE" && (
                <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
              )}
              {lastResult.status === "INVALID" && (
                <AlertCircle className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />
              )}

              <div className="flex-1">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-xs sm:text-sm font-black tracking-wide">
                    {lastResult.title || lastResult.message}
                  </h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950/60 border border-slate-800 text-slate-300 shrink-0">
                    {lastResult.time}
                  </span>
                </div>

                <p className="mt-1 text-xs text-slate-200">{lastResult.message}</p>

                {lastResult.participant && (
                  <p className="mt-1 text-xs text-slate-300">
                    Attendee: <strong className="font-semibold text-white">{lastResult.participant}</strong>
                    {lastResult.regNumber && (
                      <span className="font-mono text-[11px] text-slate-400 ml-1.5">
                        (#{lastResult.regNumber})
                      </span>
                    )}
                  </p>
                )}

                {lastResult.event && (
                  <p className="text-xs text-slate-400 mt-0.5">Event: {lastResult.event}</p>
                )}

                <div className="mt-2.5 flex items-center justify-end">
                  <button
                    type="button"
                    onClick={() => {
                      setLastResult(null);
                      lastScanRef.current = { code: "", time: 0 };
                    }}
                    className="px-3 py-1 rounded-lg text-xs font-bold bg-slate-800 hover:bg-slate-700 text-white transition-all flex items-center gap-1"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Scan Next Pass</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Manual Code Fallback */}
        <form onSubmit={handleManualSubmit} className="mt-5 pt-4 border-t border-slate-800">
          <label className="text-xs font-semibold text-slate-300 block mb-1">
            Manual Registration Number or Token Entry
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={manualCode}
              onChange={(e) => setManualCode(e.target.value)}
              placeholder="e.g. REG-001-A1B2C3 or pass token"
              className="flex-1 px-4 py-2.5 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
            <button
              type="submit"
              disabled={loading || !manualCode.trim()}
              className="px-4 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 transition-all shadow-md shadow-amber-500/20 cursor-pointer flex items-center gap-1.5 whitespace-nowrap"
            >
              {loading ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <>
                  <span>Validate</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QRScannerModal;
