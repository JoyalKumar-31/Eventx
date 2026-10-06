import React, { useState, useEffect } from "react";
import { Megaphone, AlertCircle, Clock, Search, Calendar, ShieldCheck } from "lucide-react";
import { announcementApi } from "../../api/announcementApi";
import EmptyState from "../../components/EmptyState";

export default function AnnouncementsPage() {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await announcementApi.getAnnouncements();
      setAnnouncements(data || []);
    } catch (err) {
      console.error("Failed to load announcements", err);
      setError("Unable to load announcements. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  const filtered = announcements.filter(
    (a) =>
      a.title?.toLowerCase().includes(search.toLowerCase()) ||
      a.content?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold uppercase tracking-wider">
            <Megaphone className="w-3.5 h-3.5" /> Official Bulletins
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
            Fest Announcements
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-base sm:text-lg">
            Stay up to date with immediate schedule changes, prize pool releases, guest announcements, and emergency notices.
          </p>
        </div>

        {/* Filter bar */}
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search announcements..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors shadow-inner"
          />
        </div>

        {/* List */}
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-36 rounded-2xl bg-slate-900 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-center">
            {error}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={Megaphone}
            title="No Announcements Posted"
            description="There are currently no active public announcements."
          />
        ) : (
          <div className="space-y-4">
            {filtered.map((item) => {
              const isUrgent = item.priority === "URGENT" || item.priority === "HIGH";
              const dateStr = item.created_at
                ? new Date(item.created_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })
                : "Recent";

              return (
                <div
                  key={item.id}
                  className={`p-6 rounded-2xl border transition-all ${
                    isUrgent
                      ? "bg-amber-950/20 border-amber-500/30 shadow-lg shadow-amber-500/5"
                      : "bg-slate-900/90 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                    <div className="flex items-center gap-2">
                      {isUrgent ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 uppercase tracking-wider">
                          <AlertCircle className="w-3 h-3" /> Priority Notice
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                          <ShieldCheck className="w-3 h-3 text-indigo-400" /> Official Update
                        </span>
                      )}
                      {item.target_role && item.target_role !== "ALL" && (
                        <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800/80 text-slate-300">
                          Target: {item.target_role}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-slate-500">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{dateStr}</span>
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                  <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
                    {item.content}
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
