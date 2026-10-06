import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Users, Search, CheckCircle, Clock, ShieldAlert, Download, Calendar } from "lucide-react";
import { eventApi } from "../../api/eventApi";
import { registrationApi } from "../../api/registrationApi";
import StatusBadge from "../../components/StatusBadge";
import EmptyState from "../../components/EmptyState";

export default function CoordinatorParticipantsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlEventId = searchParams.get("event_id");

  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(urlEventId || "");
  const [participants, setParticipants] = useState([]);
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [loadingList, setLoadingList] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      fetchParticipants(selectedEventId);
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

  const fetchParticipants = async (eventId) => {
    try {
      setLoadingList(true);
      const data = await registrationApi.getEventParticipants(eventId);
      setParticipants(data || []);
    } catch (err) {
      console.error("Failed to load participants", err);
    } finally {
      setLoadingList(false);
    }
  };

  const filtered = participants.filter(
    (p) =>
      p.user?.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      p.user?.email?.toLowerCase().includes(search.toLowerCase()) ||
      p.team?.name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Participant & Team Rosters
          </h1>
          <p className="text-slate-400 text-sm">
            Review registered attendees, squad rosters, and check-in statuses.
          </p>
        </div>

        {/* Event selector dropdown */}
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

      {/* Filter bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search participant or team name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="text-xs text-slate-400">
          Total Participants: <strong className="text-white font-mono">{participants.length}</strong>
        </div>
      </div>

      {/* Roster table */}
      {loadingList ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-slate-900 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : participants.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No Registered Participants"
          description="Nobody has registered for this event yet."
        />
      ) : (
        <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Participant</th>
                  <th className="px-6 py-4">Team</th>
                  <th className="px-6 py-4">Reg Status</th>
                  <th className="px-6 py-4">Payment</th>
                  <th className="px-6 py-4">Attendance Check-in</th>
                  <th className="px-6 py-4">Registered On</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map((reg) => {
                  const hasAttended = reg.attendances && reg.attendances.length > 0;
                  return (
                    <tr key={reg.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-bold text-white text-sm">
                          {reg.user?.full_name || `User #${reg.user_id}`}
                        </div>
                        <div className="text-[11px] text-slate-400">{reg.user?.email}</div>
                      </td>
                      <td className="px-6 py-4">
                        {reg.team ? (
                          <span className="font-semibold text-indigo-300">
                            {reg.team.name}
                          </span>
                        ) : (
                          <span className="text-slate-500 italic">Solo</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={reg.status} />
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                            reg.payment_status === "PAID"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}
                        >
                          {reg.payment_status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {hasAttended ? (
                          <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                            <CheckCircle className="w-3.5 h-3.5" /> Checked In
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-slate-500">
                            <Clock className="w-3.5 h-3.5" /> Awaiting Entry
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-slate-400">
                        {new Date(reg.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
