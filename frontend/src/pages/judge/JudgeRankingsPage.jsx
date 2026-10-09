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

        {/* Event selector */}
        <div className="w-full sm:w-72">
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
                  <th className="px-6 py-4 text-right">Tabulated Points</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {leaderboard.map((item) => (
                  <tr key={item.registration_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-sm">
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
                    <td className="px-6 py-4">
                      <div className="font-bold text-white text-sm">
                        {item.participant_name}
                      </div>
                      {item.team_name && (
                        <div className="text-[11px] text-indigo-300 flex items-center gap-1 mt-0.5">
                          <Users className="w-3 h-3" /> Team: {item.team_name}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 font-mono text-slate-400">
                      #{item.registration_id}
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-black text-white text-sm">
                      {Number(item.total_score).toFixed(1)}{" "}
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
