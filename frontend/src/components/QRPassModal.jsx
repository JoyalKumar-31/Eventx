import React, { useState, useEffect, useRef } from "react";
import { X, Download, Printer, ShieldCheck, MapPin, Calendar, Clock, User } from "lucide-react";
import { registrationApi } from "../api/registrationApi";

export const QRPassModal = ({
  isOpen = true,
  onClose,
  passData: initialPassData = null,
  registrationId = null,
}) => {
  const [passData, setPassData] = useState(initialPassData);
  const [loading, setLoading] = useState(false);
  const passRef = useRef(null);

  useEffect(() => {
    if (registrationId && !initialPassData) {
      setLoading(true);
      registrationApi
        .getQREntryPass(registrationId)
        .then((res) => setPassData(res))
        .catch((err) => console.error("Failed to load pass", err))
        .finally(() => setLoading(false));
    } else if (initialPassData) {
      setPassData(initialPassData);
    }
  }, [registrationId, initialPassData]);

  if (isOpen === false) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    if (!passData?.qr_image_base64) return;
    const a = document.createElement("a");
    a.href = passData.qr_image_base64;
    a.download = `QR_Pass_${passData.registration_number || registrationId}.png`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const dateStr = passData?.start_time
    ? new Date(passData.start_time).toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "TBA";

  const timeStr = passData?.start_time
    ? new Date(passData.start_time).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "TBA";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-md rounded-3xl border border-slate-700 bg-slate-900 p-6 md:p-8 shadow-2xl my-8">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2 text-indigo-400">
            <ShieldCheck className="w-5 h-5" />
            <h3 className="text-lg font-bold text-white">Official Entry Pass</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="py-16 text-center space-y-3">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs text-slate-400">Generating Cryptographic Entry Pass...</p>
          </div>
        ) : !passData ? (
          <div className="py-12 text-center text-xs text-slate-400">
            Pass not found or not yet approved.
          </div>
        ) : (
          <>
            {/* Digital Ticket Pass Card */}
            <div
              ref={passRef}
              className="mt-6 rounded-2xl border-2 border-dashed border-indigo-500/40 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 p-6 shadow-inner text-center"
            >
              <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {passData.registration_number || `REG-#${registrationId}`}
              </div>

              <h2 className="mt-3 text-xl font-extrabold text-white tracking-tight">
                {passData.event_title}
              </h2>

              {/* QR Code Container */}
              <div className="my-5 flex justify-center">
                <div className="p-3 bg-white rounded-2xl shadow-xl border-4 border-slate-800">
                  <img
                    src={passData.qr_image_base64}
                    alt="Ticket QR Code"
                    className="w-48 h-48 object-contain"
                  />
                </div>
              </div>

              <p className="text-xs text-slate-400">
                Present this QR code at the entrance scanner for venue admission.
              </p>

              {/* Ticket Metadata Roster */}
              <div className="mt-5 space-y-2 border-t border-slate-800/80 pt-4 text-xs text-left text-slate-300">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-indigo-400" />
                    Participant
                  </span>
                  <span className="font-semibold text-white">{passData.participant_name}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                    Date & Time
                  </span>
                  <span>
                    {dateStr} • {timeStr}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                    Venue
                  </span>
                  <span>
                    {passData.venue_name || "Campus"} ({passData.venue_building || "Main"})
                  </span>
                </div>
              </div>
            </div>

            {/* Modal CTAs */}
            <div className="mt-6 flex items-center gap-3">
              <button
                onClick={handleDownload}
                className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/20 cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Download Pass</span>
              </button>
              <button
                onClick={handlePrint}
                className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
              >
                <Printer className="w-4 h-4" />
                <span>Print</span>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default QRPassModal;
