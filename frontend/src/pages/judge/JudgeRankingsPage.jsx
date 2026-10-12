import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Trophy, Award, Medal, Users, Gavel } from "lucide-react";
import { judgeApi } from "../../api/judgeApi";
import EmptyState from "../../components/EmptyState";

export default function JudgeRankingsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlEventId = searchParams.get("event_id");

  const [assignedEvents, setAssignedEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(urlEventId || "");
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssigned();
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      loadLeaderboard(Number(selectedEventId));
    }
  }, [selectedEventId]);

  const fetchAssigned = async () => {
    try {
      setLoading(true);
      const data = await judgeApi.getMyAssignedEvents();
      setAssignedEvents(data || []);
      if (!selectedEventId && data && data.length > 0) {
        setSelectedEventId(String(data[0].id || data[0].event_id));
      }
    } catch (err) {
      console.error("Failed to load assigned events", err);
    } finally {
      setLoading(false);
    }
  };

  const loadLeaderboard = async (eventId) => {
    try {
      const data = await judgeApi.getLeaderboard(eventId);
      setLeaderboard(data || []);
    } catch (err) {
      console.error("Failed to load leaderboard", err);
    }
  };

  const [publishing, setPublishing] = useState(false);
  const [publishSuccess, setPublishSuccess] = useState(null);

  const selectedEvent = assignedEvents.find(
    (a) => String(a.id || a.event_id) === String(selectedEventId)
  );

  const handleFinalizeAndComplete = async () => {
    if (!selectedEventId) return;
    if (!window.confirm("Submit final results and complete this event? This will finalize standings, issue certificates, and mark the event COMPLETED.")) return;
    try {
      setPublishing(true);
      await judgeApi.publishResults(Number(selectedEventId));
      setPublishSuccess("Official results submitted & event marked COMPLETED!");
      await fetchAssigned();
      await loadLeaderboard(Number(selectedEventId));
    } catch (err) {
      console.error("Failed to publish results", err);
      alert(err.response?.data?.detail || "Failed to submit results.");
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Event Standings & Score Breakdown
          </h1>
          <p className="text-slate-400 text-sm">
            Review live tabulated leaderboard across your assigned jury panels.
          </p>
        </div>

        {/* Action Button & Event selector */}
        <div className="flex flex-wrap items-center gap-3">
          {leaderboard.length > 0 && (
            <button
              type="button"
              onClick={handleFinalizeAndComplete}
              disabled={publishing || selectedEvent?.status === "COMPLETED"}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg ${
                selectedEvent?.status === "COMPLETED"
                  ? "bg-slate-800 text-slate-400 border border-slate-700 cursor-not-allowed"
                  : "bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/30 cursor-pointer"
              }`}
            >
              <Award className="w-4 h-4 text-amber-300" />
              {selectedEvent?.status === "COMPLETED"
                ? "Event Completed (Results Published)"
                : publishing
                ? "Submitting Results..."
                : "Submit Results & Complete Event"}
            </button>
          )}

          <div className="w-full sm:w-64">
            <select
              value={selectedEventId}
              onChange={(e) => {
                setSelectedEventId(e.target.value);
                setSearchParams({ event_id: e.target.value });
              }}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
            >
              {assignedEvents.map((a) => {
                const eventId = a.id || a.event_id;
                const title = a.title || a.event?.title || `Event #${eventId}`;
                return (
                  <option key={a.id} value={eventId}>
                    {title}
                  </option>
                );
              })}
            </select>
          </div>
        </div>
      </div>

      {publishSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center justify-between">
          <span>{publishSuccess}</span>
          <button onClick={() => setPublishSuccess(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {selectedEvent?.status === "COMPLETED" && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center justify-between gap-3">
          <div className="text-xs">
            <strong className="block font-bold text-white text-sm">Event Completed & Standings Published</strong>
            Official competition results have been published. Certificates are available for all participants.
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shrink-0">
            COMPLETED
          </span>
        </div>
      )}

      {/* Table */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <Trophy className="w-4 h-4 text-amber-400" /> Current Aggregated Standings
          </h3>
          <span className="text-xs font-mono text-slate-400">
            {leaderboard.length} Competitors Tabulated
          </span>
        </div>

        {leaderboard.length === 0 ? (
          <EmptyState
            icon={Trophy}
            title="No Scored Submissions Yet"
            description="Competitor rankings will automatically compute here as judges submit scorecards."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Rank</th>
                  <th className="px-6 py-4">Competitor / Team</th>
                  <th className="px-6 py-4">Reg ID</th>
                  <th className="px-6 py-4">Rubric Breakdown & Notes</th>
                  <th className="px-6 py-4 text-right">Tabulated Points</th>
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
                    <td className="px-6 py-4 space-y-1.5 align-top">
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
                      {item.remarks && (
                        <div className="text-[11px] text-slate-300 italic bg-slate-950/70 p-1.5 rounded-lg border border-slate-800/80">
                          "{item.remarks}"
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
