import React, { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Users,
  UserPlus,
  Copy,
  Check,
  Crown,
  Calendar,
  AlertCircle,
  PlusCircle,
  Hash,
  ShieldCheck,
  ArrowRight,
  CreditCard,
  QrCode,
} from "lucide-react";
import { teamApi } from "../../api/teamApi";
import { eventApi } from "../../api/eventApi";
import { registrationApi } from "../../api/registrationApi";
import { useAuth } from "../../auth/AuthContext";
import EmptyState from "../../components/EmptyState";
import { PaymentModal } from "../../components/PaymentModal";

export default function StudentTeamsPage() {
  const [searchParams] = useSearchParams();
  const urlEventId = searchParams.get("event");

  const { user } = useAuth();
  const [teams, setTeams] = useState([]);
  const [teamEvents, setTeamEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copiedCode, setCopiedCode] = useState(null);

  // Modals / Form toggles
  const [showCreateModal, setShowCreateModal] = useState(Boolean(urlEventId));
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [paymentReg, setPaymentReg] = useState(null);

  // Form states
  const [newTeamName, setNewTeamName] = useState("");
  const [selectedEventId, setSelectedEventId] = useState(urlEventId || "");
  const [inviteCodeInput, setInviteCodeInput] = useState("");
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [registeringTeamId, setRegisteringTeamId] = useState(null);

  useEffect(() => {
    fetchTeamsAndEvents();
  }, []);

  const fetchTeamsAndEvents = async () => {
    try {
      setLoading(true);
      const [teamsData, eventsData] = await Promise.all([
        teamApi.getMyTeams().catch(() => []),
        eventApi.getEvents().catch(() => []),
      ]);
      setTeams(teamsData || []);

      // Filter events that require team format
      const teamEligible = (eventsData || []).filter(
        (e) => e.is_team_event === true || e.event_format === "TEAM" || e.event_format === "HYBRID"
      );
      setTeamEvents(teamEligible);

      if (urlEventId) {
        setSelectedEventId(String(urlEventId));
      } else if (teamEligible.length > 0 && !selectedEventId) {
        setSelectedEventId(String(teamEligible[0].id));
      }
    } catch (err) {
      console.error("Failed to load teams", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2500);
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    if (!newTeamName.trim() || !selectedEventId) return;
    try {
      setSubmitting(true);
      setActionError(null);
      await teamApi.createTeam({
        name: newTeamName.trim(),
        event_id: Number(selectedEventId),
      });
      setActionSuccess(`Squad "${newTeamName}" formed successfully! Invite your teammates using your unique squad code.`);
      setShowCreateModal(false);
      setNewTeamName("");
      fetchTeamsAndEvents();
    } catch (err) {
      console.error("Failed to create team", err);
      setActionError(err.response?.data?.detail || "Could not form squad. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleJoinTeam = async (e) => {
    e.preventDefault();
    if (!inviteCodeInput.trim()) return;
    try {
      setSubmitting(true);
      setActionError(null);
      await teamApi.joinTeam({
        invite_code: inviteCodeInput.trim().toUpperCase(),
      });
      setActionSuccess("Joined squad successfully! Check your digital passes.");
      setShowJoinModal(false);
      setInviteCodeInput("");
      fetchTeamsAndEvents();
    } catch (err) {
      console.error("Failed to join team", err);
      setActionError(err.response?.data?.detail || "Invalid invite code or squad is at maximum capacity.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRegisterSquad = async (team) => {
    try {
      setRegisteringTeamId(team.id);
      setActionError(null);
      setActionSuccess(null);

      const reg = await registrationApi.register({
        event_id: team.event_id,
        team_id: team.id,
      });

      if (team.registration_fee > 0 && reg.payment_status !== "PAID" && reg.payment_status !== "FREE") {
        setPaymentReg(reg);
      } else {
        setActionSuccess(`Squad "${team.name}" is officially enrolled! Passes are now active for all squad members.`);
      }
      fetchTeamsAndEvents();
    } catch (err) {
      console.error("Squad registration error", err);
      setActionError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Could not complete squad registration. Ensure minimum team size is met."
      );
    } finally {
      setRegisteringTeamId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Team Squads & Rosters
          </h1>
          <p className="text-slate-400 text-sm">
            Form competitive squads, invite teammates via unique invite codes, and enroll rosters in fest tournaments.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setActionError(null);
              setActionSuccess(null);
              setShowJoinModal(true);
            }}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-all flex items-center gap-2 border border-slate-700"
          >
            <Hash className="w-4 h-4 text-emerald-400" /> Join via Code
          </button>
          <button
            onClick={() => {
              setActionError(null);
              setActionSuccess(null);
              setShowCreateModal(true);
            }}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all flex items-center gap-2 shadow-lg shadow-indigo-600/20"
          >
            <PlusCircle className="w-4 h-4" /> Create New Team
          </button>
        </div>
      </div>

      {/* Notifications / Alerts */}
      {actionSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center justify-between">
          <span>{actionSuccess}</span>
          <button onClick={() => setActionSuccess(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}
      {actionError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center justify-between">
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Teams Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <div key={i} className="h-64 rounded-2xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : teams.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No Active Squads"
          description="You haven't created or joined any team yet. Form a squad to participate in esports tournaments, hackathons, and group battles!"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {teams.map((team) => {
            const isLeader = team.leader_id === user?.id;
            const minSize = team.min_team_size || 2;
            const maxSize = team.max_team_size || 4;
            const memberCount = team.members?.length || 0;
            const meetsMinSize = memberCount >= minSize;
            const isRegistered = team.is_registered || team.status === "COMPLETE";

            return (
              <div
                key={team.id}
                className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-5 flex flex-col justify-between shadow-xl hover:border-slate-700 transition-all"
              >
                <div>
                  {/* Team header */}
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div>
                      <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Users className="w-5 h-5 text-indigo-400" />
                        {team.name}
                      </h3>
                      <p className="text-xs text-slate-400 mt-1">
                        Competition: <strong className="text-slate-200">{team.event_title || team.event?.title || `Event #${team.event_id}`}</strong>
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      {isRegistered ? (
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                          Registered ✓
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                          Forming Squad
                        </span>
                      )}
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                        {memberCount}/{maxSize}
                      </span>
                    </div>
                  </div>

                  {/* Invite Code Box */}
                  <div className="p-3.5 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between gap-2 mt-4">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">
                        Squad Invite Code
                      </span>
                      <span className="text-base font-mono font-bold tracking-widest text-emerald-400">
                        {team.invite_code}
                      </span>
                    </div>
                    <button
                      onClick={() => handleCopyCode(team.invite_code)}
                      className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors flex items-center gap-1.5 text-xs font-medium"
                      title="Copy Invite Code"
                    >
                      {copiedCode === team.invite_code ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-emerald-400 font-semibold">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copy Code</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Member Roster List */}
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      <span>Squad Roster ({memberCount} / {minSize} min)</span>
                      {memberCount < minSize && (
                        <span className="text-amber-400 text-[11px] font-normal lowercase">
                          Need {minSize - memberCount} more to enroll
                        </span>
                      )}
                    </div>
                    <div className="space-y-1.5">
                      {team.members && team.members.length > 0 ? (
                        team.members.map((member) => (
                          <div
                            key={member.id}
                            className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs"
                          >
                            <div className="flex items-center gap-2">
                              {member.user_id === team.leader_id ? (
                                <Crown className="w-4 h-4 text-amber-400" title="Team Leader" />
                              ) : (
                                <div className="w-2 h-2 rounded-full bg-slate-600" />
                              )}
                              <span className="font-semibold text-white">
                                {member.user_name || `Member #${member.user_id}`}
                              </span>
                            </div>
                            <span className="text-slate-500 text-[11px] font-mono">
                              {member.user_id === team.leader_id ? "Squad Leader" : "Teammate"}
                            </span>
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-slate-500 italic">No members yet.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Team Footer Action Bar */}
                <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                  <Link
                    to={`/events/${team.event_id}`}
                    className="text-slate-400 hover:text-white transition-colors"
                  >
                    View Competition Rulebook →
                  </Link>

                  <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
                    {isRegistered ? (
                      <Link
                        to="/student/passes"
                        className="w-full sm:w-auto px-4 py-2 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 font-semibold border border-emerald-500/30 flex items-center justify-center gap-1.5"
                      >
                        <QrCode className="w-3.5 h-3.5" /> View QR Passes
                      </Link>
                    ) : isLeader ? (
                      <button
                        onClick={() => handleRegisterSquad(team)}
                        disabled={registeringTeamId === team.id || !meetsMinSize}
                        className="w-full sm:w-auto px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold transition-all shadow-md shadow-indigo-600/20 flex items-center justify-center gap-1.5"
                        title={!meetsMinSize ? `Need at least ${minSize} members` : "Enroll squad for event"}
                      >
                        {registeringTeamId === team.id ? (
                          "Enrolling..."
                        ) : (
                          <>
                            <ShieldCheck className="w-3.5 h-3.5" /> Register Squad
                          </>
                        )}
                      </button>
                    ) : (
                      <span className="text-slate-500 italic text-[11px]">
                        Awaiting leader to enroll squad
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Team Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-indigo-400" /> Form Squad for Tournament
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateTeam} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Squad Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CyberKnights / Team Delta"
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Target Competition Track *
                </label>
                <select
                  value={selectedEventId}
                  onChange={(e) => setSelectedEventId(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  {teamEvents.map((evt) => (
                    <option key={evt.id} value={evt.id}>
                      {evt.title} ({evt.min_team_size || 2}-{evt.max_team_size || 4} members)
                    </option>
                  ))}
                </select>
                {teamEvents.length === 0 && (
                  <p className="text-[11px] text-amber-400 mt-1">
                    No active team competitions currently open.
                  </p>
                )}
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || teamEvents.length === 0}
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30"
                >
                  {submitting ? "Creating Squad..." : "Create Squad"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join Team Modal */}
      {showJoinModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Hash className="w-5 h-5 text-emerald-400" /> Join Squad via Invite Code
              </h3>
              <button
                onClick={() => setShowJoinModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleJoinTeam} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Team Invite Code *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. FEST-9F8A2D"
                  value={inviteCodeInput}
                  onChange={(e) => setInviteCodeInput(e.target.value.toUpperCase())}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm font-mono tracking-widest text-white placeholder-slate-500 uppercase focus:outline-none focus:border-emerald-500"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Obtain this 6-10 character code from your squad leader.
                </p>
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowJoinModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !inviteCodeInput.trim()}
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30"
                >
                  {submitting ? "Joining..." : "Join Squad"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Payment Modal if squad event requires registration fee */}
      {paymentReg && (
        <PaymentModal
          registration={paymentReg}
          onSuccess={() => {
            setPaymentReg(null);
            setActionSuccess("Squad payment cleared and entry passes confirmed!");
            fetchTeamsAndEvents();
          }}
          onClose={() => setPaymentReg(null)}
        />
      )}
    </div>
  );
}
