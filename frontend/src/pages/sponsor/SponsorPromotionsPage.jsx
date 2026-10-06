import React, { useState, useEffect } from "react";
import { PlusCircle, ExternalLink, Eye, MousePointer, Image as ImageIcon, Sparkles } from "lucide-react";
import { sponsorApi } from "../../api/sponsorApi";
import EmptyState from "../../components/EmptyState";

export default function SponsorPromotionsPage() {
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form states
  const [slotName, setSlotName] = useState("MAIN_HERO");
  const [bannerUrl, setBannerUrl] = useState("");
  const [targetUrl, setTargetUrl] = useState("");
  const [priority, setPriority] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    fetchPromotions();
  }, []);

  const fetchPromotions = async () => {
    try {
      setLoading(true);
      const data = await sponsorApi.getActivePromotions();
      setPromotions(data || []);
    } catch (err) {
      console.error("Failed to load promotions", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePromotion = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setFeedback(null);
      await sponsorApi.createPromotion({
        slot_name: slotName,
        banner_image_url: bannerUrl.trim(),
        target_url: targetUrl.trim(),
        priority: Number(priority),
      });
      setFeedback({ type: "success", text: "Promotional banner slot created!" });
      setShowModal(false);
      setBannerUrl("");
      setTargetUrl("");
      fetchPromotions();
    } catch (err) {
      console.error("Failed to create promotion", err);
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || "Failed to create promotion.",
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
            Promotional Banners & Brand Slots
          </h1>
          <p className="text-slate-400 text-sm">
            Deploy brand visuals and external target links across active fest portal surfaces.
          </p>
        </div>

        <button
          onClick={() => {
            setFeedback(null);
            setShowModal(true);
          }}
          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all flex items-center gap-2 self-start sm:self-center shadow-lg shadow-emerald-600/20"
        >
          <PlusCircle className="w-4 h-4" /> New Banner Slot
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

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <div key={i} className="h-60 rounded-3xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : promotions.length === 0 ? (
        <EmptyState
          icon={ImageIcon}
          title="No Active Banners Found"
          description="Deploy promotional banner slots to start capturing student traffic and impressions."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {promotions.map((p) => {
            const impressions = p.impressions_count || 0;
            const clicks = p.clicks_count || 0;
            const ctr = impressions > 0 ? ((clicks / impressions) * 100).toFixed(1) : "0.0";

            return (
              <div
                key={p.id}
                className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl flex flex-col justify-between"
              >
                <div>
                  {/* Banner Preview */}
                  <div className="h-36 bg-slate-950 overflow-hidden relative flex items-center justify-center border-b border-slate-800">
                    {p.banner_image_url ? (
                      <img
                        src={p.banner_image_url}
                        alt={p.slot_name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="text-slate-600 text-xs flex items-center gap-2">
                        <ImageIcon className="w-5 h-5" /> No banner graphic
                      </div>
                    )}
                    <span className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-[10px] font-mono font-bold bg-slate-950/80 text-emerald-400 border border-slate-800">
                      {p.slot_name}
                    </span>
                  </div>

                  <div className="p-5 space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">Target Link:</span>
                      <a
                        href={p.target_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-emerald-400 hover:underline flex items-center gap-1 font-mono text-[11px]"
                      >
                        {p.target_url} <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>

                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/80 text-center">
                      <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                        <span className="text-[10px] text-slate-500 uppercase font-bold block">
                          Impressions
                        </span>
                        <span className="text-base font-bold font-mono text-white">
                          {impressions}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                        <span className="text-[10px] text-slate-500 uppercase font-bold block">
                          Clicks
                        </span>
                        <span className="text-base font-bold font-mono text-emerald-400">
                          {clicks}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                        <span className="text-[10px] text-slate-500 uppercase font-bold block">
                          CTR
                        </span>
                        <span className="text-base font-bold font-mono text-amber-400">
                          {ctr}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-emerald-400" /> New Banner Slot
              </h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleCreatePromotion} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Placement Slot</label>
                <select
                  value={slotName}
                  onChange={(e) => setSlotName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                >
                  <option value="MAIN_HERO">MAIN_HERO (Home Hero Carousel)</option>
                  <option value="EVENT_DETAIL">EVENT_DETAIL (Sidebar Sponsor)</option>
                  <option value="FOOTER_BANNER">FOOTER_BANNER (Global Footer Banner)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Banner Image URL *</label>
                <input
                  type="url"
                  required
                  placeholder="https://example.com/banner.png"
                  value={bannerUrl}
                  onChange={(e) => setBannerUrl(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Inbound URL *</label>
                <input
                  type="url"
                  required
                  placeholder="https://yourcompany.com/fest-offer"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
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
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30"
                >
                  {submitting ? "Deploying..." : "Deploy Slot"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
