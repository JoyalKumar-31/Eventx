import React, { useState, useEffect } from "react";
import { Building, PlusCircle, DollarSign, Users, CheckCircle, ShieldCheck, Sparkles } from "lucide-react";
import { sponsorApi } from "../../api/sponsorApi";
import EmptyState from "../../components/EmptyState";

export default function AdminSponsorsPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form states
  const [tier, setTier] = useState("PLATINUM");
  const [price, setPrice] = useState(50000);
  const [description, setDescription] = useState("");
  const [maxSponsors, setMaxSponsors] = useState(3);
  const [benefits, setBenefits] = useState("");
  const [submitting, setSubmitting] = useState(false);
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

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setFeedback(null);
      await sponsorApi.createPlan({
        tier,
        price: Number(price),
        description: description.trim(),
        max_sponsors: Number(maxSponsors),
        benefits: benefits
          ? benefits.split("\n").map((b) => b.trim()).filter(Boolean)
          : [],
      });
      setFeedback({ type: "success", text: "Sponsorship tier plan created!" });
      setShowModal(false);
      setDescription("");
      setBenefits("");
      fetchPlans();
    } catch (err) {
      console.error("Failed to create plan", err);
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || "Failed to create plan.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Sponsorship Tiers & Partnerships
          </h1>
          <p className="text-slate-400 text-sm">
            Configure partner tier pricing, branding slots, and corporate deliverables.
          </p>
        </div>

        <button
          onClick={() => {
            setFeedback(null);
            setShowModal(true);
          }}
          className="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs transition-all flex items-center gap-2 self-start sm:self-center shadow-lg shadow-purple-600/20"
        >
          <PlusCircle className="w-4 h-4" /> Create Tier Plan
        </button>
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

      {/* Plans Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-64 rounded-3xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : plans.length === 0 ? (
        <EmptyState
          icon={Building}
          title="No Sponsorship Plans Configured"
          description="Create your first corporate sponsorship plan above to open onboarding for brand partners."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((p) => (
            <div
              key={p.id}
              className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 hover:border-purple-500/40 transition-all flex flex-col justify-between shadow-xl"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 rounded-full text-xs font-black bg-purple-500/20 text-purple-300 border border-purple-500/30 uppercase tracking-widest">
                    {p.tier} Tier
                  </span>
                  <Building className="w-5 h-5 text-purple-400" />
                </div>

                <div>
                  <div className="text-3xl font-black font-mono text-white">
                    ₹{Number(p.price).toLocaleString()}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{p.description || "Corporate partnership tier"}</p>
                </div>

                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1.5">
                  <div className="flex justify-between">
                    <span>Capacity / Cap:</span>
                    <strong className="text-white">{p.max_sponsors} Brands Max</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Active Sponsors:</span>
                    <strong className="text-emerald-400">{p.sponsorships?.length || 0} Joined</strong>
                  </div>
                </div>

                {p.benefits && p.benefits.length > 0 && (
                  <div className="space-y-1.5 pt-2">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block">Deliverables</span>
                    {p.benefits.map((b, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 text-xs text-slate-300">
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{b}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Plan Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Building className="w-5 h-5 text-purple-400" /> New Sponsorship Plan
              </h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleCreatePlan} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Tier Name</label>
                  <select
                    value={tier}
                    onChange={(e) => setTier(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                  >
                    <option value="TITLE">TITLE</option>
                    <option value="PLATINUM">PLATINUM</option>
                    <option value="GOLD">GOLD</option>
                    <option value="SILVER">SILVER</option>
                    <option value="BRONZE">BRONZE</option>
                    <option value="PARTNER">PARTNER</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Price (₹)</label>
                  <input
                    type="number"
                    min={1000}
                    step={1000}
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Max Brand Slots</label>
                <input
                  type="number"
                  min={1}
                  value={maxSponsors}
                  onChange={(e) => setMaxSponsors(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
                <input
                  type="text"
                  placeholder="e.g. Prominent main-stage branding and booth space"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Deliverables (1 per line)
                </label>
                <textarea
                  rows={3}
                  placeholder="Keynote speech slot&#10;Logo on fest banner&#10;10 VIP passes"
                  value={benefits}
                  onChange={(e) => setBenefits(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                />
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/30"
                >
                  {submitting ? "Saving..." : "Create Plan"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
