import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Calendar,
  Users,
  QrCode,
  Award,
  CreditCard,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Clock,
  ExternalLink,
} from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import { registrationApi } from "../../api/registrationApi";
import { teamApi } from "../../api/teamApi";
import { certificateApi } from "../../api/certificateApi";
import { eventApi } from "../../api/eventApi";
import StatCard from "../../components/StatCard";
import StatusBadge from "../../components/StatusBadge";
import QRPassModal from "../../components/QRPassModal";
import EventCard from "../../components/EventCard";

export default function StudentDashboard() {
  const { user } = useAuth();
  const [registrations, setRegistrations] = useState([]);
  const [teams, setTeams] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [availableEvents, setAvailableEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPassRegId, setSelectedPassRegId] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [regsData, teamsData, certsData, eventsData] = await Promise.all([
        registrationApi.getMyRegistrations().catch(() => []),
        teamApi.getMyTeams().catch(() => []),
        certificateApi.getMyCertificates().catch(() => []),
        eventApi.getEvents({ limit: 12 }).catch(() => []),
      ]);
      setRegistrations(regsData || []);
      setTeams(teamsData || []);
      setCertificates(certsData || []);
      setAvailableEvents(eventsData || []);
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  const pendingPayments = registrations.filter(
    (r) => r.status === "PENDING" && r.payment_status === "UNPAID"
  );
  const confirmedRegistrations = registrations.filter(
    (r) => r.status === "CONFIRMED" || r.payment_status === "PAID"
  );

  return (
    <div className="space-y-8">
      {/* Welcome Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-900/60 via-slate-900 to-slate-900 p-6 sm:p-8 border border-indigo-500/20 shadow-2xl">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> Student Fest Portal
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Welcome back, {user?.full_name?.split(" ")[0] || "Student"}! 🚀
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Manage your registered events, access instant QR entry passes, coordinate with your teams, and download verified certificates.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/events"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-all shadow-lg shadow-indigo-600/30"
            >
              Explore Events <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/student/passes"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-all"
            >
              <QrCode className="w-4 h-4 text-indigo-400" /> My QR Passes
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Registrations"
          value={registrations.length}
          subtitle="Events entered"
          icon={Calendar}
          color="indigo"
        />
        <StatCard
          title="Active Teams"
          value={teams.length}
          subtitle="Squads joined"
          icon={Users}
          color="emerald"
        />
        <StatCard
          title="Confirmed Passes"
          value={confirmedRegistrations.length}
          subtitle="Ready for entry"
          icon={QrCode}
          color="amber"
        />
        <StatCard
          title="Certificates"
          value={certificates.length}
          subtitle="Issued credentials"
          icon={Award}
          color="purple"
        />
      </div>

      {/* My Fest Journey Tracker */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400" /> My Fest Progress Tracker
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400">Step 1</span>
              {registrations.length > 0 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <Clock className="w-4 h-4 text-slate-600" />
              )}
            </div>
            <div className="font-semibold text-white text-sm">Register for Events</div>
            <p className="text-xs text-slate-400">{registrations.length} events registered</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400">Step 2</span>
              {teams.length > 0 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <Clock className="w-4 h-4 text-slate-600" />
              )}
            </div>
            <div className="font-semibold text-white text-sm">Join / Create Team</div>
            <p className="text-xs text-slate-400">{teams.length} teams connected</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400">Step 3</span>
              {confirmedRegistrations.length > 0 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <Clock className="w-4 h-4 text-slate-600" />
              )}
            </div>
            <div className="font-semibold text-white text-sm">QR Gate Pass</div>
            <p className="text-xs text-slate-400">{confirmedRegistrations.length} passes ready</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400">Step 4</span>
              {certificates.length > 0 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <Clock className="w-4 h-4 text-slate-600" />
              )}
            </div>
            <div className="font-semibold text-white text-sm">Certificates</div>
            <p className="text-xs text-slate-400">{certificates.length} credentials earned</p>
          </div>
        </div>
      </div>

      {/* Action Required: Pending Payments Banner */}
      {pendingPayments.length > 0 && (
        <div className="p-5 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <CreditCard className="w-6 h-6 text-amber-400 shrink-0" />
            <div>
              <h4 className="text-sm font-bold text-white">
                You have {pendingPayments.length} pending registration payment(s)
              </h4>
              <p className="text-xs text-amber-300/80">
                Complete your checkout to confirm your entry pass and secure your team slot.
              </p>
            </div>
          </div>
          <Link
            to="/student/registrations"
            className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-all whitespace-nowrap"
          >
            Complete Payment
          </Link>
        </div>
      )}

      {/* Live Fest Events / Competitions Open for Registration */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" /> Live Campus Events & Tournaments
            </h3>
            <p className="text-xs text-slate-400">
              Explore competitions created by fest coordinators and register with 1 click.
            </p>
          </div>
          <Link
            to="/events"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors"
          >
            Explore All ({availableEvents.length}) <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 bg-slate-900/60 border border-slate-800 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : availableEvents.length === 0 ? (
          <div className="p-8 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-2">
            <Calendar className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">No events currently open for registration.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {availableEvents.slice(0, 6).map((evt) => {
              const isRegistered = registrations.some((r) => r.event_id === evt.id);
              return (
                <EventCard
                  key={evt.id}
                  event={evt}
                  isRegistered={isRegistered}
                  registrationStatus={isRegistered ? "CONFIRMED" : null}
                />
              );
            })}
          </div>
        )}
      </div>

      {/* Recent Registrations Table */}
      <div className="rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-white text-base">My Recent Registrations</h3>
          <Link
            to="/student/registrations"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            View All ({registrations.length}) →
          </Link>
        </div>

        {loading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-slate-950 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : registrations.length === 0 ? (
          <div className="p-8 text-center space-y-3">
            <Calendar className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">You haven't registered for any events yet.</p>
            <Link
              to="/events"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all"
            >
              Browse Event Catalog
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {registrations.slice(0, 5).map((reg) => (
              <div
                key={reg.id}
                className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/40 transition-colors"
              >
                <div>
                  <div className="text-sm font-bold text-white hover:text-indigo-400">
                    <Link to={`/events/${reg.event_id}`}>{reg.event?.title || `Event #${reg.event_id}`}</Link>
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-3">
                    <span>Format: {reg.event?.event_format || "SOLO"}</span>
                    {reg.team && (
                      <span className="text-indigo-300">Team: {reg.team.name}</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center">
                  <StatusBadge status={reg.status} />
                  <button
                    onClick={() => setSelectedPassRegId(reg.id)}
                    className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all text-xs font-medium flex items-center gap-1.5"
                    title="View QR Pass"
                  >
                    <QrCode className="w-4 h-4 text-indigo-400" />
                    <span>Pass</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* QR Pass Modal */}
      {selectedPassRegId && (
        <QRPassModal
          registrationId={selectedPassRegId}
          onClose={() => setSelectedPassRegId(null)}
        />
      )}
    </div>
  );
}
