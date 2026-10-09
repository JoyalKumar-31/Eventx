import React, { useState, useEffect } from "react";
import { Activity, Search, Shield, Filter, Clock, User, Server } from "lucide-react";
import { adminApi } from "../../api/adminApi";
import EmptyState from "../../components/EmptyState";

export default function AdminAuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("ALL");

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await adminApi.getAuditLogs({ limit: 100 });
      setLogs(data || []);
    } catch (err) {
      console.error("Failed to load audit logs", err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = logs.filter((l) => {
    const action = l.action || "";
    const resType = l.entity_type || l.resource_type || "";
    const uName = l.user_name || l.user?.full_name || "";
    const uEmail = l.user_email || l.user?.email || "";

    const matchesSearch =
      action.toLowerCase().includes(search.toLowerCase()) ||
      resType.toLowerCase().includes(search.toLowerCase()) ||
      uName.toLowerCase().includes(search.toLowerCase()) ||
      uEmail.toLowerCase().includes(search.toLowerCase());
    const matchesAction = actionFilter === "ALL" || action === actionFilter;
    return matchesSearch && matchesAction;
  });

  const uniqueActions = Array.from(new Set(logs.map((l) => l.action))).filter(Boolean);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          System Audit Trail & Security Ledger
        </h1>
        <p className="text-slate-400 text-sm">
          Cryptographically tracked audit logs for administrative, operational, and RBAC actions.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by action, user, or resource..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Action:
          </span>
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-purple-500"
          >
            <option value="ALL">All Actions</option>
            {uniqueActions.map((act) => (
              <option key={act} value={act}>
                {act}
              </option>
            ))}
          </select>
          <span className="text-xs text-slate-400 hidden sm:inline ml-2">
            ({filtered.length} entries)
          </span>
        </div>
      </div>

      {/* Logs Table */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-16 bg-slate-900 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Activity}
          title="No Audit Records Found"
          description="No security log events match your query."
        />
      ) : (
        <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Timestamp</th>
                  <th className="px-6 py-4">Action</th>
                  <th className="px-6 py-4">Actor / User</th>
                  <th className="px-6 py-4">Target Resource</th>
                  <th className="px-6 py-4">Details / Metadata</th>
                  <th className="px-6 py-4 text-right">Client IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map((log) => {
                  const timestamp = log.timestamp || log.created_at;
                  const userName = log.user_name || log.user?.full_name || (log.user_id ? `User #${log.user_id}` : "System/Guest");
                  const userEmail = log.user_email || log.user?.email;
                  const resourceType = log.entity_type || log.resource_type;
                  const resourceId = log.entity_id ?? log.resource_id;
                  const detailsData = log.new_values || log.details || log.old_values;

                  return (
                    <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-mono text-slate-400 whitespace-nowrap">
                        {timestamp ? new Date(timestamp).toLocaleString() : "--"}
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1 font-mono font-bold text-purple-300 bg-purple-500/10 px-2.5 py-1 rounded-lg border border-purple-500/20 text-[11px]">
                          <Shield className="w-3 h-3 text-purple-400" />
                          {log.action}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-bold text-white">
                          {userName}
                        </div>
                        {userEmail && (
                          <div className="text-[10px] text-slate-500">{userEmail}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 font-mono text-slate-300">
                        {resourceType ? `${resourceType} #${resourceId ?? ""}` : "N/A"}
                      </td>
                      <td className="px-6 py-4 text-slate-400 max-w-xs truncate">
                        {detailsData ? (typeof detailsData === "object" ? JSON.stringify(detailsData) : String(detailsData)) : "--"}
                      </td>
                      <td className="px-6 py-4 text-right font-mono text-slate-500 text-[11px]">
                        {log.ip_address || "127.0.0.1"}
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
