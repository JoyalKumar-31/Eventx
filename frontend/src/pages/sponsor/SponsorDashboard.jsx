import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Building,
  Eye,
  MousePointer,
  TrendingUp,
  Award,
  Sparkles,
  ArrowRight,
  PlusCircle,
} from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import { sponsorApi } from "../../api/sponsorApi";
import StatCard from "../../components/StatCard";

export default function SponsorDashboard() {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [sponsorships, setSponsorships] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSponsorData();
  }, []);

  const fetchSponsorData = async () => {
    try {
      setLoading(true);
      const [m, sp] = await Promise.all([
        sponsorApi.getMetrics().catch(() => null),
        sponsorApi.getMySponsorships().catch(() => []),
      ]);
      setMetrics(m);
      setSponsorships(sp || []);
    } catch (err) {
      console.error("Failed to load sponsor metrics", err);
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
      {/* Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-950/50 via-slate-900 to-slate-900 p-6 sm:p-8 border border-emerald-500/20 shadow-2xl">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-semibold uppercase tracking-wider">
            <Building className="w-3.5 h-3.5" /> Brand Partner Hub
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Welcome, {user?.sponsor_profile?.company_name || user?.full_name || "Partner"}
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Monitor real-time student impressions, launch festival banner campaigns, and measure reach across our tech & cultural tracks.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/sponsor/plans"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition-all shadow-lg shadow-emerald-600/30"
            >
              <Award className="w-4 h-4" /> Sponsorship Tiers
            </Link>
            <Link
              to="/sponsor/promotions"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-all border border-slate-700"
            >
              <PlusCircle className="w-4 h-4 text-emerald-400" /> New Banner Slot
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Impressions"
          value={metrics?.total_impressions ?? 0}
          subtitle="Campus student views"
          icon={Eye}
          color="emerald"
        />
        <StatCard
          title="Total Clicks"
          value={metrics?.total_clicks ?? 0}
          subtitle="Inbound website leads"
          icon={MousePointer}
          color="blue"
        />
        <StatCard
          title="Click-Through Rate"
          value={`${ctr}%`}
          subtitle="Engagement efficiency"
          icon={TrendingUp}
          color="amber"
        />
        <StatCard
          title="Active Sponsorships"
          value={sponsorships.length}
          subtitle="Active partnership tiers"
          icon={Building}
          color="purple"
        />
      </div>

      {/* Active Partnerships List */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-lg">My Subscribed Partnerships</h3>
            <p className="text-xs text-slate-400 mt-0.5">Approved and active brand tiers</p>
          </div>
          <Link
            to="/sponsor/plans"
            className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            Upgrade Plan →
          </Link>
        </div>

        {sponsorships.length === 0 ? (
          <div className="p-8 text-center space-y-3">
            <Building className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">You haven't selected a sponsorship plan yet.</p>
            <Link
              to="/sponsor/plans"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-all"
            >
              Browse Sponsorship Plans
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {sponsorships.map((s) => (
              <div
                key={s.id}
                className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-800/40 transition-colors"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-base">
                      {s.plan?.tier} Tier Partnership
                    </span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">
                      {s.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Investment: ₹{Number(s.amount_contributed || s.plan?.price || 0).toLocaleString()} • Joined on {new Date(s.created_at).toLocaleDateString()}
                  </p>
                </div>

                <Link
                  to="/sponsor/promotions"
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors"
                >
                  Manage Banners →
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
