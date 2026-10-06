import React, { useState, useEffect } from "react";
import { Award, CheckCircle, Building, Sparkles, ShieldCheck } from "lucide-react";
import { sponsorApi } from "../../api/sponsorApi";
import EmptyState from "../../components/EmptyState";

export default function SponsorPlansPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submittingPlanId, setSubmittingPlanId] = useState(null);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const data = await sponsorApi.getPlans();
      setPlans(data || []);
    } catch (err) {
      console.error("Failed to load plans", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = async (planId) => {
    try {
      setSubmittingPlanId(planId);
      setFeedback(null);
      await sponsorApi.selectPlan({
        plan_id: planId,
        notes: "Partner requested tier via self-service portal.",
      });
      setFeedback({
        type: "success",
        text: "Sponsorship tier selected successfully! Our committee will verify your deliverables.",
      });
    } catch (err) {
      console.error("Failed to select plan", err);
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || "Could not select this sponsorship tier.",
      });
    } finally {
      setSubmittingPlanId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Sponsorship Tiers & Brand Packages
        </h1>
        <p className="text-slate-400 text-sm">
          Select a brand tier to showcase your company across prime festival touchpoints and digital feeds.
        </p>
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

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-72 rounded-3xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : plans.length === 0 ? (
        <EmptyState
          icon={Building}
          title="No Sponsorship Plans Available"
          description="The festival committee has not published any sponsorship tiers yet."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((p) => {
            const isPlatinum = p.tier === "TITLE" || p.tier === "PLATINUM";
            return (
              <div
                key={p.id}
                className={`p-6 sm:p-8 rounded-3xl border transition-all flex flex-col justify-between shadow-xl ${
                  isPlatinum
                    ? "bg-gradient-to-b from-slate-900 to-emerald-950/30 border-emerald-500/40 shadow-emerald-500/5"
                    : "bg-slate-900 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="space-y-5">
                  <div className="flex items-center justify-between">
                    <span className="px-3 py-1 rounded-full text-xs font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-widest">
                      {p.tier} Tier
                    </span>
                    {isPlatinum && <Sparkles className="w-5 h-5 text-emerald-400" />}
                  </div>

                  <div>
                    <div className="text-3xl sm:text-4xl font-black font-mono text-white">
                      ₹{Number(p.price).toLocaleString()}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{p.description}</p>
                  </div>

                  {p.benefits && p.benefits.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-800/80">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">
                        Included Deliverables
                      </span>
                      {p.benefits.map((b, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{b}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mt-8 pt-4 border-t border-slate-800">
                  <button
                    onClick={() => handleSelectPlan(p.id)}
                    disabled={submittingPlanId === p.id}
                    className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs transition-all shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2"
                  >
                    {submittingPlanId === p.id ? "Processing..." : "Select & Confirm Tier"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
