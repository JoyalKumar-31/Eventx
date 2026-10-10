import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { QrCode, Calendar, MapPin, Download, Printer, ShieldCheck, ExternalLink } from "lucide-react";
import { registrationApi } from "../../api/registrationApi";
import EmptyState from "../../components/EmptyState";
import QRPassModal from "../../components/QRPassModal";

export default function StudentPassPage() {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeModalRegId, setActiveModalRegId] = useState(null);

  useEffect(() => {
    fetchPasses();
  }, []);

  const fetchPasses = async () => {
    try {
      setLoading(true);
      const data = await registrationApi.getMyRegistrations();
      // Only keep confirmed or paid registrations that have a pass
      const valid = (data || []).filter((r) => {
        const fee = Number(r.registration_fee ?? r.event?.registration_fee ?? 0);
        const isPaid = fee === 0 || r.payment_status === "PAID" || r.payment_status === "SUCCESS";
        return isPaid && (r.status === "CONFIRMED" || fee === 0);
      });
      setRegistrations(valid);
    } catch (err) {
      console.error("Failed to load passes", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Digital Festival Entry Passes
        </h1>
        <p className="text-slate-400 text-sm">
          Present these QR passes at the entrance gate or event hall for instant barcode attendance check-in.
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-64 rounded-3xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : registrations.length === 0 ? (
        <EmptyState
          icon={QrCode}
          title="No Active Entry Passes"
          description="Your confirmed event registrations will generate digital entry passes here."
          actionText="Explore Events"
          actionHref="/events"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {registrations.map((reg) => {
            const eventTitle = reg.event_title || reg.event?.title || `Event #${reg.event_id}`;
            const categoryName = reg.category_name || reg.event?.category?.name || "General Track";
            const teamName = reg.team_name || reg.team?.name;
            const startDate = reg.start_time || reg.event?.start_time || reg.event?.start_date;
            const venueName = reg.venue_name || reg.event?.venue?.name;

            return (
              <div
                key={reg.id}
                className="group relative rounded-3xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 transition-all p-6 flex flex-col justify-between overflow-hidden shadow-xl"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                      <ShieldCheck className="w-3.5 h-3.5" /> Entry Authorized
                    </span>
                    <span className="text-xs font-mono text-slate-500">
                      PASS-#{reg.id}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-white group-hover:text-indigo-400 transition-colors">
                      {eventTitle}
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">
                      {categoryName} • {teamName ? "TEAM" : (reg.event?.event_format || "SOLO")}
                    </p>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/80 space-y-2 text-xs text-slate-300">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                      <span>
                        {startDate
                          ? new Date(startDate).toLocaleDateString(undefined, {
                              weekday: "short",
                              month: "short",
                              day: "numeric",
                            })
                          : "TBA"}
                      </span>
                    </div>
                    {venueName && (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-rose-400" />
                        <span>{venueName}</span>
                      </div>
                    )}
                    {teamName && (
                      <div className="text-indigo-300 font-semibold">
                        Team: {teamName}
                      </div>
                    )}
                  </div>
                </div>

              <div className="mt-6 pt-4 border-t border-slate-800">
                <button
                  onClick={() => setActiveModalRegId(reg.id)}
                  className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20"
                >
                  <QrCode className="w-4 h-4" /> Open Full-Screen Pass
                </button>
              </div>
            </div>
          );
        })}
        </div>
      )}

      {/* QR Pass Modal */}
      {activeModalRegId && (
        <QRPassModal
          registrationId={activeModalRegId}
          onClose={() => setActiveModalRegId(null)}
        />
      )}
    </div>
  );
}
