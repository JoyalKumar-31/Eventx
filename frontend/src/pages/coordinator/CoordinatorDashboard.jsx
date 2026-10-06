import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Calendar,
  Users,
  QrCode,
  Trophy,
  PlusCircle,
  ScanLine,
  Eye,
  Edit,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import { eventApi } from "../../api/eventApi";
import { adminApi } from "../../api/adminApi";
import StatCard from "../../components/StatCard";
import StatusBadge from "../../components/StatusBadge";
import QRScannerModal from "../../components/QRScannerModal";

export default function CoordinatorDashboard() {
  const { user } = useAuth();
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showScanner, setShowScanner] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [eventsData, metricsData] = await Promise.all([
        eventApi.getMyCoordinatedEvents().catch(() => []),
        adminApi.getCoordinatorMetrics().catch(() => null),
      ]);
      setEvents(eventsData || []);
      setMetrics(metricsData);
    } catch (err) {
      console.error("Failed to load coordinator data", err);
    } finally {
      setLoading(false);
    }
  };

  const totalRegistrations = events.reduce(
    (acc, e) => acc + (e.registrations?.length || 0),
    0
  );

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-900/50 via-slate-900 to-slate-900 p-6 sm:p-8 border border-blue-500/20 shadow-2xl">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs font-semibold uppercase tracking-wider">
            Coordinator Hub
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Festival Operations & Management
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Configure competitive events, upload cover imagery, monitor participant check-ins via QR scanner, and publish official leaderboards.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/coordinator/events?action=new"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition-all shadow-lg shadow-blue-600/30"
            >
              <PlusCircle className="w-4 h-4" /> Create New Event
            </Link>
            <button
              onClick={() => setShowScanner(true)}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-all border border-slate-700"
            >
              <ScanLine className="w-4 h-4 text-emerald-400" /> Launch Gate Scanner
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Assigned Events"
          value={metrics?.total_events ?? events.length}
          subtitle="Events under your control"
          icon={Calendar}
          color="blue"
        />
        <StatCard
          title="Total Registrations"
          value={metrics?.total_registrations ?? totalRegistrations}
          subtitle="Enrolled participants & teams"
          icon={Users}
          color="indigo"
        />
        <StatCard
          title="Gate Attendance"
          value={metrics?.total_attendance ?? 0}
          subtitle="Total scanned check-ins"
          icon={QrCode}
          color="emerald"
        />
        <StatCard
          title="Published Results"
          value={metrics?.published_results ?? 0}
          subtitle="Official standings"
          icon={Trophy}
          color="amber"
        />
      </div>

      {/* Events Table */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-lg">My Coordinated Events</h3>
            <p className="text-xs text-slate-400 mt-0.5">Manage event details, images, venues, and status</p>
          </div>
          <Link
            to="/coordinator/events"
            className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
          >
            Manage All ({events.length}) →
          </Link>
        </div>

        {loading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-slate-950 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="p-8 text-center space-y-3">
            <Calendar className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">You haven't created any events yet.</p>
            <Link
              to="/coordinator/events?action=new"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-all"
            >
              Create Your First Event
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {events.map((evt) => (
              <div
                key={evt.id}
                className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-800/40 transition-colors"
              >
                <div className="flex items-center gap-4">
                  {evt.primary_media_url ? (
                    <img
                      src={evt.primary_media_url}
                      alt={evt.title}
                      className="w-14 h-14 rounded-xl object-cover border border-slate-800 shrink-0"
                    />
                  ) : (
                    <div className="w-14 h-14 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-500 shrink-0">
                      <Calendar className="w-6 h-6" />
                    </div>
                  )}

                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold text-white hover:text-blue-400 transition-colors">
                        <Link to={`/events/${evt.id}`}>{evt.title}</Link>
                      </span>
                      <StatusBadge status={evt.status} />
                    </div>
                    <div className="text-xs text-slate-400 flex flex-wrap items-center gap-3">
                      <span>Category: <strong className="text-slate-300">{evt.category?.name || "General"}</strong></span>
                      <span>Format: <strong className="text-slate-300">{evt.event_format}</strong></span>
                      <span>Regs: <strong className="text-blue-400">{evt.registrations?.length || 0}</strong></span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  <Link
                    to={`/coordinator/events?edit=${evt.id}`}
                    className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all text-xs flex items-center gap-1.5"
                    title="Edit Event & Visuals"
                  >
                    <Edit className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </Link>
                  <Link
                    to={`/coordinator/participants?event_id=${evt.id}`}
                    className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all text-xs flex items-center gap-1.5"
                    title="View Participants"
                  >
                    <Users className="w-3.5 h-3.5" />
                    <span>Attendees</span>
                  </Link>
                  <Link
                    to={`/coordinator/results?event_id=${evt.id}`}
                    className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-400 hover:text-amber-300 transition-all text-xs flex items-center gap-1.5"
                    title="Judging & Leaderboard"
                  >
                    <Trophy className="w-3.5 h-3.5" />
                    <span>Results</span>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* QR Scanner Modal */}
      {showScanner && (
        <QRScannerModal
          isOpen={showScanner}
          onClose={() => setShowScanner(false)}
          onScanSuccess={() => {
            fetchDashboardData();
          }}
        />
      )}
    </div>
  );
}
