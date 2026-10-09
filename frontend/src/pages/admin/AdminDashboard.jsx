import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Users,
  Calendar,
  DollarSign,
  QrCode,
  ShieldCheck,
  Building,
  ArrowRight,
  TrendingUp,
  Activity,
  FileText,
  UserCheck,
} from "lucide-react";
import { adminApi } from "../../api/adminApi";
import StatCard from "../../components/StatCard";

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const [m, logs] = await Promise.all([
        adminApi.getAdminMetrics().catch(() => null),
        adminApi.getAuditLogs({ limit: 5 }).catch(() => []),
      ]);
      setMetrics(m);
      setAuditLogs(logs || []);
    } catch (err) {
      console.error("Failed to load admin metrics", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-purple-950/50 via-slate-900 to-slate-900 p-6 sm:p-8 border border-purple-500/20 shadow-2xl">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-semibold uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5" /> Fest Executive Console
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Central Command & Administration
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Monitor real-time festival metrics, enforce role-based access controls, review immutable audit logs, and oversee fiscal operations.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/admin/applications"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm transition-all shadow-lg shadow-purple-600/30"
            >
              <UserCheck className="w-4 h-4" /> Role Approvals & Invites
            </Link>
            <Link
              to="/admin/users"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-all border border-slate-700"
            >
              <Users className="w-4 h-4" /> Manage Users
            </Link>
            <Link
              to="/admin/audit-logs"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-all border border-slate-700"
            >
              <Activity className="w-4 h-4 text-purple-400" /> Security Audit Trail
            </Link>
          </div>
        </div>
      </div>

      {/* Global Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Users"
          value={metrics?.total_users ?? 0}
          subtitle="Registered accounts"
          icon={Users}
          color="purple"
        />
        <StatCard
          title="Total Events"
          value={metrics?.total_events ?? 0}
          subtitle={`${metrics?.published_events ?? 0} live catalog events`}
          icon={Calendar}
          color="blue"
        />
        <StatCard
          title="Total Registrations"
          value={metrics?.total_registrations ?? 0}
          subtitle="Solo & team enrollments"
          icon={QrCode}
          color="indigo"
        />
        <StatCard
          title="Gross Revenue"
          value={`₹${metrics?.total_revenue ? Number(metrics.total_revenue).toLocaleString() : 0}`}
          subtitle="Processed through gateway"
          icon={DollarSign}
          color="emerald"
        />
      </div>

      {/* Second Row: Attendance & Certificates */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <StatCard
          title="Total Attendance"
          value={metrics?.total_attendance ?? 0}
          subtitle="Scanned gate check-ins"
          icon={QrCode}
          color="amber"
        />
        <StatCard
          title="Certificates Generated"
          value={metrics?.total_certificates ?? 0}
          subtitle="Issued digital credentials"
          icon={FileText}
          color="rose"
        />
      </div>

      {/* Recent Security Audit Logs Preview */}
      <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-lg flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-400" /> Recent Security & Administrative Actions
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Live immutable stream of system operations and RBAC changes
            </p>
          </div>
          <Link
            to="/admin/audit-logs"
            className="text-xs font-semibold text-purple-400 hover:text-purple-300 transition-colors"
          >
            Full Audit Trail →
          </Link>
        </div>

        {loading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-slate-950 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : auditLogs.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 italic">
            No audit events recorded yet.
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {auditLogs.map((log) => (
              <div
                key={log.id}
                className="px-6 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                    {log.action}
                  </span>
                  <span className="text-white font-medium">
                    {log.user?.full_name || `User #${log.user_id}`}
                  </span>
                  <span className="text-slate-400">
                    on {log.resource_type} #{log.resource_id}
                  </span>
                </div>
                <span className="text-slate-500 text-[11px]">
                  {new Date(log.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
