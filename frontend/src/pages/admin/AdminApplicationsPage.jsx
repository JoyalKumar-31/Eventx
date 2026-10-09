import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  CheckCircle,
  XCircle,
  Clock,
  Send,
  Copy,
  Trash2,
  Filter,
  AlertCircle,
  Check,
  UserCheck,
  Gavel,
  Briefcase,
  Building,
  KeyRound,
  ExternalLink,
  RefreshCw,
  Plus,
} from "lucide-react";
import { adminApi } from "../../api/adminApi";
import EmptyState from "../../components/EmptyState";

export default function AdminApplicationsPage() {
  const [activeTab, setActiveTab] = useState("coordinators"); // "coordinators" | "judges" | "invitations"

  // Coordinator applications state
  const [coordinatorApps, setCoordinatorApps] = useState([]);
  const [coordLoading, setCoordLoading] = useState(false);
  const [coordFilter, setCoordFilter] = useState("PENDING");

  // Judge applications state
  const [judgeApps, setJudgeApps] = useState([]);
  const [judgeLoading, setJudgeLoading] = useState(false);
  const [judgeFilter, setJudgeFilter] = useState("PENDING");

  // Invitations state
  const [invitations, setInvitations] = useState([]);
  const [invLoading, setInvLoading] = useState(false);
  const [invRoleFilter, setInvRoleFilter] = useState("ALL");
  const [invStatusFilter, setInvStatusFilter] = useState("ALL");

  // Modal / Action states
  const [actionModal, setActionModal] = useState(null); // { type: 'approve' | 'reject', itemType: 'coordinator' | 'judge', item: ... }
  const [adminNotes, setAdminNotes] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);

  // New Invitation Form
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [newInviteEmail, setNewInviteEmail] = useState("");
  const [newInviteRole, setNewInviteRole] = useState("JUDGE");
  const [newInviteOrg, setNewInviteOrg] = useState("");
  const [newInviteSpec, setNewInviteSpec] = useState("");
  const [newInviteDays, setNewInviteDays] = useState(7);
  const [createdInviteResult, setCreatedInviteResult] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (activeTab === "coordinators") {
      fetchCoordinatorApps();
    } else if (activeTab === "judges") {
      fetchJudgeApps();
    } else if (activeTab === "invitations") {
      fetchInvitations();
    }
  }, [activeTab, coordFilter, judgeFilter, invRoleFilter, invStatusFilter]);

  const fetchCoordinatorApps = async () => {
    try {
      setCoordLoading(true);
      const data = await adminApi.getCoordinatorApplications(coordFilter === "ALL" ? undefined : coordFilter);
      setCoordinatorApps(data || []);
    } catch (err) {
      console.error("Failed to load coordinator applications", err);
    } finally {
      setCoordLoading(false);
    }
  };

  const fetchJudgeApps = async () => {
    try {
      setJudgeLoading(true);
      const data = await adminApi.getJudgeApplications(judgeFilter === "ALL" ? undefined : judgeFilter);
      setJudgeApps(data || []);
    } catch (err) {
      console.error("Failed to load judge applications", err);
    } finally {
      setJudgeLoading(false);
    }
  };

  const fetchInvitations = async () => {
    try {
      setInvLoading(true);
      const params = {};
      if (invRoleFilter !== "ALL") params.role = invRoleFilter;
      if (invStatusFilter !== "ALL") params.status = invStatusFilter;
      const data = await adminApi.getInvitations(params);
      setInvitations(data || []);
    } catch (err) {
      console.error("Failed to load invitations", err);
    } finally {
      setInvLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!actionModal || actionLoading) return;
    setActionLoading(true);
    setFeedback(null);

    const { type, itemType, item } = actionModal;

    try {
      if (itemType === "coordinator") {
        if (type === "approve") {
          await adminApi.approveCoordinatorApplication(item.id, adminNotes);
          setFeedback({ type: "success", text: `Successfully approved ${item.full_name} as Event Coordinator!` });
        } else {
          await adminApi.rejectCoordinatorApplication(item.id, adminNotes);
          setFeedback({ type: "success", text: `Application for ${item.full_name} marked as rejected.` });
        }
        fetchCoordinatorApps();
      } else if (itemType === "judge") {
        if (type === "approve") {
          await adminApi.approveJudgeApplication(item.id, adminNotes);
          setFeedback({ type: "success", text: `Successfully approved ${item.full_name} as Fest Judge!` });
        } else {
          await adminApi.rejectJudgeApplication(item.id, adminNotes);
          setFeedback({ type: "success", text: `Judge application for ${item.full_name} marked as rejected.` });
        }
        fetchJudgeApps();
      }
      setActionModal(null);
      setAdminNotes("");
    } catch (err) {
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || err.response?.data?.message || "Action failed to execute.",
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateInvitation = async (e) => {
    e.preventDefault();
    if (actionLoading) return;
    setActionLoading(true);
    setFeedback(null);

    try {
      const payload = {
        email: newInviteEmail.trim().toLowerCase(),
        role: newInviteRole,
        organization: newInviteOrg.trim() || undefined,
        specialization: newInviteSpec.trim() || undefined,
        expires_in_days: Number(newInviteDays) || 7,
      };

      const res = await adminApi.createInvitation(payload);
      setCreatedInviteResult(res);
      fetchInvitations();
      // Reset form
      setNewInviteEmail("");
      setNewInviteOrg("");
      setNewInviteSpec("");
      setNewInviteDays(7);
    } catch (err) {
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || err.response?.data?.message || "Failed to create invitation.",
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleRevokeInvitation = async (id, email) => {
    if (!window.confirm(`Are you sure you want to revoke the invitation for ${email}?`)) return;
    try {
      setFeedback(null);
      await adminApi.revokeInvitation(id);
      setFeedback({ type: "success", text: `Invitation for ${email} has been revoked.` });
      fetchInvitations();
    } catch (err) {
      setFeedback({
        type: "error",
        text: err.response?.data?.detail || "Failed to revoke invitation.",
      });
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-purple-950/40 via-slate-900 to-slate-900 p-6 sm:p-8 border border-purple-500/20 shadow-xl">
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-semibold uppercase tracking-wider">
              <ShieldCheck className="w-3.5 h-3.5" /> RBAC Authority & Governance
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Role Approvals & Invitation Management
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm max-w-2xl">
              Inspect pending Event Coordinator applications, issue cryptographically bound single-use Judge invitations, and review corporate Sponsor proposals.
            </p>
          </div>
          {activeTab === "invitations" && (
            <button
              onClick={() => {
                setShowInviteModal(true);
                setCreatedInviteResult(null);
              }}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs sm:text-sm transition-all shadow-lg shadow-purple-600/30 shrink-0 cursor-pointer"
            >
              <Plus className="w-4 h-4" /> Issue New Invitation
            </button>
          )}
        </div>
      </div>

      {/* Global Feedback Banner */}
      {feedback && (
        <div
          className={`flex items-start gap-2.5 p-4 rounded-2xl border text-xs ${
            feedback.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
              : "bg-rose-500/10 border-rose-500/30 text-rose-300"
          }`}
        >
          {feedback.type === "success" ? (
            <CheckCircle className="w-4 h-4 shrink-0 mt-0.5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
          )}
          <span>{feedback.text}</span>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 gap-2 sm:gap-4 overflow-x-auto pb-px">
        <button
          onClick={() => setActiveTab("coordinators")}
          className={`pb-3 px-3 text-xs sm:text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap ${
            activeTab === "coordinators"
              ? "border-amber-400 text-amber-400"
              : "border-transparent text-slate-400 hover:text-white"
          }`}
        >
          <UserCheck className="w-4 h-4" />
          <span>Coordinator Applications</span>
          {coordinatorApps.filter((a) => a.status === "PENDING").length > 0 && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">
              {coordinatorApps.filter((a) => a.status === "PENDING").length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("judges")}
          className={`pb-3 px-3 text-xs sm:text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap ${
            activeTab === "judges"
              ? "border-purple-400 text-purple-400"
              : "border-transparent text-slate-400 hover:text-white"
          }`}
        >
          <Gavel className="w-4 h-4" />
          <span>Judge Applications</span>
          {judgeApps.filter((a) => a.status === "PENDING").length > 0 && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30">
              {judgeApps.filter((a) => a.status === "PENDING").length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("invitations")}
          className={`pb-3 px-3 text-xs sm:text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap ${
            activeTab === "invitations"
              ? "border-blue-400 text-blue-400"
              : "border-transparent text-slate-400 hover:text-white"
          }`}
        >
          <KeyRound className="w-4 h-4" />
          <span>Judge Direct Invitations</span>
        </button>
      </div>

      {/* =========================================================================
          TAB 1: COORDINATOR APPLICATIONS
          ========================================================================= */}
      {activeTab === "coordinators" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400 font-medium">Filter Status:</span>
              {["ALL", "PENDING", "APPROVED", "REJECTED"].map((st) => (
                <button
                  key={st}
                  onClick={() => setCoordFilter(st)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                    coordFilter === st
                      ? "bg-amber-500 text-slate-950"
                      : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
            <button
              onClick={fetchCoordinatorApps}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1 self-start sm:self-auto cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh List
            </button>
          </div>

          {coordLoading ? (
            <div className="p-8 text-center text-xs text-slate-400 animate-pulse">
              Loading coordinator applications...
            </div>
          ) : coordinatorApps.length === 0 ? (
            <EmptyState
              icon={UserCheck}
              title="No coordinator applications found"
              description={`No applications matching filter "${coordFilter}".`}
            />
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {coordinatorApps.map((app) => (
                <div
                  key={app.id}
                  className="rounded-2xl bg-slate-900 border border-slate-800 p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-bold text-white text-base">{app.full_name}</h3>
                      <span className="font-mono text-xs text-slate-400">({app.email})</span>
                      {app.status === "APPROVED" ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                          <CheckCircle className="w-3 h-3" /> APPROVED
                        </span>
                      ) : app.status === "REJECTED" ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                          <XCircle className="w-3 h-3" /> REJECTED
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          <Clock className="w-3 h-3" /> PENDING REVIEW
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs text-slate-300">
                      <div>
                        <span className="text-slate-500">Department:</span> {app.department}
                      </div>
                      <div>
                        <span className="text-slate-500">Designation:</span> {app.designation}
                      </div>
                      <div>
                        <span className="text-slate-500">Phone:</span> {app.phone || "—"}
                      </div>
                    </div>

                    {app.office_location && (
                      <div className="text-xs text-slate-400">
                        <span className="text-slate-500">Office / Cabin:</span> {app.office_location}
                      </div>
                    )}

                    {app.experience && (
                      <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300">
                        <span className="text-slate-500 font-semibold block mb-0.5">Experience & Fest Track:</span>
                        {app.experience}
                      </div>
                    )}

                    {app.admin_notes && (
                      <div className="text-xs text-slate-400 italic">
                        <strong>Admin Notes:</strong> {app.admin_notes}
                      </div>
                    )}

                    <div className="text-[11px] text-slate-500">
                      Submitted on {new Date(app.created_at).toLocaleString()}
                    </div>
                  </div>

                  {app.status === "PENDING" && (
                    <div className="flex sm:flex-col gap-2 shrink-0">
                      <button
                        onClick={() =>
                          setActionModal({
                            type: "approve",
                            itemType: "coordinator",
                            item: app,
                          })
                        }
                        className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-colors shadow-md shadow-emerald-600/20 flex items-center justify-center gap-1.5 cursor-pointer"
                      >
                        <CheckCircle className="w-3.5 h-3.5" /> Approve Role
                      </button>
                      <button
                        onClick={() =>
                          setActionModal({
                            type: "reject",
                            itemType: "coordinator",
                            item: app,
                          })
                        }
                        className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-rose-900/40 hover:bg-rose-900/60 border border-rose-700/50 text-rose-300 font-bold text-xs transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                      >
                        <XCircle className="w-3.5 h-3.5" /> Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 2: JUDGE & SPONSOR INVITATIONS
          ========================================================================= */}
      {activeTab === "invitations" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-3 text-xs">
              <div className="flex items-center gap-1">
                <span className="text-slate-400 font-medium">Role:</span>
                {["ALL", "JUDGE", "SPONSOR"].map((r) => (
                  <button
                    key={r}
                    onClick={() => setInvRoleFilter(r)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold cursor-pointer ${
                      invRoleFilter === r
                        ? "bg-blue-600 text-white"
                        : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-1">
                <span className="text-slate-400 font-medium">Status:</span>
                {["ALL", "PENDING", "ACCEPTED", "EXPIRED", "REVOKED"].map((s) => (
                  <button
                    key={s}
                    onClick={() => setInvStatusFilter(s)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold cursor-pointer ${
                      invStatusFilter === s
                        ? "bg-purple-600 text-white"
                        : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
            <button
              onClick={fetchInvitations}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1 self-start sm:self-auto cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh Invitations
            </button>
          </div>

          {invLoading ? (
            <div className="p-8 text-center text-xs text-slate-400 animate-pulse">
              Loading invitations...
            </div>
          ) : invitations.length === 0 ? (
            <EmptyState
              icon={KeyRound}
              title="No invitations issued"
              description="Click 'Issue New Invitation' above to generate single-use invite codes for Judges or Sponsors."
            />
          ) : (
            <div className="rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Recipient Email</th>
                      <th className="px-4 py-3">Designated Role</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Organization / Spec</th>
                      <th className="px-4 py-3">Expires At</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {invitations.map((inv) => (
                      <tr key={inv.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="px-4 py-3.5 font-medium text-white font-mono">
                          {inv.email}
                        </td>
                        <td className="px-4 py-3.5">
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold ${
                              inv.role === "JUDGE"
                                ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                                : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            }`}
                          >
                            {inv.role === "JUDGE" ? <Gavel className="w-3 h-3" /> : <Briefcase className="w-3 h-3" />}
                            {inv.role}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">
                          {inv.status === "ACCEPTED" ? (
                            <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                              <CheckCircle className="w-3 h-3" /> Accepted
                            </span>
                          ) : inv.status === "EXPIRED" ? (
                            <span className="text-slate-500 font-semibold">Expired</span>
                          ) : inv.status === "REVOKED" ? (
                            <span className="text-rose-400 font-semibold">Revoked</span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-amber-400 font-semibold">
                              <Clock className="w-3 h-3" /> Pending
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3.5 text-slate-300">
                          {inv.organization || "—"}
                          {inv.specialization && (
                            <span className="text-slate-500 block text-[10px]">
                              {inv.specialization}
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3.5 text-slate-400 font-mono text-[11px]">
                          {new Date(inv.expires_at).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3.5 text-right">
                          {inv.status === "PENDING" && (
                            <button
                              onClick={() => handleRevokeInvitation(inv.id, inv.email)}
                              className="text-rose-400 hover:text-rose-300 p-1.5 rounded-lg hover:bg-rose-500/10 transition-colors cursor-pointer"
                              title="Revoke invitation token"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 2: JUDGE APPLICATIONS (SAME APPROVAL WORKFLOW AS COORDINATOR)
          ========================================================================= */}
      {activeTab === "judges" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400 font-medium">Filter Status:</span>
              {["ALL", "PENDING", "APPROVED", "REJECTED"].map((st) => (
                <button
                  key={st}
                  onClick={() => setJudgeFilter(st)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                    judgeFilter === st
                      ? "bg-purple-600 text-white"
                      : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
            <button
              onClick={fetchJudgeApps}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1 self-start sm:self-auto cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh List
            </button>
          </div>

          {judgeLoading ? (
            <div className="p-8 text-center text-xs text-slate-400 animate-pulse">
              Loading judge applications...
            </div>
          ) : judgeApps.length === 0 ? (
            <EmptyState
              icon={Gavel}
              title="No judge applications found"
              description={`No judge applications matching filter "${judgeFilter}".`}
            />
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {judgeApps.map((app) => (
                <div
                  key={app.id}
                  className="rounded-2xl bg-slate-900 border border-slate-800 p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-bold text-white text-base">{app.full_name}</h3>
                      <span className="font-mono text-xs text-slate-400">({app.email})</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        {app.organization}
                      </span>
                      {app.status === "APPROVED" ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                          <CheckCircle className="w-3 h-3" /> APPROVED
                        </span>
                      ) : app.status === "REJECTED" ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                          <XCircle className="w-3 h-3" /> REJECTED
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                          <Clock className="w-3 h-3" /> PENDING REVIEW
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300">
                      <div>
                        <span className="text-slate-500">Domain / Specialization:</span>{" "}
                        <strong className="text-purple-300">{app.specialization}</strong>
                      </div>
                      {app.phone && (
                        <div>
                          <span className="text-slate-500">Phone:</span> {app.phone}
                        </div>
                      )}
                    </div>

                    {app.experience && (
                      <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300">
                        <span className="text-slate-500 font-semibold block mb-0.5">Experience & Credentials:</span>
                        {app.experience}
                      </div>
                    )}

                    {app.bio && (
                      <div className="text-xs text-slate-400">
                        <span className="text-slate-500 font-semibold">Bio:</span> {app.bio}
                      </div>
                    )}

                    {app.admin_notes && (
                      <div className="text-xs text-slate-400 italic">
                        <strong>Admin Remarks:</strong> {app.admin_notes}
                      </div>
                    )}

                    <div className="text-[11px] text-slate-500">
                      Submitted on {new Date(app.created_at).toLocaleString()}
                    </div>
                  </div>

                  {app.status === "PENDING" && (
                    <div className="flex sm:flex-col gap-2 shrink-0">
                      <button
                        onClick={() =>
                          setActionModal({
                            type: "approve",
                            itemType: "judge",
                            item: app,
                          })
                        }
                        className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs transition-colors shadow-md shadow-purple-600/20 flex items-center justify-center gap-1.5 cursor-pointer"
                      >
                        <CheckCircle className="w-3.5 h-3.5" /> Approve Judge
                      </button>
                      <button
                        onClick={() =>
                          setActionModal({
                            type: "reject",
                            itemType: "judge",
                            item: app,
                          })
                        }
                        className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-rose-900/40 hover:bg-rose-900/60 border border-rose-700/50 text-rose-300 font-bold text-xs transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                      >
                        <XCircle className="w-3.5 h-3.5" /> Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          MODAL 1: APPROVE / REJECT DIALOG
          ========================================================================= */}
      {actionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-3xl bg-slate-900 border border-slate-800 p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white">
              {actionModal.type === "approve" ? "Confirm Approval" : "Confirm Rejection"}
            </h3>
            <p className="text-xs text-slate-300">
              {actionModal.type === "approve"
                ? `You are granting elevated privileges to ${actionModal.item.full_name || actionModal.item.company_name}. This will update their account role immediately.`
                : `You are rejecting the application for ${actionModal.item.full_name || actionModal.item.company_name}.`}
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Admin Review Notes (Optional)
              </label>
              <textarea
                rows={3}
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                placeholder="Add internal feedback or remarks..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-purple-400 resize-none"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  setActionModal(null);
                  setAdminNotes("");
                }}
                className="flex-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleReviewSubmit}
                disabled={actionLoading}
                className={`flex-1 py-2.5 rounded-xl text-white text-xs font-bold transition-all shadow-lg flex items-center justify-center gap-1.5 cursor-pointer ${
                  actionModal.type === "approve"
                    ? "bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/30"
                    : "bg-rose-600 hover:bg-rose-500 shadow-rose-600/30"
                }`}
              >
                {actionLoading ? (
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : actionModal.type === "approve" ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    <span>Confirm Approval</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4" />
                    <span>Confirm Rejection</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          MODAL 2: ISSUE NEW INVITATION MODAL
          ========================================================================= */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-3xl bg-slate-900 border border-slate-800 p-6 sm:p-8 shadow-2xl space-y-5">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <KeyRound className="w-5 h-5 text-purple-400" /> Issue Cryptographic Invitation
              </h3>
              <button
                onClick={() => setShowInviteModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            {createdInviteResult ? (
              <div className="space-y-4 py-2">
                <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs space-y-1">
                  <div className="font-bold text-emerald-400 flex items-center gap-1">
                    <CheckCircle className="w-4 h-4" /> Invitation Token Generated!
                  </div>
                  <p>
                    A single-use invitation for <strong>{createdInviteResult.email}</strong> as <strong>{createdInviteResult.role}</strong> has been secured.
                  </p>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold text-slate-300">
                    Direct Invitation URL (Share with recipient):
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      readOnly
                      value={`${window.location.origin}${createdInviteResult.invite_url}`}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 font-mono text-xs select-all"
                    />
                    <button
                      onClick={() =>
                        copyToClipboard(`${window.location.origin}${createdInviteResult.invite_url}`)
                      }
                      className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs transition-colors shrink-0 flex items-center gap-1 cursor-pointer"
                    >
                      {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? "Copied" : "Copy"}</span>
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold text-slate-300">
                    Raw Security Token:
                  </label>
                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-purple-300 font-mono text-xs break-all">
                    {createdInviteResult.raw_token}
                  </div>
                  <span className="text-[11px] text-slate-500 block">
                    The token is valid until {new Date(createdInviteResult.expires_at).toLocaleDateString()} and will be destroyed upon first use.
                  </span>
                </div>

                <div className="pt-2">
                  <button
                    onClick={() => {
                      setCreatedInviteResult(null);
                      setShowInviteModal(false);
                    }}
                    className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors cursor-pointer"
                  >
                    Done
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleCreateInvitation} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Invited Recipient Email *
                    </label>
                    <input
                      type="email"
                      required
                      value={newInviteEmail}
                      onChange={(e) => setNewInviteEmail(e.target.value)}
                      placeholder="judge@expert.org"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-purple-400"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Assigned Role *
                    </label>
                    <select
                      value={newInviteRole}
                      onChange={(e) => setNewInviteRole(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-purple-400"
                    >
                      <option value="JUDGE">JUDGE (Event Evaluator)</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Organization / University / Brand
                    </label>
                    <input
                      type="text"
                      value={newInviteOrg}
                      onChange={(e) => setNewInviteOrg(e.target.value)}
                      placeholder="e.g. Google / IIT Delhi"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-purple-400"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Domain Track / Specialization
                    </label>
                    <input
                      type="text"
                      value={newInviteSpec}
                      onChange={(e) => setNewInviteSpec(e.target.value)}
                      placeholder="e.g. AI Hackathon / Title Partner"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-purple-400"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Token Validity Period (Days)
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={90}
                    value={newInviteDays}
                    onChange={(e) => setNewInviteDays(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-purple-400"
                  />
                  <span className="text-[11px] text-slate-500 mt-1 block">
                    After this period, the invitation token automatically expires.
                  </span>
                </div>

                <div className="pt-2 flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowInviteModal(false)}
                    className="flex-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={actionLoading}
                    className="flex-1 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition-all shadow-lg shadow-purple-600/30 flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    {actionLoading ? (
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span>Generate Token</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
