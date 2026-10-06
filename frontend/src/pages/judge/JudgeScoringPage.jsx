import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Gavel,
  Sliders,
  CheckCircle2,
  Users,
  MessageSquare,
  Award,
  Sparkles,
  AlertCircle,
} from "lucide-react";
import { judgeApi } from "../../api/judgeApi";
import { registrationApi } from "../../api/registrationApi";
import EmptyState from "../../components/EmptyState";

export default function JudgeScoringPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlEventId = searchParams.get("event_id");

  const [assignedEvents, setAssignedEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(urlEventId || "");
  const [participants, setParticipants] = useState([]);
  const [selectedRegId, setSelectedRegId] = useState("");
  const [criteria, setCriteria] = useState([]);
  const [scores, setScores] = useState({});
  const [remarks, setRemarks] = useState("");

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    fetchAssignedEvents();
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      loadEventData(Number(selectedEventId));
    }
  }, [selectedEventId]);

  const fetchAssignedEvents = async () => {
    try {
      setLoading(true);
      const data = await judgeApi.getMyAssignedEvents();
      setAssignedEvents(data || []);
      if (!selectedEventId && data && data.length > 0) {
        setSelectedEventId(String(data[0].event_id));
      }
    } catch (err) {
      console.error("Failed to load assigned events", err);
    } finally {
      setLoading(false);
    }
  };

  const loadEventData = async (eventId) => {
    try {
      const [parts, critList] = await Promise.all([
        registrationApi.getEventParticipants(eventId).catch(() => []),
        judgeApi.getEventCriteria(eventId).catch(() => []),
      ]);
      setParticipants(parts || []);
      setCriteria(critList || []);

      if (parts && parts.length > 0) {
        setSelectedRegId(String(parts[0].id));
      }
      // Initialize scores map
      const initial = {};
      (critList || []).forEach((c) => {
        initial[c.id] = Math.round(c.max_points * 0.7); // default 70%
      });
      setScores(initial);
      setRemarks("");
    } catch (err) {
      console.error("Failed to load event participants or criteria", err);
    }
  };

  const handleScoreChange = (criteriaId, val) => {
    setScores((prev) => ({
      ...prev,
      [criteriaId]: Number(val),
    }));
  };

  const calculateTotal = () => {
    let total = 0;
    criteria.forEach((c) => {
      const val = scores[c.id] || 0;
      total += val * (c.weightage || 1.0);
    });
    return total.toFixed(1);
  };

  const handleSubmitScore = async (e) => {
    e.preventDefault();
    if (!selectedEventId || !selectedRegId) return;

    try {
      setSubmitting(true);
      setFeedback(null);

      const scorePayload = criteria.map((c) => ({
        criteria_id: c.id,
        score: Number(scores[c.id] || 0),
      }));

      await judgeApi.submitScores(Number(selectedEventId), {
        registration_id: Number(selectedRegId),
        scores: scorePayload,
        remarks: remarks.trim(),
      });

      setFeedback({
        type: "success",
        text: "Scores submitted successfully and tabulated into leaderboards!",
      });
    } catch (err) {
      console.error("Failed to submit score", err);
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || "Could not submit score. Please try again.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const activeParticipant = participants.find((p) => String(p.id) === String(selectedRegId));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Submission Evaluation & Scoring
          </h1>
          <p className="text-slate-400 text-sm">
            Evaluate competitors using standardized weighted rubrics and provide qualitative feedback.
          </p>
        </div>

        {/* Event Selector */}
        <div className="w-full sm:w-72">
          <select
            value={selectedEventId}
            onChange={(e) => {
              setSelectedEventId(e.target.value);
              setSearchParams({ event_id: e.target.value });
            }}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
          >
            {assignedEvents.map((a) => (
              <option key={a.id} value={a.event_id}>
                {a.event?.title || `Event #${a.event_id}`}
              </option>
            ))}
          </select>
        </div>
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
        <div className="h-64 rounded-3xl bg-slate-900 border border-slate-800 animate-pulse" />
      ) : assignedEvents.length === 0 ? (
        <EmptyState
          icon={Gavel}
          title="No Assigned Events"
          description="You are not assigned to evaluate any events at this time."
        />
      ) : participants.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No Enrolled Competitors"
          description="There are no participants registered in this event yet to evaluate."
        />
      ) : (
        <form onSubmit={handleSubmitScore} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Competitor Selector Column */}
          <div className="lg:col-span-1 p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Users className="w-4 h-4 text-amber-400" />
              Select Competitor
            </h3>

            <div className="space-y-2 max-h-[480px] overflow-y-auto pr-1">
              {participants.map((p) => {
                const isSelected = String(p.id) === String(selectedRegId);
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => {
                      setSelectedRegId(String(p.id));
                      setFeedback(null);
                    }}
                    className={`w-full text-left p-3.5 rounded-2xl transition-all border ${
                      isSelected
                        ? "bg-amber-500/10 border-amber-500/50 shadow-lg shadow-amber-500/5"
                        : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="font-bold text-white text-sm">
                      {p.user?.full_name || `Participant #${p.user_id}`}
                    </div>
                    {p.team && (
                      <div className="text-xs text-indigo-300 font-semibold mt-0.5">
                        Team: {p.team.name}
                      </div>
                    )}
                    <div className="text-[10px] text-slate-500 mt-1">
                      Reg ID: #{p.id}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Scoring Rubrics Column */}
          <div className="lg:col-span-2 p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 space-y-6 flex flex-col justify-between">
            <div className="space-y-6">
              {/* Evaluated Competitor Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                <div>
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest block">
                    Now Evaluating
                  </span>
                  <h2 className="text-xl font-black text-white">
                    {activeParticipant?.user?.full_name || "Competitor"}
                    {activeParticipant?.team ? ` (${activeParticipant.team.name})` : ""}
                  </h2>
                </div>

                <div className="text-right">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest block">
                    Calculated Weighted Score
                  </span>
                  <div className="text-3xl font-black font-mono text-amber-400">
                    {calculateTotal()} <span className="text-xs text-slate-500 font-normal">pts</span>
                  </div>
                </div>
              </div>

              {/* Rubric Sliders */}
              <div className="space-y-5">
                {criteria.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">
                    No rubric criteria configured by coordinator for this event yet.
                  </p>
                ) : (
                  criteria.map((c) => {
                    const currentVal = scores[c.id] ?? 0;
                    return (
                      <div
                        key={c.id}
                        className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-bold text-white text-sm block">{c.name}</span>
                            {c.description && (
                              <p className="text-[11px] text-slate-400">{c.description}</p>
                            )}
                          </div>
                          <span className="font-mono font-bold text-base text-amber-400">
                            {currentVal} / {c.max_points}
                          </span>
                        </div>

                        <div className="flex items-center gap-3 pt-1">
                          <input
                            type="range"
                            min={0}
                            max={c.max_points}
                            step={1}
                            value={currentVal}
                            onChange={(e) => handleScoreChange(c.id, e.target.value)}
                            className="flex-1 accent-amber-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
                          />
                        </div>
                        <div className="text-[10px] text-slate-500 text-right">
                          Weight factor: {c.weightage}x
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Qualitative Remarks */}
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
                  Qualitative Feedback & Remarks (Optional)
                </label>
                <textarea
                  rows={3}
                  placeholder="Key strengths, architectural highlights, suggestions for improvement..."
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                type="submit"
                disabled={submitting || criteria.length === 0}
                className="px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold text-xs transition-all flex items-center gap-2 shadow-lg shadow-amber-500/20"
              >
                <Gavel className="w-4 h-4" />
                {submitting ? "Recording Score..." : "Submit Official Evaluation"}
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
