import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Gavel,
  UserPlus,
  PlusCircle,
  Sliders,
  CheckCircle,
  AlertCircle,
  Trash2,
  Calendar,
  Layers,
} from "lucide-react";
import { eventApi } from "../../api/eventApi";
import { judgeApi } from "../../api/judgeApi";
import { adminApi } from "../../api/adminApi";
import EmptyState from "../../components/EmptyState";

export default function CoordinatorJudgesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlEventId = searchParams.get("event_id");

  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(urlEventId || "");
  const [allJudges, setAllJudges] = useState([]);
  const [assignedJudges, setAssignedJudges] = useState([]);
  const [criteria, setCriteria] = useState([]);
  const [loading, setLoading] = useState(true);

  // Assignment form
  const [selectedJudgeUserId, setSelectedJudgeUserId] = useState("");

  // Criteria form
  const [critName, setCritName] = useState("");
  const [critDesc, setCritDesc] = useState("");
  const [critMaxPoints, setCritMaxPoints] = useState(10);
  const [critWeightage, setCritWeightage] = useState(1.0);

  const [feedback, setFeedback] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchEventsAndJudges();
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      loadEventJudgingData(Number(selectedEventId));
    }
  }, [selectedEventId]);

  const fetchEventsAndJudges = async () => {
    try {
      setLoading(true);
      const [eventsData, judgesData] = await Promise.all([
        eventApi.getMyCoordinatedEvents().catch(() => []),
        adminApi.getJudges().catch(() => []),
      ]);
      setEvents(eventsData || []);
      setAllJudges(judgesData || []);

      if (!selectedEventId && eventsData && eventsData.length > 0) {
        setSelectedEventId(String(eventsData[0].id));
      }
      if (judgesData && judgesData.length > 0) {
        setSelectedJudgeUserId(String(judgesData[0].id));
      }
    } catch (err) {
      console.error("Failed to load initial judging data", err);
    } finally {
      setLoading(false);
    }
  };

  const loadEventJudgingData = async (eventId) => {
    try {
      const [assignments, critList] = await Promise.all([
        judgeApi.getEventJudgeAssignments(eventId).catch(() => []),
        judgeApi.getEventCriteria(eventId).catch(() => []),
      ]);
      setAssignedJudges(assignments || []);
      setCriteria(critList || []);
    } catch (err) {
      console.error("Failed to load event judging details", err);
    }
  };

  const handleAssignJudge = async (e) => {
    e.preventDefault();
    if (!selectedEventId || !selectedJudgeUserId) return;
    try {
      setSubmitting(true);
      setFeedback(null);
      await judgeApi.assignJudge({
        event_id: Number(selectedEventId),
        judge_user_id: Number(selectedJudgeUserId),
      });
      setFeedback({ type: "success", text: "Judge assigned successfully!" });
      loadEventJudgingData(Number(selectedEventId));
    } catch (err) {
      console.error("Failed to assign judge", err);
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || "Could not assign judge.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateCriteria = async (e) => {
    e.preventDefault();
    if (!selectedEventId || !critName.trim()) return;
    try {
      setSubmitting(true);
      setFeedback(null);
      await judgeApi.createCriteria({
        event_id: Number(selectedEventId),
        name: critName.trim(),
        description: critDesc.trim(),
        max_points: Number(critMaxPoints),
        weightage: Number(critWeightage),
      });
      setFeedback({ type: "success", text: "Judging criteria added successfully!" });
      setCritName("");
      setCritDesc("");
      loadEventJudgingData(Number(selectedEventId));
    } catch (err) {
      console.error("Failed to create criteria", err);
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || "Failed to create criteria.",
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
            Judging Panel & Evaluation Rubrics
          </h1>
          <p className="text-slate-400 text-sm">
            Appoint verified judges to events and establish standardized scoring rubrics.
          </p>
        </div>

        {/* Event selector */}
        <div className="w-full sm:w-72">
          <select
            value={selectedEventId}
            onChange={(e) => {
              setSelectedEventId(e.target.value);
              setSearchParams({ event_id: e.target.value });
            }}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
          >
            {events.map((evt) => (
              <option key={evt.id} value={evt.id}>
                {evt.title}
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

      {/* Grid: 1. Assigned Judges & 2. Evaluation Criteria */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Judges Panel Section */}
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 space-y-6 flex flex-col justify-between">
          <div className="space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Gavel className="w-5 h-5 text-amber-400" />
                Assigned Judges Panel
              </h2>
              <span className="text-xs font-bold text-slate-400 bg-slate-800 px-2.5 py-1 rounded-lg">
                {assignedJudges.length} Active
              </span>
            </div>

            {/* Assign Form */}
            <form onSubmit={handleAssignJudge} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
              <label className="block text-xs font-semibold text-slate-300">
                Assign Certified Judge to this Event
              </label>
              <div className="flex items-center gap-2">
                <select
                  value={selectedJudgeUserId}
                  onChange={(e) => setSelectedJudgeUserId(e.target.value)}
                  className="flex-1 px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  {allJudges.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.full_name} ({j.email})
                    </option>
                  ))}
                </select>
                <button
                  type="submit"
                  disabled={submitting || allJudges.length === 0}
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold whitespace-nowrap shadow-md shadow-blue-600/20"
                >
                  Assign
                </button>
              </div>
            </form>

            {/* Assigned List */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                Current Event Judges
              </span>
              {assignedJudges.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No judges assigned yet.</p>
              ) : (
                assignedJudges.map((a) => (
                  <div
                    key={a.id}
                    className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-bold text-white">{a.judge_user?.full_name}</div>
                      <div className="text-[11px] text-slate-400">{a.judge_user?.email}</div>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">
                      Authorized
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Evaluation Rubrics Section */}
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 space-y-6 flex flex-col justify-between">
          <div className="space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Sliders className="w-5 h-5 text-indigo-400" />
                Scoring Rubrics & Criteria
              </h2>
              <span className="text-xs font-bold text-slate-400 bg-slate-800 px-2.5 py-1 rounded-lg">
                {criteria.length} Criteria
              </span>
            </div>

            {/* Add Criteria Form */}
            <form onSubmit={handleCreateCriteria} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Criteria Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Technical Innovation & Architecture"
                  value={critName}
                  onChange={(e) => setCritName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Max Points
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={critMaxPoints}
                    onChange={(e) => setCritMaxPoints(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Weightage Factor
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="5.0"
                    value={critWeightage}
                    onChange={(e) => setCritWeightage(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting || !critName.trim()}
                className="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold transition-all shadow-md shadow-indigo-600/20"
              >
                + Add Scoring Criteria
              </button>
            </form>

            {/* Criteria List */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                Configured Rubrics
              </span>
              {criteria.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No criteria configured yet.</p>
              ) : (
                criteria.map((c) => (
                  <div
                    key={c.id}
                    className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-bold text-white">{c.name}</div>
                      <div className="text-[11px] text-slate-400">
                        Weightage: {c.weightage}x • Max: {c.max_points} pts
                      </div>
                    </div>
                    <span className="font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-1 rounded-lg border border-indigo-500/20">
                      /{c.max_points}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
