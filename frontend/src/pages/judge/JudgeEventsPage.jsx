import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Gavel, Award, Calendar, Users, MapPin, ExternalLink } from "lucide-react";
import { judgeApi } from "../../api/judgeApi";
import EmptyState from "../../components/EmptyState";

export default function JudgeEventsPage() {
  const [assigned, setAssigned] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssigned();
  }, []);

  const fetchAssigned = async () => {
    try {
      setLoading(true);
      const data = await judgeApi.getMyAssignedEvents();
      setAssigned(data || []);
    } catch (err) {
      console.error("Failed to load assigned events", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Assigned Competitive Events
        </h1>
        <p className="text-slate-400 text-sm">
          Select an assigned competition track to review rubrics and grade submissions.
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-64 rounded-3xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : assigned.length === 0 ? (
        <EmptyState
          icon={Gavel}
          title="No Events Assigned"
          description="You have not been assigned to any events yet by the event coordinators."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assigned.map((item) => {
            const evt = item.event;
            return (
              <div
                key={item.id}
                className="group relative rounded-3xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 transition-all p-6 flex flex-col justify-between overflow-hidden shadow-xl"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/20 uppercase tracking-wider">
                      Jury Appointed
                    </span>
                    <span className="text-xs font-mono text-slate-500">#{evt?.id}</span>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-white group-hover:text-amber-400 transition-colors">
                      {evt?.title}
                    </h3>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                      {evt?.short_description}
                    </p>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-2 text-xs text-slate-300">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-amber-400" />
                      <span>
                        {evt?.start_date
                          ? new Date(evt.start_date).toLocaleDateString(undefined, {
                              weekday: "short",
                              month: "short",
                              day: "numeric",
                            })
                          : "TBA"}
                      </span>
                    </div>
                    {evt?.venue && (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-rose-400" />
                        <span>{evt.venue.name}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Users className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{evt?.registrations?.length || 0} Registered Competitors</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center gap-3">
                  <Link
                    to={`/judge/scoring?event_id=${evt?.id}`}
                    className="flex-1 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-all flex items-center justify-center gap-1.5 shadow-lg shadow-amber-500/20"
                  >
                    <Gavel className="w-3.5 h-3.5" /> Start Scoring
                  </Link>
                  <Link
                    to={`/judge/rankings?event_id=${evt?.id}`}
                    className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                    title="View Leaderboard"
                  >
                    <Award className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
