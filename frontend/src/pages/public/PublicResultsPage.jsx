import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Trophy, Medal, Award, Search, Users, ExternalLink, Calendar } from "lucide-react";
import { judgeApi } from "../../api/judgeApi";
import EmptyState from "../../components/EmptyState";

export default function PublicResultsPage() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [selectedEvent, setSelectedEvent] = useState("all");

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await judgeApi.getAllPublicResults();
      setResults(data || []);
    } catch (err) {
      console.error("Failed to load results", err);
      setError("Unable to load fest results at this moment.");
    } finally {
      setLoading(false);
    }
  };

  // Group by event
  const eventsMap = {};
  results.forEach((r) => {
    if (!eventsMap[r.event_id]) {
      eventsMap[r.event_id] = {
        id: r.event_id,
        title: r.event_title || `Event #${r.event_id}`,
        items: [],
      };
    }
    eventsMap[r.event_id].items.push(r);
  });

  const eventList = Object.values(eventsMap);

  const filteredEvents = eventList
    .map((evt) => {
      const filteredItems = evt.items.filter(
        (item) =>
          item.participant_name?.toLowerCase().includes(search.toLowerCase()) ||
          item.team_name?.toLowerCase().includes(search.toLowerCase()) ||
          evt.title.toLowerCase().includes(search.toLowerCase())
      );
      return {
        ...evt,
        items: filteredItems,
      };
    })
    .filter((evt) => {
      if (selectedEvent !== "all" && String(evt.id) !== selectedEvent) return false;
      return evt.items.length > 0;
    });

  const getRankBadge = (rank) => {
    if (rank === 1) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
          <Trophy className="w-3.5 h-3.5 text-amber-400" /> Winner (1st)
        </span>
      );
    }
    if (rank === 2) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-300/20 text-slate-200 border border-slate-300/40">
          <Medal className="w-3.5 h-3.5 text-slate-300" /> 1st Runner Up (2nd)
        </span>
      );
    }
    if (rank === 3) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-700/20 text-amber-500 border border-amber-700/40">
          <Award className="w-3.5 h-3.5 text-amber-600" /> 2nd Runner Up (3rd)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400">
        Rank #{rank}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold uppercase tracking-wider">
            <Trophy className="w-3.5 h-3.5" /> Official Standings
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
            Hall of Champions & Results
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-base sm:text-lg">
            Celebrate the winners, runner-ups, and standout performers across all events and competitive rounds.
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search winners, teams, or events..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors"
            />
          </div>

          <div className="w-full sm:w-auto flex items-center gap-2">
            <span className="text-xs text-slate-400 whitespace-nowrap">Filter Event:</span>
            <select
              value={selectedEvent}
              onChange={(e) => setSelectedEvent(e.target.value)}
              className="w-full sm:w-64 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
            >
              <option value="all">All Events ({eventList.length})</option>
              {eventList.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Results Content */}
        {loading ? (
          <div className="space-y-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 rounded-2xl bg-slate-900 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-center">
            {error}
          </div>
        ) : filteredEvents.length === 0 ? (
          <EmptyState
            icon={Trophy}
            title="No Results Published Yet"
            description="Results will be announced here once competitions finish and judging is finalized."
          />
        ) : (
          <div className="space-y-8">
            {filteredEvents.map((evt) => (
              <div
                key={evt.id}
                className="overflow-hidden rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl"
              >
                {/* Event header banner */}
                <div className="px-6 py-4 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border-b border-slate-800 flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                      <Trophy className="w-5 h-5 text-amber-400" />
                      {evt.title}
                    </h2>
                  </div>
                  <Link
                    to={`/events/${evt.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                  >
                    Event Details <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>

                {/* Leaderboard table */}
                <div className="divide-y divide-slate-800/80">
                  {evt.items.map((row) => (
                    <div
                      key={row.id}
                      className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/40 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="shrink-0">{getRankBadge(row.rank)}</div>
                        <div>
                          <div className="text-base font-bold text-white flex items-center gap-2">
                            {row.participant_name}
                            {row.award_title && (
                              <span className="text-xs font-medium text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                                {row.award_title}
                              </span>
                            )}
                          </div>
                          {row.team_name && (
                            <div className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
                              <Users className="w-3.5 h-3.5 text-slate-500" /> Team:{" "}
                              <span className="text-indigo-300 font-medium">{row.team_name}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="text-right sm:text-right flex sm:flex-col items-center sm:items-end justify-between">
                        <span className="text-xs text-slate-500 uppercase tracking-wider">Final Score</span>
                        <span className="text-lg font-mono font-extrabold text-white">
                          {row.total_score != null ? Number(row.total_score).toFixed(1) : "--"}
                          <span className="text-xs text-slate-500 font-normal"> pts</span>
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
