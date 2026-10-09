import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  ScanLine,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Users,
  Search,
  Camera,
  Keyboard,
  ShieldCheck,
} from "lucide-react";
import { eventApi } from "../../api/eventApi";
import { attendanceApi } from "../../api/attendanceApi";
import QRScannerModal from "../../components/QRScannerModal";
import EmptyState from "../../components/EmptyState";

export default function CoordinatorAttendancePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlEventId = searchParams.get("event_id");

  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(urlEventId || "");
  const [attendances, setAttendances] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Scanner modal & Manual input
  const [showScannerModal, setShowScannerModal] = useState(false);
  const [manualCode, setManualCode] = useState("");
  const [manualSubmitting, setManualSubmitting] = useState(false);
  const [scanResult, setScanResult] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      loadAttendanceData(Number(selectedEventId));
    }
  }, [selectedEventId]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const data = await eventApi.getMyCoordinatedEvents();
      setEvents(data || []);
      if (!selectedEventId && data && data.length > 0) {
        setSelectedEventId(String(data[0].id));
      }
    } catch (err) {
      console.error("Failed to load events", err);
    } finally {
      setLoading(false);
    }
  };

  const loadAttendanceData = async (eventId) => {
    try {
      const [attList, attStats] = await Promise.all([
        attendanceApi.getEventAttendance(eventId).catch(() => []),
        attendanceApi.getEventAttendanceStats(eventId).catch(() => null),
      ]);
      setAttendances(attList || []);
      setStats(attStats);
    } catch (err) {
      console.error("Failed to load attendance", err);
    }
  };

  const handleManualScan = async (e) => {
    e.preventDefault();
    if (!manualCode.trim() || !selectedEventId) return;
    try {
      setManualSubmitting(true);
      setScanResult(null);
      const res = await attendanceApi.scanQR({
        qr_payload: manualCode.trim(),
        qr_hash: manualCode.trim(),
        event_id: Number(selectedEventId),
      });
      setScanResult({
        type: "success",
        title: "ACCESS GRANTED",
        message: `Welcome, ${res.participant_name || "Participant"}!`,
        regId: res.registration_id,
      });
      setManualCode("");
      loadAttendanceData(Number(selectedEventId));
    } catch (err) {
      console.error("Manual scan error", err);
      const status = err.response?.status;
      const detail = err.response?.data?.detail || "Scan verification failed.";
      if (status === 409) {
        setScanResult({
          type: "warning",
          title: "DUPLICATE ENTRY DETECTED",
          message: detail,
        });
      } else {
        setScanResult({
          type: "error",
          title: "ENTRY DENIED",
          message: detail,
        });
      }
    } finally {
      setManualSubmitting(false);
    }
  };

  const attendanceRate =
    stats && stats.total_registrations > 0
      ? Math.round((stats.total_attended / stats.total_registrations) * 100)
      : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Gate Attendance & QR Scanner
          </h1>
          <p className="text-slate-400 text-sm">
            Scan digital ticket barcodes with camera, verify passes, and prevent duplicate entry.
          </p>
        </div>

        {/* Event selector */}
        <div className="w-full sm:w-72">
          <select
            value={selectedEventId}
            onChange={(e) => {
              setSelectedEventId(e.target.value);
              setSearchParams({ event_id: e.target.value });
            }}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
          >
            {events.map((evt) => (
              <option key={evt.id} value={evt.id}>
                {evt.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Top Banner Actions & Live Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scanner Launch Card */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-gradient-to-r from-blue-900/50 via-slate-900 to-slate-900 border border-blue-500/30 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
              <Camera className="w-3.5 h-3.5" /> High-Speed Check-In
            </span>
            <h3 className="text-xl font-bold text-white">Live Camera QR Scanner</h3>
            <p className="text-xs text-slate-300">
              Launch device camera to scan attendee QR passes continuously with millisecond latency.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => setShowScannerModal(true)}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition-all flex items-center gap-2 shadow-lg shadow-blue-600/30"
            >
              <ScanLine className="w-4 h-4" /> Launch Camera Scanner
            </button>
          </div>
        </div>

        {/* Stats Card */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 flex flex-col justify-between space-y-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Attendance Rate
          </h4>
          <div>
            <div className="text-4xl font-black text-white font-mono">{attendanceRate}%</div>
            <p className="text-xs text-slate-400 mt-1">
              <strong className="text-emerald-400">{stats?.total_attended || attendances.length}</strong> checked in of{" "}
              <strong className="text-white">{stats?.total_registrations || 0}</strong> registered
            </p>
          </div>
          {/* Progress bar */}
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-emerald-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(attendanceRate, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Manual Code Input & Scan Feedback */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Keyboard className="w-4 h-4 text-emerald-400" /> Manual Code / QR Hash Check-In
        </h3>

        <form onSubmit={handleManualScan} className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Paste QR Ticket Hash or Code (e.g. 5f8a9e...)"
            value={manualCode}
            onChange={(e) => setManualCode(e.target.value)}
            className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={manualSubmitting || !manualCode.trim()}
            className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs transition-all whitespace-nowrap shadow-md shadow-emerald-600/20"
          >
            {manualSubmitting ? "Validating..." : "Verify & Check-In"}
          </button>
        </form>

        {/* Scan Result Feedback banner */}
        {scanResult && (
          <div
            className={`p-4 rounded-2xl flex items-center justify-between text-xs font-semibold ${
              scanResult.type === "success"
                ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-300"
                : scanResult.type === "warning"
                ? "bg-amber-500/10 border border-amber-500/30 text-amber-300"
                : "bg-rose-500/10 border border-rose-500/30 text-rose-300"
            }`}
          >
            <div className="flex items-center gap-2.5">
              {scanResult.type === "success" ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
              ) : scanResult.type === "warning" ? (
                <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />
              ) : (
                <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
              )}
              <div>
                <strong className="block text-white text-sm">{scanResult.title}</strong>
                <span>{scanResult.message}</span>
              </div>
            </div>
            <button
              onClick={() => setScanResult(null)}
              className="text-slate-400 hover:text-white"
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* Attendance Check-in Log Table */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-white text-sm">Gate Check-in Audit Logs</h3>
          <span className="text-xs text-slate-400 font-mono">
            {attendances.length} scans recorded
          </span>
        </div>

        {attendances.length === 0 ? (
          <EmptyState
            icon={ScanLine}
            title="No Attendance Logs Yet"
            description="Participants checked in at the gate will appear here in real time."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Attendee Name</th>
                  <th className="px-6 py-4">Reg ID</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Scanned At</th>
                  <th className="px-6 py-4">Method</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {attendances.map((att) => (
                  <tr key={att.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-white">
                      {att.participant_name || att.registration?.user?.full_name || "Participant"}
                    </td>
                    <td className="px-6 py-4 font-mono text-slate-400">
                      #{att.registration_id}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> Valid Entry
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {new Date(att.scanned_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      })}
                    </td>
                    <td className="px-6 py-4 text-slate-400 font-mono text-[11px]">
                      {att.scan_method || "CAMERA_QR"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Camera QR Scanner Modal */}
      {showScannerModal && (
        <QRScannerModal
          isOpen={showScannerModal}
          eventId={Number(selectedEventId)}
          onClose={() => setShowScannerModal(false)}
          onScanSuccess={() => {
            if (selectedEventId) {
              loadAttendanceData(Number(selectedEventId));
            }
          }}
        />
      )}
    </div>
  );
}
