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
  Clock,
  RefreshCw,
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
  const [evaluatedMap, setEvaluatedMap] = useState({});

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [refreshingRoster, setRefreshingRoster] = useState(false);
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
        setSelectedEventId(String(data[0].id || data[0].event_id));
      }
    } catch (err) {
      console.error("Failed to load assigned events", err);
    } finally {
      setLoading(false);
    }
  };

  const isAttendeeCheckedIn = (p) => {
    if (!p) return false;
    return Boolean(
      p.has_attended === true ||
      p.is_attended === true ||
      p.status === "ATTENDED" ||
      p.entry_status === "VALID" ||
      p.entry_status === "ENTERED"
    );
  };

  const processEvaluatedScores = (scoreList) => {
    const evalMap = {};
    (scoreList || []).forEach((s) => {
      const regKey = String(s.registration_id);
      if (!evalMap[regKey]) {
        evalMap[regKey] = {
          total: 0,
          scores: {},
          remarks: s.remarks || "",
          submittedAt: s.submitted_at,
        };
      }
      evalMap[regKey].scores[s.criteria_id] = Number(s.score_value);
      evalMap[regKey].total += Number(s.score_value);
      if (s.remarks && !evalMap[regKey].remarks) {
        evalMap[regKey].remarks = s.remarks;
      }
    });
    return evalMap;
  };

  const loadEventData = async (eventId) => {
    try {
      const [parts, critList, existingScores] = await Promise.all([
        registrationApi.getEventParticipants(eventId).catch(() => []),
        judgeApi.getEventCriteria(eventId).catch(() => []),
        judgeApi.getEventScores(eventId).catch(() => []),
      ]);
      setParticipants(parts || []);
      setCriteria(critList || []);

      const evalMap = processEvaluatedScores(existingScores);
      setEvaluatedMap(evalMap);

      setSelectedRegId((prev) => {
        const targetRegId = (prev && parts && parts.some((p) => String(p.id) === String(prev)))
          ? String(prev)
          : (parts && parts.length > 0 ? String(parts[0].id) : "");

        if (targetRegId && evalMap[targetRegId]) {
          setScores({ ...evalMap[targetRegId].scores });
          setRemarks(evalMap[targetRegId].remarks || "");
        } else {
          const initial = {};
          (critList || []).forEach((c) => {
            const maxVal = c.max_score || c.max_points || 10;
            initial[c.id] = Math.round(maxVal * 0.7);
          });
          setScores(initial);
          setRemarks("");
        }
        return targetRegId;
      });
    } catch (err) {
      console.error("Failed to load event participants or criteria", err);
    }
  };

  const handleRefreshRoster = async () => {
    if (!selectedEventId || refreshingRoster) return;
    try {
      setRefreshingRoster(true);
      await loadEventData(Number(selectedEventId));
    } finally {
      setRefreshingRoster(false);
    }
  };

  const handleSelectParticipant = (regId) => {
    setSelectedRegId(regId);
    setFeedback(null);
    if (evaluatedMap[regId]) {
      setScores({ ...evaluatedMap[regId].scores });
      setRemarks(evaluatedMap[regId].remarks || "");
    } else {
      const initial = {};
      criteria.forEach((c) => {
        const maxVal = c.max_score || c.max_points || 10;
        initial[c.id] = Math.round(maxVal * 0.7);
      });
      setScores(initial);
      setRemarks("");
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

    if (!isAttendeeCheckedIn(activeParticipant)) {
      setFeedback({
        type: "error",
        text: "Gate check-in required! Cannot submit scores: Participant has not completed entrance QR scan check-in yet.",
      });
      return;
    }

    try {
      setSubmitting(true);
      setFeedback(null);

      const scorePayload = criteria.map((c) => ({
        criteria_id: c.id,
        score_value: Number(scores[c.id] || 0),
        score: Number(scores[c.id] || 0),
      }));

      await judgeApi.submitScores(Number(selectedEventId), {
        registration_id: Number(selectedRegId),
        scores: scorePayload,
        remarks: remarks.trim(),
      });

      // Re-fetch scores to sync state
      const updatedScores = await judgeApi.getEventScores(Number(selectedEventId)).catch(() => []);
      const evalMap = processEvaluatedScores(updatedScores);
      setEvaluatedMap(evalMap);

      const isUpdate = Boolean(evaluatedMap[selectedRegId]);
      setFeedback({
        type: "success",
        text: isUpdate
          ? "Official scorecard updated & saved! Standings synced with Event Coordinator."
          : "Official scorecard submitted & saved! Transmitted to Event Coordinator.",
      });
    } catch (err) {
      console.error("Failed to submit score", err);
      const detailMsg = err.response?.data?.detail;
      const errorText = typeof detailMsg === "string" ? detailMsg : (detailMsg?.message || "Could not submit score. Please try again.");
      setFeedback({
        type: "error",
        text: errorText,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const activeParticipant = participants.find((p) => String(p.id) === String(selectedRegId));
  const selectedEvent = assignedEvents.find(
    (a) => String(a.id || a.event_id) === String(selectedEventId)
  );

  const isEventCommenced = () => {
    if (!selectedEvent) return true;
    if (selectedEvent.status === "ONGOING" || selectedEvent.status === "COMPLETED") return true;
    if (selectedEvent.start_time) {
      const startTime = new Date(selectedEvent.start_time);
      const now = new Date();
      if (now >= startTime || now.toDateString() === startTime.toDateString()) return true;
    }
    return false;
  };

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
            {assignedEvents.map((a) => {
              const eventId = a.id || a.event_id;
              const title = a.title || a.event?.title || `Event #${eventId}`;
              return (
                <option key={a.id} value={eventId}>
                  {title}
                </option>
              );
            })}
          </select>
        </div>
      </div>

      {!isEventCommenced() && selectedEvent && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-amber-400" />
          <div className="text-xs">
            <strong className="block font-bold text-white text-sm mb-0.5">Competition Not Commenced</strong>
            Official judging and scorecards unlock on event day ({new Date(selectedEvent.start_time).toLocaleDateString()}) once the competition has started.
          </div>
        </div>
      )}

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
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Users className="w-4 h-4 text-amber-400" />
                  Select Competitor
                </h3>
                <button
                  type="button"
                  onClick={handleRefreshRoster}
                  disabled={refreshingRoster}
                  title="Refresh Roster & Gate Check-Ins"
                  className="p-1 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${refreshingRoster ? "animate-spin text-amber-400" : ""}`} />
                </button>
              </div>
              <div className="text-right">
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {Object.keys(evaluatedMap).length} / {participants.length} Evaluated
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">
                  {participants.filter(isAttendeeCheckedIn).length} / {participants.length} Gate Approved
                </span>
              </div>
            </div>

            <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">
              {participants.map((p) => {
                const isSelected = String(p.id) === String(selectedRegId);
                const name = p.participant_name || p.user?.full_name || `Participant #${p.user_id}`;
                const team = p.team_name || p.team?.name;
                const isEvaluated = Boolean(evaluatedMap[String(p.id)]);
                const evalData = evaluatedMap[String(p.id)];
                const isCheckedIn = isAttendeeCheckedIn(p);

                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => handleSelectParticipant(String(p.id))}
                    className={`w-full text-left p-3.5 rounded-2xl transition-all border ${
                      isSelected
                        ? isEvaluated
                          ? "bg-emerald-500/15 border-emerald-500/60 shadow-lg shadow-emerald-500/10"
                          : isCheckedIn
                          ? "bg-amber-500/10 border-amber-500/50 shadow-lg shadow-amber-500/5"
                          : "bg-rose-500/10 border-rose-500/40 shadow-lg shadow-rose-500/5"
                        : isEvaluated
                        ? "bg-slate-950/80 border-emerald-500/25 hover:border-emerald-500/50"
                        : isCheckedIn
                        ? "bg-slate-950/60 border-slate-800/80 hover:border-slate-700"
                        : "bg-slate-950/40 border-slate-800/50 opacity-80 hover:opacity-100 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="font-bold text-white text-sm truncate">
                        {name}
                      </div>
                      {isEvaluated ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/30 shrink-0">
                          <CheckCircle2 className="w-3 h-3" /> {evalData.total.toFixed(1)} pts
                        </span>
                      ) : isCheckedIn ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 shrink-0">
                          <CheckCircle2 className="w-2.5 h-2.5" /> Gate Cleared
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20 shrink-0">
                          <Clock className="w-2.5 h-2.5" /> Gate Pending
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400 mt-1 flex items-center justify-between">
                      <span>{team ? `Squad: ${team}` : "Solo Entry"}</span>
                      <span className="font-mono text-[11px] text-slate-500">#{p.registration_number || p.id}</span>
                    </div>
                    {!isEvaluated && (
                      <div className="mt-1 text-[10px] font-medium flex items-center gap-1">
                        {isCheckedIn ? (
                          <span className="text-amber-400/80 flex items-center gap-1">
                            <Clock className="w-3 h-3" /> Cleared for Scoring
                          </span>
                        ) : (
                          <span className="text-rose-400/90 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" /> Gate QR Check-in Required
                          </span>
                        )}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Rubric Evaluation Form Column */}
          <div className="lg:col-span-2 p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 space-y-6 flex flex-col justify-between shadow-xl">
            <div className="space-y-6">
              {/* Active competitor header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                <div>
                  <span className="text-[10px] uppercase font-bold text-amber-400 tracking-wider block">
                    Evaluating Competitor
                  </span>
                  <div className="flex items-center gap-2 flex-wrap mt-0.5">
                    <h2 className="text-xl font-extrabold text-white">
                      {activeParticipant?.participant_name || activeParticipant?.user?.full_name || "Selected Participant"}
                    </h2>
                    {isAttendeeCheckedIn(activeParticipant) ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        <CheckCircle2 className="w-3 h-3" /> Gate Checked-In
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        <Clock className="w-3 h-3" /> Gate Check-In Pending
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {activeParticipant?.team_name ? `Team: ${activeParticipant.team_name}` : "Solo Entry"} • Registration #{activeParticipant?.registration_number || activeParticipant?.id}
                  </p>
                </div>

                <div className="text-right bg-slate-950 p-3 rounded-2xl border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">
                    Tabulated Total
                  </span>
                  <div className="text-2xl font-black text-amber-400 font-mono">
                    {calculateTotal()} <span className="text-xs text-slate-400 font-normal">pts</span>
                  </div>
                </div>
              </div>

              {/* Gate Attendance Banner */}
              {!isAttendeeCheckedIn(activeParticipant) ? (
                <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-300 flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 shrink-0 text-amber-400 mt-0.5" />
                  <div className="space-y-1">
                    <div className="font-bold text-white text-sm flex items-center gap-2">
                      Gate Attendance Approval Required
                      <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        Awaiting QR Scan
                      </span>
                    </div>
                    <p className="text-xs text-amber-200/90 leading-relaxed">
                      This participant has not yet been verified at the venue gate. Festival regulations mandate that competitors must have their attendance QR code scanned and approved at the entrance before judges can award official marks.
                    </p>
                    <p className="text-[11px] text-slate-400 pt-0.5">
                      💡 Once the gate coordinator scans this student's ticket, click <strong>"Refresh Roster"</strong> to immediately unlock scorecard evaluation.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2.5 text-xs text-emerald-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>
                    <strong>Gate Check-In Approved</strong>: Participant verified at the venue gate. Cleared for judicial evaluation & rubric scoring.
                  </span>
                </div>
              )}

              {/* Status banner if already evaluated */}
              {Boolean(evaluatedMap[String(selectedRegId)]) && (
                <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-emerald-300">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
                      <CheckCircle2 className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="font-bold text-white text-sm flex items-center gap-2">
                        Official Scorecard Submitted & Saved
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                          Saved in System
                        </span>
                      </div>
                      <div className="text-xs text-emerald-400/90 mt-0.5">
                        Tabulated Score: <strong className="text-white font-mono">{calculateTotal()} pts</strong> • Official scorecard transmitted to Event Coordinator.
                      </div>
                    </div>
                  </div>
                  {evaluatedMap[String(selectedRegId)]?.submittedAt && (
                    <span className="text-[11px] font-mono text-slate-400 self-end sm:self-center">
                      Recorded {new Date(evaluatedMap[String(selectedRegId)].submittedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </div>
              )}

              {/* Rubric Sliders / Inputs */}
              {criteria.length === 0 ? (
                <div className="p-8 text-center bg-slate-950 rounded-2xl border border-slate-800">
                  <AlertCircle className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                  <p className="text-xs text-slate-400">
                    No evaluation criteria have been established for this event yet by the coordinator.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {criteria.map((c) => {
                    const maxScore = c.max_score || c.max_points || 10;
                    const val = scores[c.id] || 0;
                    return (
                      <div
                        key={c.id}
                        className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-3"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-bold text-white text-sm">{c.name}</div>
                            {c.description && (
                              <div className="text-xs text-slate-400 mt-0.5">{c.description}</div>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] text-slate-400 font-mono">
                              ({c.weightage}x weight)
                            </span>
                            <span className="font-mono font-bold text-base text-amber-400">
                              {val} / {maxScore}
                            </span>
                          </div>
                        </div>

                        <div className={`flex items-center gap-4 ${!isAttendeeCheckedIn(activeParticipant) ? "opacity-40 pointer-events-none" : ""}`}>
                          <input
                            type="range"
                            min="0"
                            max={maxScore}
                            step="1"
                            disabled={!isAttendeeCheckedIn(activeParticipant)}
                            value={val}
                            onChange={(e) => handleScoreChange(c.id, e.target.value)}
                            className="flex-1 accent-amber-500 h-2 bg-slate-800 rounded-lg cursor-pointer disabled:cursor-not-allowed"
                          />
                          <input
                            type="number"
                            min="0"
                            max={maxScore}
                            disabled={!isAttendeeCheckedIn(activeParticipant)}
                            value={val}
                            onChange={(e) => handleScoreChange(c.id, e.target.value)}
                            className="w-16 px-2 py-1 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-center text-white focus:outline-none focus:border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Remarks Box */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-amber-400" />
                  Judicial Evaluation Remarks & Feedback
                </label>
                <textarea
                  rows="3"
                  disabled={!isAttendeeCheckedIn(activeParticipant)}
                  placeholder={
                    isAttendeeCheckedIn(activeParticipant)
                      ? "Constructive feedback, technical critique, or performance notes..."
                      : "Awaiting gate attendance check-in before entering evaluation notes..."
                  }
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 disabled:opacity-40 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Submit Action Button */}
            <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="text-xs text-slate-400">
                {!isAttendeeCheckedIn(activeParticipant) ? (
                  <span className="text-rose-400/90 flex items-center gap-1.5 font-medium">
                    <AlertCircle className="w-3.5 h-3.5" /> Gate entry pass QR scan approval required before scoring.
                  </span>
                ) : Boolean(evaluatedMap[String(selectedRegId)]) ? (
                  <span className="text-emerald-400 flex items-center gap-1.5 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Scorecard active. Modifying sliders will update standings.
                  </span>
                ) : (
                  <span className="text-amber-400/90 flex items-center gap-1.5 font-medium">
                    <Clock className="w-3.5 h-3.5" /> Cleared for evaluation. Submit official scores to record.
                  </span>
                )}
              </div>

              <button
                type="submit"
                disabled={
                  submitting ||
                  criteria.length === 0 ||
                  !isEventCommenced() ||
                  !isAttendeeCheckedIn(activeParticipant)
                }
                className={`px-6 py-3 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-bold text-xs transition-all shadow-lg flex items-center gap-2 ${
                  !isAttendeeCheckedIn(activeParticipant)
                    ? "bg-slate-800 text-slate-400 border border-slate-700 cursor-not-allowed"
                    : Boolean(evaluatedMap[String(selectedRegId)])
                    ? "bg-emerald-500 hover:bg-emerald-400 shadow-emerald-500/20"
                    : "bg-amber-500 hover:bg-amber-400 shadow-amber-500/20"
                }`}
              >
                {!isAttendeeCheckedIn(activeParticipant) ? (
                  <Clock className="w-4 h-4 text-amber-400" />
                ) : (
                  <CheckCircle2 className="w-4 h-4" />
                )}
                {!isEventCommenced()
                  ? "Scoring Opens on Event Day"
                  : !isAttendeeCheckedIn(activeParticipant)
                  ? "Awaiting Gate Check-In Approval (QR Scan Required)"
                  : submitting
                  ? (Boolean(evaluatedMap[String(selectedRegId)]) ? "Updating Scorecard..." : "Submitting Official Scorecard...")
                  : (Boolean(evaluatedMap[String(selectedRegId)]) ? "Update Official Scorecard" : "Submit Official Scorecard")}
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
