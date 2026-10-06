import React, { useState, useEffect } from "react";
import { BarChart3, TrendingUp, Users, QrCode, DollarSign, Calendar } from "lucide-react";
import { adminApi } from "../../api/adminApi";
import { eventApi } from "../../api/eventApi";
import StatCard from "../../components/StatCard";

export default function CoordinatorAnalyticsPage() {
  const [metrics, setMetrics] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [m, evts] = await Promise.all([
        adminApi.getCoordinatorMetrics().catch(() => null),
        eventApi.getMyCoordinatedEvents().catch(() => []),
      ]);
      setMetrics(m);
      setEvents(evts || []);
    } catch (err) {
      console.error("Failed to load analytics", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Operational Analytics & Turnout
        </h1>
        <p className="text-slate-400 text-sm">
          Real-time aggregated metrics across attendance rates, registration volume, and event engagement.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Events"
          value={metrics?.total_events ?? events.length}
          subtitle="Managed in dashboard"
          icon={Calendar}
          color="blue"
        />
        <StatCard
          title="Total Registrations"
          value={metrics?.total_registrations ?? 0}
          subtitle="Participants enrolled"
          icon={Users}
          color="indigo"
        />
        <StatCard
          title="Total Attendance"
          value={metrics?.total_attendance ?? 0}
          subtitle="Verified check-ins"
          icon={QrCode}
          color="emerald"
        />
        <StatCard
          title="Published Results"
          value={metrics?.published_results ?? 0}
          subtitle="Competitions completed"
          icon={TrendingUp}
          color="amber"
        />
      </div>

      {/* Per Event Breakdown */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
        <div className="border-b border-slate-800 pb-4">
          <h3 className="font-bold text-white text-lg">Event-by-Event Turnout & Capacity</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Monitor real-time conversion from registration to gate attendance
          </p>
        </div>

        {events.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No event data available yet.</p>
        ) : (
          <div className="space-y-6">
            {events.map((evt) => {
              const regCount = evt.registrations?.length || 0;
              const maxCap = evt.max_participants || 100;
              const capPercent = Math.min(Math.round((regCount / maxCap) * 100), 100);

              return (
                <div key={evt.id} className="space-y-2 p-4 rounded-2xl bg-slate-950 border border-slate-800/80">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <span className="font-bold text-white text-sm">{evt.title}</span>
                    <span className="text-xs font-mono text-slate-400">
                      {regCount} / {maxCap} Registrations ({capPercent}% Cap)
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-600 to-indigo-500 rounded-full transition-all duration-500"
                      style={{ width: `${capPercent}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                    <span>Format: {evt.event_format}</span>
                    <span>Fee: ₹{evt.registration_fee}</span>
                    <span>Status: {evt.status}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
