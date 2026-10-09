import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Calendar, Clock, MapPin, Search, Tag, ArrowRight } from "lucide-react";
import { publicApi } from "../../api/publicApi";
import EmptyState from "../../components/EmptyState";

export default function SchedulePage() {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [selectedDate, setSelectedDate] = useState("all");

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await publicApi.getSchedules();
      setSchedules(data || []);
    } catch (err) {
      console.error("Failed to load schedules", err);
      setError("Unable to load festival schedule. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  // Group schedules or extract unique dates
  const uniqueDates = Array.from(
    new Set(
      schedules
        .map((s) => (s.start_time ? new Date(s.start_time).toISOString().split("T")[0] : null))
        .filter(Boolean)
    )
  ).sort();

  const filteredSchedules = schedules.filter((s) => {
    const searchTarget = (
      (s.event?.title || "") + " " +
      (s.title || "") + " " +
      (s.round?.name || "") + " " +
      (s.venue?.name || "")
    ).toLowerCase();

    const matchesSearch = !search || searchTarget.includes(search.toLowerCase());

    const itemDate = s.start_time ? new Date(s.start_time).toISOString().split("T")[0] : null;
    const matchesDate = selectedDate === "all" || itemDate === selectedDate;

    return matchesSearch && matchesDate;
  });

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold uppercase tracking-wider">
            <Calendar className="w-3.5 h-3.5" /> Fest Timetable
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
            Schedule & Timeline
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-base sm:text-lg">
            Plan your festival journey. Track real-time rounds, stage schedules, and venue allotments across all competitive tracks.
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by event, round, or venue..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors"
            />
          </div>

          {/* Date tabs */}
          <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
            <button
              onClick={() => setSelectedDate("all")}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedDate === "all"
                  ? "bg-amber-500 text-slate-950 font-bold shadow-lg shadow-amber-500/20"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              All Days ({schedules.length})
            </button>
            {uniqueDates.map((dateStr) => {
              const d = new Date(dateStr);
              const label = d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
              return (
                <button
                  key={dateStr}
                  onClick={() => setSelectedDate(dateStr)}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                    selectedDate === dateStr
                      ? "bg-amber-500 text-slate-950 font-bold shadow-lg shadow-amber-500/20"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content list */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-44 rounded-2xl bg-slate-900 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-center">
            {error}
          </div>
        ) : filteredSchedules.length === 0 ? (
          <EmptyState
            icon={Calendar}
            title="No Scheduled Rounds Found"
            description="There are currently no scheduled events matching your filter."
          />
        ) : (
          <div className="space-y-4">
            {filteredSchedules.map((item) => {
              const start = item.start_time ? new Date(item.start_time) : null;
              const end = item.end_time ? new Date(item.end_time) : null;
              return (
                <div
                  key={item.id}
                  className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-5 rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 hover:bg-slate-900 transition-all gap-4"
                >
                  <div className="flex items-start sm:items-center gap-4">
                    {/* Time block */}
                    <div className="w-24 shrink-0 text-center p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
                      <div className="text-xs font-bold text-amber-400 uppercase">
                        {start ? start.toLocaleDateString(undefined, { weekday: "short" }) : "TBA"}
                      </div>
                      <div className="text-sm font-extrabold text-white">
                        {start ? start.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "--:--"}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {end ? `to ${end.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : ""}
                      </div>
                    </div>

                    {/* Details */}
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        {item.round && (
                          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                            {item.round.name}
                          </span>
                        )}
                        {item.event?.category && (
                          <span className="flex items-center gap-1 text-[11px] text-slate-400">
                            <Tag className="w-3 h-3 text-slate-500" />
                            {item.event.category.name}
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-bold text-white hover:text-amber-400 transition-colors">
                        <Link to={`/events/${item.event_id}`}>
                          {item.event?.title || item.title || `Event #${item.event_id}`}
                        </Link>
                      </h3>
                      <div className="flex items-center gap-3 text-xs text-slate-400">
                        {item.venue && (
                          <span className="flex items-center gap-1 text-slate-300 font-medium">
                            <MapPin className="w-3.5 h-3.5 text-amber-400" />
                            {item.venue.name} {item.venue.room_number ? `(${item.venue.room_number})` : ""}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Action link */}
                  <Link
                    to={`/events/${item.event_id}`}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-amber-500 hover:text-slate-950 transition-all self-end sm:self-center shrink-0"
                  >
                    View Event <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
