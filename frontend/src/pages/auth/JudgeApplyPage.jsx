import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Gavel,
  ShieldCheck,
  Mail,
  Lock,
  User,
  Phone,
  Building,
  Award,
  FileText,
  AlertCircle,
  CheckCircle2,
  Clock,
  ArrowRight,
  Search,
  XCircle,
  Briefcase
} from "lucide-react";
import { authApi } from "../../api/authApi";

export default function JudgeApplyPage() {
  const [activeTab, setActiveTab] = useState("apply"); // "apply" | "status"

  // Application Form State
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [organization, setOrganization] = useState("");
  const [specialization, setSpecialization] = useState("");
  const [experience, setExperience] = useState("");
  const [bio, setBio] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submittedApp, setSubmittedApp] = useState(null);

  // Status Lookup State
  const [statusEmail, setStatusEmail] = useState("");
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusResult, setStatusResult] = useState(null);
  const [statusError, setStatusError] = useState(null);

  const navigate = useNavigate();

  const handleApply = async (e) => {
    e.preventDefault();
    if (loading) return;
    setError(null);
    setLoading(true);

    const payload = {
      full_name: fullName.trim(),
      email: email.trim().toLowerCase(),
      password: password || undefined,
      phone: phone.trim() || undefined,
      organization: organization.trim(),
      specialization: specialization.trim(),
      experience: experience.trim() || undefined,
      bio: bio.trim() || undefined,
    };

    try {
      const res = await authApi.applyJudge(payload);
      setSubmittedApp(res);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to submit judge application. Please verify all details."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCheckStatus = async (e) => {
    e.preventDefault();
    if (!statusEmail.trim() || statusLoading) return;
    setStatusError(null);
    setStatusResult(null);
    setStatusLoading(true);

    try {
      const res = await authApi.checkApplicationStatus(statusEmail.trim().toLowerCase());
      setStatusResult(res);
    } catch (err) {
      setStatusError(
        err.response?.data?.detail ||
        "No application records found for this email address."
      );
    } finally {
      setStatusLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 selection:bg-purple-500/30 selection:text-purple-200">
      <div className="sm:mx-auto sm:w-full sm:max-w-2xl text-center">
        <Link to="/" className="inline-flex items-center gap-2.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-600 via-purple-500 to-indigo-400 flex items-center justify-center text-white shadow-xl shadow-purple-500/30">
            <Gavel className="w-6 h-6" />
          </div>
        </Link>
        <h2 className="mt-4 text-2xl sm:text-3xl font-black tracking-tight text-white">
          Fest Judge Candidacy Portal
        </h2>
        <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-lg mx-auto">
          Apply to serve on official judging panels, evaluate student projects, and submit competition scores. All judge candidacies are verified and appointed by the Fest Admin Council.
        </p>

        {/* Tab Switcher */}
        <div className="mt-6 inline-flex p-1 bg-slate-900 border border-slate-800 rounded-2xl">
          <button
            type="button"
            onClick={() => {
              setActiveTab("apply");
              setError(null);
            }}
            className={`px-5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "apply"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Submit Application
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab("status");
              setStatusError(null);
            }}
            className={`px-5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "status"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Check Status
          </button>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl px-4 sm:px-0">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 sm:p-10 backdrop-blur-xl shadow-2xl shadow-black/40">
          {activeTab === "apply" ? (
            submittedApp ? (
              <div className="text-center py-6 space-y-4">
                <div className="w-16 h-16 mx-auto rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                  <Clock className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-white">Application Received!</h3>
                <p className="text-xs sm:text-sm text-slate-300 max-w-md mx-auto leading-relaxed">
                  Your judge application for <span className="text-purple-400 font-semibold">{submittedApp.email}</span> has been saved under status{" "}
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                    PENDING REVIEW
                  </span>.
                </p>
                <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 text-left max-w-md mx-auto space-y-2 text-xs text-slate-400">
                  <div><strong className="text-slate-200">Name:</strong> {submittedApp.full_name}</div>
                  <div><strong className="text-slate-200">Organization:</strong> {submittedApp.organization}</div>
                  <div><strong className="text-slate-200">Specialization:</strong> {submittedApp.specialization}</div>
                  <div><strong className="text-slate-200">Submitted At:</strong> {new Date(submittedApp.created_at).toLocaleString()}</div>
                </div>
                <p className="text-xs text-slate-400 max-w-md mx-auto">
                  Our Fest Administrators will review your credentials and domain expertise. Once approved, you will be granted access to the Judge Portal.
                </p>
                <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
                  <button
                    onClick={() => {
                      setSubmittedApp(null);
                      setFullName("");
                      setEmail("");
                      setPassword("");
                      setPhone("");
                      setOrganization("");
                      setSpecialization("");
                      setExperience("");
                      setBio("");
                    }}
                    className="w-full sm:w-auto px-6 py-2.5 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs sm:text-sm font-semibold text-white transition-colors"
                  >
                    Submit Another
                  </button>
                  <Link
                    to="/login"
                    className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs sm:text-sm font-semibold text-white transition-colors text-center shadow-lg shadow-purple-600/20"
                  >
                    Proceed to Login
                  </Link>
                </div>
              </div>
            ) : (
              <form onSubmit={handleApply} className="space-y-5">
                {error && (
                  <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs sm:text-sm flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
                    <span>{typeof error === "string" ? error : JSON.stringify(error)}</span>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Full Name */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-purple-400" />
                      Full Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Dr. Jane Smith"
                      className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                    />
                  </div>

                  {/* Email */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <Mail className="w-3.5 h-3.5 text-purple-400" />
                      Email Address *
                    </label>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="judge@institution.org"
                      className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                    />
                  </div>

                  {/* Password */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <Lock className="w-3.5 h-3.5 text-purple-400" />
                      Account Password *
                    </label>
                    <input
                      type="password"
                      required
                      minLength={6}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Min 6 characters"
                      className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                    />
                  </div>

                  {/* Phone */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <Phone className="w-3.5 h-3.5 text-purple-400" />
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="+91 98765 43210"
                      className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                    />
                  </div>

                  {/* Organization / Company */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <Building className="w-3.5 h-3.5 text-purple-400" />
                      Organization / University / Firm *
                    </label>
                    <input
                      type="text"
                      required
                      value={organization}
                      onChange={(e) => setOrganization(e.target.value)}
                      placeholder="e.g. National Institute of Tech / Google"
                      className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                    />
                  </div>

                  {/* Domain Specialization */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5 text-purple-400" />
                      Judging Specialization / Domain *
                    </label>
                    <input
                      type="text"
                      required
                      value={specialization}
                      onChange={(e) => setSpecialization(e.target.value)}
                      placeholder="e.g. AI/ML, Web3, Esports, Robotics, Fine Arts"
                      className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                    />
                  </div>
                </div>

                {/* Experience */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <Briefcase className="w-3.5 h-3.5 text-purple-400" />
                    Judging / Industry Experience
                  </label>
                  <textarea
                    rows={2}
                    value={experience}
                    onChange={(e) => setExperience(e.target.value)}
                    placeholder="Briefly describe hackathons, competitions, or panels you have judged, or relevant industry background..."
                    className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 resize-none"
                  />
                </div>

                {/* Bio */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-purple-400" />
                    Short Bio / Professional Profile
                  </label>
                  <textarea
                    rows={2}
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    placeholder="Distinguished researcher, senior software architect, or jury member..."
                    className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 resize-none"
                  />
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-950/50 border border-slate-800 text-[11px] text-slate-400 leading-relaxed flex items-start gap-2.5">
                  <ShieldCheck className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                  <div>
                    Submitting this form creates a secure account in <span className="text-slate-200 font-semibold">PENDING</span> status. To safeguard competition integrity, judge permissions and score submission access are only unlocked after verified administrator approval.
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-4 rounded-xl font-bold text-xs sm:text-sm text-white bg-gradient-to-r from-purple-600 via-purple-500 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 shadow-lg shadow-purple-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                      <span>Submitting Candidacy...</span>
                    </>
                  ) : (
                    <>
                      <span>Submit Judge Application</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            )
          ) : (
            <div className="space-y-6">
              <form onSubmit={handleCheckStatus} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <Search className="w-3.5 h-3.5 text-purple-400" />
                    Registered Applicant Email
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="email"
                      required
                      value={statusEmail}
                      onChange={(e) => setStatusEmail(e.target.value)}
                      placeholder="Enter the email address you applied with"
                      className="flex-1 px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-purple-500"
                    />
                    <button
                      type="submit"
                      disabled={statusLoading}
                      className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs sm:text-sm font-semibold transition-colors disabled:opacity-50"
                    >
                      {statusLoading ? "Checking..." : "Look Up"}
                    </button>
                  </div>
                </div>
              </form>

              {statusError && (
                <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs sm:text-sm flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
                  <span>{statusError}</span>
                </div>
              )}

              {statusResult && (
                <div className="space-y-4">
                  {statusResult.judge_application ? (
                    <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs uppercase font-bold tracking-wider text-purple-400 flex items-center gap-1.5">
                          <Gavel className="w-4 h-4" />
                          Fest Judge Candidacy
                        </span>
                        <span
                          className={`px-2.5 py-0.5 rounded text-[11px] font-bold border ${
                            statusResult.judge_application.status === "APPROVED"
                              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                              : statusResult.judge_application.status === "REJECTED"
                              ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                              : "bg-purple-500/10 text-purple-300 border-purple-500/30"
                          }`}
                        >
                          {statusResult.judge_application.status}
                        </span>
                      </div>
                      <div className="text-xs text-slate-300 space-y-1">
                        <div>
                          <strong className="text-slate-400">Submitted:</strong>{" "}
                          {new Date(statusResult.judge_application.submitted_at).toLocaleString()}
                        </div>
                        {statusResult.judge_application.admin_notes && (
                          <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 mt-2">
                            <strong className="text-purple-400">Admin Remarks:</strong>{" "}
                            {statusResult.judge_application.admin_notes}
                          </div>
                        )}
                      </div>

                      {statusResult.judge_application.status === "APPROVED" && (
                        <div className="pt-2">
                          <Link
                            to="/login"
                            className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-md transition-colors"
                          >
                            <span>Sign in to Judge Dashboard</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-xs text-slate-400 text-center">
                      No Fest Judge application found for this email address.
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="mt-8 pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
            <div>
              Already have an approved account?{" "}
              <Link to="/login" className="text-purple-400 hover:text-purple-300 font-semibold underline underline-offset-4">
                Sign in here
              </Link>
            </div>
            <div>
              Looking for coordinator role?{" "}
              <Link to="/apply/coordinator" className="text-amber-400 hover:text-amber-300 font-semibold underline underline-offset-4">
                Apply as Coordinator
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
