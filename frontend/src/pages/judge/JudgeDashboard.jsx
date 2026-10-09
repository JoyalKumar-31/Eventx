import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Gavel, CheckCircle2, Clock, Calendar, ArrowRight, Award, Sparkles } from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import { judgeApi } from "../../api/judgeApi";
import { adminApi } from "../../api/adminApi";
import StatCard from "../../components/StatCard";

export default function JudgeDashboard() {
  const { user } = useAuth();
  const [assignedEvents, setAssignedEvents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJudgeData();
  }, []);

  const fetchJudgeData = async () => {
    try {
      setLoading(true);
      const [eventsData, metricsData] = await Promise.all([
        judgeApi.getMyAssignedEvents().catch(() => []),
        adminApi.getJudgeMetrics().catch(() => null),
      ]);
      setAssignedEvents(eventsData || []);
      setMetrics(metricsData);
    } catch (err) {
      console.error("Failed to load judge data", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-900 p-6 sm:p-8 border border-amber-500/20 shadow-2xl">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-semibold uppercase tracking-wider">
            <Gavel className="w-3.5 h-3.5" /> Adjudication Desk
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Welcome, Judge {user?.full_name?.split(" ")[0] || "Evaluator"} ⚖️
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Review your assigned competitive events, grade submissions using weighted rubric criteria, and evaluate leaderboards.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/judge/scoring"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-all shadow-lg shadow-amber-500/20"
            >
              <Gavel className="w-4 h-4" /> Start Evaluation
            </Link>
            <Link
              to="/judge/rankings"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-all border border-slate-700"
            >
              <Award className="w-4 h-4 text-amber-400" /> View Leaderboard
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard
          title="Assigned Events"
          value={metrics?.total_assigned_events ?? assignedEvents.length}
          subtitle="Tracks under your jury"
          icon={Calendar}
          color="amber"
        />
        <StatCard
          title="Scores Submitted"
          value={metrics?.scores_submitted ?? 0}
          subtitle="Participant evaluations"
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Average Score"
          value={metrics?.average_score != null ? `${Number(metrics.average_score).toFixed(1)} pts` : "N/A"}
          subtitle="Awarded per evaluation"
          icon={Gavel}
          color="purple"
        />
      </div>

      {/* Assigned Events Roster */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-lg">My Assigned Events</h3>
            <p className="text-xs text-slate-400 mt-0.5">Events where you are authorized to score</p>
          </div>
          <Link
            to="/judge/events"
            className="text-xs font-semibold text-amber-400 hover:text-amber-300 transition-colors"
          >
            View All ({assignedEvents.length}) →
          </Link>
        </div>

        {loading ? (
          <div className="p-6 space-y-3">
            {[1, 2].map((i) => (
              <div key={i} className="h-16 bg-slate-950 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : assignedEvents.length === 0 ? (
          <div className="p-8 text-center space-y-3">
            <Gavel className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">You have no events assigned yet.</p>
            <p className="text-xs text-slate-500">
              The fest coordinator will assign you to judging panels soon.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {assignedEvents.map((item) => {
              const evt = item.event || item;
              return (
                <div
                  key={item.id}
                  className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-800/40 transition-colors"
                >
                  <div>
                    <h4 className="text-base font-bold text-white hover:text-amber-400 transition-colors">
                      <Link to={`/events/${evt?.id}`}>{evt?.title}</Link>
                    </h4>
                    <div className="text-xs text-slate-400 flex items-center gap-3 mt-1">
                      <span>Category: <strong className="text-slate-200">{evt?.category?.name || "General"}</strong></span>
                      <span>Format: <strong className="text-slate-200">{evt?.is_team_event ? "Team" : "Solo"}</strong></span>
                      <span>Enrolled: <strong className="text-amber-400">{evt?.current_participants ?? evt?.registrations?.length ?? 0}</strong></span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-center">
                    <Link
                      to={`/judge/scoring?event_id=${evt?.id}`}
                      className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-all flex items-center gap-1.5 shadow-md shadow-amber-500/20"
                    >
                      <Gavel className="w-4 h-4" /> Score Now
                    </Link>
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
