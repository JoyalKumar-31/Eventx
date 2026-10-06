import React, { useState, useEffect } from "react";
import { Eye, MousePointer, TrendingUp, BarChart3, Building } from "lucide-react";
import { sponsorApi } from "../../api/sponsorApi";
import StatCard from "../../components/StatCard";

export default function SponsorAnalyticsPage() {
  const [metrics, setMetrics] = useState(null);
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [m, promos] = await Promise.all([
        sponsorApi.getMetrics().catch(() => null),
        sponsorApi.getActivePromotions().catch(() => []),
      ]);
      setMetrics(m);
      setPromotions(promos || []);
    } catch (err) {
      console.error("Failed to load analytics", err);
    } finally {
      setLoading(false);
    }
  };

  const ctr =
    metrics && metrics.total_impressions > 0
      ? ((metrics.total_clicks / metrics.total_impressions) * 100).toFixed(2)
      : "0.00";

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Brand Engagement & Reach Analytics
        </h1>
        <p className="text-slate-400 text-sm">
          Measure student interactions, banner impression velocity, and outbound conversion clicks.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          title="Total Impressions"
          value={metrics?.total_impressions ?? 0}
          subtitle="Delivered banner impressions"
          icon={Eye}
          color="emerald"
        />
        <StatCard
          title="Direct Clicks"
          value={metrics?.total_clicks ?? 0}
          subtitle="Outbound leads generated"
          icon={MousePointer}
          color="blue"
        />
        <StatCard
          title="Overall CTR"
          value={`${ctr}%`}
          subtitle="Click-through conversion"
          icon={TrendingUp}
          color="amber"
        />
      </div>

      {/* Breakdown per promotion slot */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
        <div className="border-b border-slate-800 pb-4">
          <h3 className="font-bold text-white text-lg">Slot-by-Slot Engagement Breakdown</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Compare performance across header carousels and detail sidebars
          </p>
        </div>

        {promotions.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No banner slots currently running.</p>
        ) : (
          <div className="space-y-4">
            {promotions.map((p) => {
              const imps = p.impressions_count || 0;
              const clks = p.clicks_count || 0;
              const rate = imps > 0 ? ((clks / imps) * 100).toFixed(1) : "0.0";

              return (
                <div
                  key={p.id}
                  className="p-5 rounded-2xl bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <span className="font-mono font-bold text-emerald-400 text-sm">
                      {p.slot_name}
                    </span>
                    <p className="text-xs text-slate-400 truncate max-w-md">
                      Target: {p.target_url}
                    </p>
                  </div>

                  <div className="flex items-center gap-6 font-mono text-xs">
                    <div>
                      <span className="text-slate-500 uppercase text-[10px] block font-bold">Views</span>
                      <strong className="text-white text-sm">{imps}</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 uppercase text-[10px] block font-bold">Clicks</span>
                      <strong className="text-emerald-400 text-sm">{clks}</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 uppercase text-[10px] block font-bold">CTR</span>
                      <strong className="text-amber-400 text-sm">{rate}%</strong>
                    </div>
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
