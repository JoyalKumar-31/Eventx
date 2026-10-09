import React, { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import {
  Users,
  Search,
  CheckCircle,
  Clock,
  ShieldAlert,
  Download,
  Calendar,
  QrCode,
  ShieldCheck,
  Crown,
  Copy,
  Check,
  UserCheck
} from "lucide-react";
import { eventApi } from "../../api/eventApi";
import { registrationApi } from "../../api/registrationApi";
import { teamApi } from "../../api/teamApi";
import StatusBadge from "../../components/StatusBadge";
import EmptyState from "../../components/EmptyState";
import QRPassModal from "../../components/QRPassModal";

export default function CoordinatorParticipantsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlEventId = searchParams.get("event_id");

  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(urlEventId || "");
  const [participants, setParticipants] = useState([]);
  const [teams, setTeams] = useState([]);
  const [activeTab, setActiveTab] = useState("participants"); // "participants" | "teams"
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [loadingList, setLoadingList] = useState(false);
  const [search, setSearch] = useState("");
  const [selectedPassRegId, setSelectedPassRegId] = useState(null);
  const [copiedCode, setCopiedCode] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      loadEventData(selectedEventId);
    }
  }, [selectedEventId]);

  const fetchEvents = async () => {
    try {
      setLoadingEvents(true);
      const data = await eventApi.getMyCoordinatedEvents();
      setEvents(data || []);
      if (!selectedEventId && data && data.length > 0) {
        setSelectedEventId(String(data[0].id));
      }
    } catch (err) {
      console.error("Failed to load events", err);
    } finally {
      setLoadingEvents(false);
    }
  };

  const loadEventData = async (eventId) => {
    try {
      setLoadingList(true);
      const [partsData, teamsData] = await Promise.all([
        registrationApi.getEventParticipants(eventId).catch(() => []),
        teamApi.getEventTeams(eventId).catch(() => []),
      ]);
      setParticipants(partsData || []);
      setTeams(teamsData || []);
      
      // Auto-switch to teams tab if event is team event and no solo participants yet
      const curEvent = events.find((e) => String(e.id) === String(eventId));
      if (curEvent && curEvent.is_team_event && (!partsData || partsData.length === 0) && teamsData && teamsData.length > 0) {
        setActiveTab("teams");
      }
    } catch (err) {
      console.error("Failed to load participant data", err);
    } finally {
      setLoadingList(false);
    }
  };

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2500);
  };

  const filteredParticipants = participants.filter((p) => {
    const q = search.toLowerCase();
    const name = (p.participant_name || p.user?.full_name || "").toLowerCase();
    const email = (p.participant_email || p.user?.email || "").toLowerCase();
    const team = (p.team_name || p.team?.name || "").toLowerCase();
    const regNum = (p.registration_number || "").toLowerCase();
    return name.includes(q) || email.includes(q) || team.includes(q) || regNum.includes(q);
  });

  const filteredTeams = teams.filter((t) => {
    const q = search.toLowerCase();
    const teamName = (t.name || "").toLowerCase();
    const code = (t.invite_code || "").toLowerCase();
    const members = (t.members || []).some(
      (m) => (m.user_name || "").toLowerCase().includes(q) || (m.user_email || "").toLowerCase().includes(q)
    );
    return teamName.includes(q) || code.includes(q) || members;
  });

  const currentEvent = events.find((e) => String(e.id) === String(selectedEventId));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Participant & Team Rosters
          </h1>
          <p className="text-slate-400 text-sm">
            Review registered attendees, squad rosters, gate check-in passes, and team formation status.
          </p>
        </div>

        {/* Event selector dropdown */}
        <div className="w-full sm:w-72">
          <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
            Filter by Event
          </label>
          <select
            value={selectedEventId}
            onChange={(e) => {
              setSelectedEventId(e.target.value);
              setSearchParams({ event_id: e.target.value });
            }}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500 font-semibold"
          >
            {events.map((evt) => (
              <option key={evt.id} value={evt.id}>
                {evt.title} {evt.is_team_event ? "(Team Squad)" : "(Solo)"}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Tabs & Search Filter Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* View Switcher Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-950 border border-slate-800/80 rounded-xl w-full sm:w-auto">
          <button
            onClick={() => setActiveTab("participants")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === "participants"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <UserCheck className="w-3.5 h-3.5" />
            Registered Attendees
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-800 text-slate-300">
              {participants.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("teams")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === "teams"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            Squads & Rosters
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-800 text-slate-300">
              {teams.length}
            </span>
          </button>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder={
              activeTab === "participants"
                ? "Search participant, email, reg number..."
                : "Search squad name, invite code, player..."
            }
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* CONTENT: TAB 1 - Registered Attendees */}
      {activeTab === "participants" && (
        <>
          {loadingList ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 bg-slate-900 rounded-2xl animate-pulse" />
              ))}
            </div>
          ) : filteredParticipants.length === 0 ? (
            <div className="rounded-3xl bg-slate-900/60 border border-slate-800 p-8 text-center space-y-3">
              <EmptyState
                icon={Users}
                title="No Confirmed Attendees Yet"
                description={
                  currentEvent?.is_team_event
                    ? "This is a team event. Switch to the 'Squads & Rosters' tab to see squads currently forming or ready to enroll!"
                    : "Nobody has registered for this event yet."
                }
              />
              {currentEvent?.is_team_event && teams.length > 0 && (
                <button
                  onClick={() => setActiveTab("teams")}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors inline-flex items-center gap-1.5"
                >
                  <Users className="w-3.5 h-3.5" /> View {teams.length} Forming Squads
                </button>
              )}
            </div>
          ) : (
            <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="px-6 py-4">Participant</th>
                      <th className="px-6 py-4">Squad / Format</th>
                      <th className="px-6 py-4">Reg Status</th>
                      <th className="px-6 py-4">Payment</th>
                      <th className="px-6 py-4">Gate Check-in</th>
                      <th className="px-6 py-4">Registered On</th>
                      <th className="px-6 py-4 text-right">Pass</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {filteredParticipants.map((reg) => {
                      const hasAttended =
                        reg.entry_status === "VALID" ||
                        reg.entry_status === "ENTERED" ||
                        (reg.attendance_records && reg.attendance_records.length > 0) ||
                        (reg.attendances && reg.attendances.length > 0);

                      const displayName = reg.participant_name || reg.user?.full_name || `User #${reg.user_id}`;
                      const displayEmail = reg.participant_email || reg.user?.email || "";
                      const displayTeam = reg.team_name || reg.team?.name;
                      const regDate = reg.registered_at || reg.created_at;

                      return (
                        <tr key={reg.id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="px-6 py-4">
                            <div className="font-bold text-white text-sm">
                              {displayName}
                            </div>
                            <div className="text-[11px] text-slate-400 font-mono">
                              {displayEmail} • #{reg.registration_number || reg.id}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            {displayTeam ? (
                              <span className="font-semibold text-indigo-300 inline-flex items-center gap-1">
                                <Users className="w-3.5 h-3.5" /> {displayTeam}
                              </span>
                            ) : (
                              <span className="text-slate-500 italic">Solo Competitor</span>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <StatusBadge status={reg.status} />
                          </td>
                          <td className="px-6 py-4">
                            <span
                              className={`px-2 py-0.5 rounded text-[11px] font-semibold uppercase ${
                                reg.payment_status === "PAID" || reg.payment_status === "FREE"
                                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                  : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                              }`}
                            >
                              {reg.payment_status || "FREE"}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            {hasAttended ? (
                              <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                                <CheckCircle className="w-3.5 h-3.5" /> Checked In
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-slate-400">
                                <Clock className="w-3.5 h-3.5" /> Awaiting Entry
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 text-slate-400 font-mono">
                            {regDate ? new Date(regDate).toLocaleDateString() : "--"}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() => setSelectedPassRegId(reg.id)}
                              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                              title="View Digital Pass"
                            >
                              <QrCode className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* CONTENT: TAB 2 - Squads & Rosters */}
      {activeTab === "teams" && (
        <>
          {loadingList ? (
            <div className="space-y-4">
              {[1, 2].map((i) => (
                <div key={i} className="h-32 bg-slate-900 rounded-3xl animate-pulse" />
              ))}
            </div>
          ) : filteredTeams.length === 0 ? (
            <EmptyState
              icon={Users}
              title="No Squads Formed For This Event"
              description="No student squads have been created yet for this tournament."
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredTeams.map((team) => {
                const memberCount = team.members ? team.members.length : 0;
                const minSize = team.min_team_size || 2;
                const maxSize = team.max_team_size || 5;
                const isEnrolled = team.is_registered || team.status === "COMPLETE";

                return (
                  <div
                    key={team.id}
                    className="p-6 rounded-3xl bg-slate-900 border border-slate-800 flex flex-col justify-between shadow-lg hover:border-slate-700 transition-all space-y-5"
                  >
                    <div>
                      {/* Squad Header */}
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-lg font-bold text-white tracking-tight">
                              {team.name}
                            </h3>
                            {isEnrolled ? (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                                Enrolled ✓
                              </span>
                            ) : (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                                Forming Squad
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-400 mt-1">
                            Formed on {new Date(team.created_at).toLocaleDateString()}
                          </p>
                        </div>

                        <span className="px-3 py-1 rounded-xl text-xs font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                          {memberCount} / {maxSize} Members
                        </span>
                      </div>

                      {/* Squad Invite Code Bar */}
                      <div className="mt-4 p-3 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between gap-2">
                        <div>
                          <span className="text-[10px] uppercase font-bold text-slate-500 block">
                            Squad Invite Code
                          </span>
                          <span className="text-sm font-mono font-bold tracking-widest text-emerald-400">
                            {team.invite_code}
                          </span>
                        </div>
                        <button
                          onClick={() => handleCopyCode(team.invite_code)}
                          className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors flex items-center gap-1.5 text-xs font-medium cursor-pointer"
                          title="Copy Code"
                        >
                          {copiedCode === team.invite_code ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                              <span className="text-emerald-400 text-[11px] font-semibold">Copied!</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5" />
                              <span className="text-[11px]">Copy Code</span>
                            </>
                          )}
                        </button>
                      </div>

                      {/* Squad Members Roster */}
                      <div className="mt-4 space-y-2">
                        <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400">
                          <span>Roster ({memberCount} / {minSize} min)</span>
                          {memberCount < minSize && (
                            <span className="text-amber-400 text-[11px] font-normal lowercase">
                              Requires {minSize - memberCount} more to confirm
                            </span>
                          )}
                        </div>

                        <div className="space-y-1.5">
                          {team.members && team.members.length > 0 ? (
                            team.members.map((m) => (
                              <div
                                key={m.id}
                                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs"
                              >
                                <div className="flex items-center gap-2">
                                  {m.user_id === team.leader_id ? (
                                    <Crown className="w-4 h-4 text-amber-400" title="Squad Leader" />
                                  ) : (
                                    <div className="w-2 h-2 rounded-full bg-slate-600" />
                                  )}
                                  <div>
                                    <span className="font-bold text-white">{m.user_name}</span>
                                    <span className="text-[11px] text-slate-400 block font-mono">{m.user_email}</span>
                                  </div>
                                </div>
                                <span className="text-[11px] font-mono text-slate-400">
                                  {m.user_id === team.leader_id ? "Leader" : "Member"}
                                </span>
                              </div>
                            ))
                          ) : (
                            <p className="text-xs text-slate-500 italic">No members joined yet.</p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Squad Footer status */}
                    <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                      <span>Status: <strong className="text-white">{isEnrolled ? "Officially Registered" : "Awaiting Formation"}</strong></span>
                      {team.registration_id && (
                        <button
                          onClick={() => setSelectedPassRegId(team.registration_id)}
                          className="text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 cursor-pointer"
                        >
                          <QrCode className="w-3.5 h-3.5" /> View Squad Pass
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {selectedPassRegId && (
        <QRPassModal
          registrationId={selectedPassRegId}
          onClose={() => setSelectedPassRegId(null)}
        />
      )}
    </div>
  );
}
