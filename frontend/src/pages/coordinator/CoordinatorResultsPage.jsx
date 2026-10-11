import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Trophy,
  Award,
  Globe,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Users,
  Medal,
  Sparkles,
  RefreshCw,
  Sliders,
  MessageSquare,
} from "lucide-react";
import { eventApi } from "../../api/eventApi";
import { judgeApi } from "../../api/judgeApi";
import EmptyState from "../../components/EmptyState";

export default function CoordinatorResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlEventId = searchParams.get("event_id");

  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(urlEventId || "");
  const [leaderboard, setLeaderboard] = useState([]);
  const [publicResults, setPublicResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      loadResultsData(Number(selectedEventId));
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

  const loadResultsData = async (eventId) => {
    try {
      const [lb, pub] = await Promise.all([
        judgeApi.getLeaderboard(eventId).catch(() => []),
        judgeApi.getPublicResults(eventId).catch(() => []),
      ]);
      setLeaderboard(lb || []);
      setPublicResults(pub || []);
    } catch (err) {
      console.error("Failed to load results", err);
    }
  };

  const handlePublish = async () => {
    if (!selectedEventId) return;
    if (
      !window.confirm(
        "Are you sure you want to finalize and publish results? This will compute official ranks, issue digital certificates, and notify all participants."
      )
    ) {
      return;
    }

    try {
      setPublishing(true);
      setFeedback(null);
      await judgeApi.publishResults(Number(selectedEventId));
      setFeedback({
        type: "success",
        text: "Results finalized & published! Certificates generated for all participants.",
      });
      loadResultsData(Number(selectedEventId));
    } catch (err) {
      console.error("Failed to publish results", err);
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || "Could not publish results.",
      });
    } finally {
      setPublishing(false);
    }
  };

  const isPublished = publicResults.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Leaderboard, Ranks & Result Publishing
          </h1>
          <p className="text-slate-400 text-sm">
            Review live judge scores, auto-compute ranks, and publish official winner standings.
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

      {feedback && (
        <div
          className={`p-4 rounded-xl text-xs font-semibold flex items-center justify-between ${
            feedback.type === "success"
              ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-300"
              : "bg-rose-500/10 border border-rose-500/30 text-rose-300"
          }`}
        >
          <span>{feedback.text}</span>
          <button onClick={() => setFeedback(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Control Banner */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                isPublished
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
              }`}
            >
              {isPublished ? "Official Results: Published" : "Draft / In Review"}
            </span>
          </div>
          <p className="text-xs text-slate-400">
            {isPublished
              ? "Winners are publicly listed on the fest results page and digital certificates are live."
              : "Scores are currently being tabulated. Review standings below before publishing."}
          </p>
        </div>

        <button
          onClick={handlePublish}
          disabled={publishing || leaderboard.length === 0}
          className="px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold text-xs transition-all flex items-center gap-2 shadow-lg shadow-amber-500/20 whitespace-nowrap"
        >
          <Sparkles className="w-4 h-4" />
          {publishing
            ? "Publishing & Issuing Certs..."
            : isPublished
            ? "Re-calculate & Update Standings"
            : "Finalize & Publish Results"}
        </button>
      </div>

      {/* Leaderboard Table */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <Trophy className="w-4 h-4 text-amber-400" />
            Tabulated Standings (Ranked by Total Score)
          </h3>
          <div className="flex items-center gap-3">
            <button
              onClick={async () => {
                if (selectedEventId) {
                  setRefreshing(true);
                  await loadResultsData(Number(selectedEventId));
                  setRefreshing(false);
                }
              }}
              disabled={refreshing}
              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 hover:text-white font-semibold transition-all flex items-center gap-1.5 border border-slate-700"
              title="Fetch latest scores submitted by judges"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-amber-400" : ""}`} />
              {refreshing ? "Syncing Scores..." : "Refresh Scores"}
            </button>
            <span className="text-xs font-mono text-slate-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
              {leaderboard.length} Scored Submissions
            </span>
          </div>
        </div>

        {leaderboard.length === 0 ? (
          <EmptyState
            icon={Trophy}
            title="No Scored Submissions Yet"
            description="Judges haven't submitted evaluation scores for participants of this event yet."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Rank</th>
                  <th className="px-6 py-4">Participant / Team</th>
                  <th className="px-6 py-4">Reg ID</th>
                  <th className="px-6 py-4">Rubric Criteria & Notes</th>
                  <th className="px-6 py-4 text-right">Total Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {leaderboard.map((item) => (
                  <tr key={item.registration_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-sm align-top">
                      {item.rank === 1 ? (
                        <span className="inline-flex items-center gap-1.5 text-amber-400">
                          <Trophy className="w-4 h-4" /> 1st Place
                        </span>
                      ) : item.rank === 2 ? (
                        <span className="inline-flex items-center gap-1.5 text-slate-200">
                          <Medal className="w-4 h-4" /> 2nd Place
                        </span>
                      ) : item.rank === 3 ? (
                        <span className="inline-flex items-center gap-1.5 text-amber-600">
                          <Award className="w-4 h-4" /> 3rd Place
                        </span>
                      ) : (
                        <span className="text-slate-400">#{item.rank}</span>
                      )}
                    </td>
                    <td className="px-6 py-4 align-top">
                      <div className="font-bold text-white text-sm">
                        {item.participant_name}
                      </div>
                      {item.team_name && (
                        <div className="text-[11px] text-indigo-300 flex items-center gap-1 mt-0.5">
                          <Users className="w-3 h-3" /> Team: {item.team_name}
                        </div>
                      )}
                      {item.participant_email && (
                        <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                          {item.participant_email}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 font-mono text-slate-400 align-top">
                      #{item.registration_number || item.registration_id}
                    </td>
                    <td className="px-6 py-4 space-y-2 align-top">
                      {item.scores_by_criteria && Object.keys(item.scores_by_criteria).length > 0 ? (
                        <div className="flex flex-wrap gap-1.5">
                          {Object.entries(item.scores_by_criteria).map(([critName, val]) => (
                            <span
                              key={critName}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800 text-[10px] text-slate-300 font-mono"
                            >
                              <span>{critName}:</span>
                              <strong className="text-amber-400">{val}</strong>
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-500 italic text-[11px]">No rubric breakdown available</span>
                      )}

                      {item.judges && item.judges.length > 0 && (
                        <div className="text-[10px] text-slate-400">
                          Scored by: <strong className="text-slate-200">{item.judges.join(", ")}</strong>
                        </div>
                      )}

                      {item.remarks && (
                        <div className="text-[11px] text-slate-300 italic bg-slate-950/70 p-2 rounded-xl border border-slate-800/80 flex items-start gap-1.5">
                          <MessageSquare className="w-3 h-3 text-amber-400 mt-0.5 shrink-0" />
                          <span>"{item.remarks}"</span>
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-black text-white text-base align-top">
                      <span className="text-amber-400">{Number(item.total_score).toFixed(1)}</span>{" "}
                      <span className="text-slate-500 text-xs font-normal">pts</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
