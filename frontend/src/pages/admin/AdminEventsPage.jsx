import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Calendar,
  Search,
  Globe,
  XCircle,
  Trash2,
  ExternalLink,
  Users,
  DollarSign,
  Filter,
} from "lucide-react";
import { eventApi } from "../../api/eventApi";
import StatusBadge from "../../components/StatusBadge";
import EmptyState from "../../components/EmptyState";

export default function AdminEventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const data = await eventApi.getEvents();
      setEvents(data || []);
    } catch (err) {
      console.error("Failed to load events", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePublishToggle = async (eventId, currentStatus) => {
    try {
      if (currentStatus === "PUBLISHED") {
        await eventApi.unpublishEvent(eventId);
      } else {
        await eventApi.publishEvent(eventId);
      }
      fetchEvents();
    } catch (err) {
      console.error("Failed to toggle publish status", err);
      alert("Failed to update event publication state.");
    }
  };

  const handleDelete = async (eventId) => {
    if (!window.confirm("Permanently delete this event from the fest system?")) return;
    try {
      await eventApi.deleteEvent(eventId);
      fetchEvents();
    } catch (err) {
      console.error("Failed to delete event", err);
      alert("Failed to delete event.");
    }
  };

  const filtered = events.filter((e) => {
    const matchesSearch =
      e.title?.toLowerCase().includes(search.toLowerCase()) ||
      e.coordinator?.full_name?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === "ALL" || e.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Festival Event Catalog Oversight
        </h1>
        <p className="text-slate-400 text-sm">
          Supervise all competitive tracks, published statuses, registrations, and coordinator assignments.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by event or coordinator..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          {["ALL", "PUBLISHED", "DRAFT", "COMPLETED", "CANCELLED"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                statusFilter === st
                  ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-16 bg-slate-900 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No Events Found"
          description="No events match your current filter parameters."
        />
      ) : (
        <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Event Details</th>
                  <th className="px-6 py-4">Coordinator</th>
                  <th className="px-6 py-4">Format & Fee</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Registrations</th>
                  <th className="px-6 py-4 text-right">Admin Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map((evt) => (
                  <tr key={evt.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-white text-sm hover:text-purple-400">
                        <Link to={`/events/${evt.id}`}>{evt.title}</Link>
                      </div>
                      <div className="text-[11px] text-slate-400">
                        {evt.category?.name || "General"} • {evt.event_type}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-white font-medium">
                        {evt.coordinator?.full_name || "Unassigned"}
                      </div>
                      <div className="text-[10px] text-slate-500">{evt.coordinator?.email}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-semibold text-slate-300">{evt.event_format}</span>
                      <div className="text-[11px] text-emerald-400 font-mono">
                        {evt.registration_fee > 0 ? `₹${evt.registration_fee}` : "Free"}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={evt.status} />
                    </td>
                    <td className="px-6 py-4 font-mono font-bold text-white">
                      {evt.registrations?.length || 0} / {evt.max_participants || "∞"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/events/${evt.id}`}
                          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                          title="View Public Event Page"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </Link>

                        <button
                          onClick={() => handlePublishToggle(evt.id, evt.status)}
                          className={`p-2 rounded-xl transition-colors ${
                            evt.status === "PUBLISHED"
                              ? "bg-amber-500/10 hover:bg-amber-500/20 text-amber-400"
                              : "bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400"
                          }`}
                          title={evt.status === "PUBLISHED" ? "Unpublish Event" : "Publish Event"}
                        >
                          {evt.status === "PUBLISHED" ? (
                            <XCircle className="w-3.5 h-3.5" />
                          ) : (
                            <Globe className="w-3.5 h-3.5" />
                          )}
                        </button>

                        <button
                          onClick={() => handleDelete(evt.id)}
                          className="p-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-colors"
                          title="Delete Event"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
