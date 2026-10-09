import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ShieldCheck,
  Sparkles,
  Mail,
  Lock,
  User,
  Phone,
  Building,
  Briefcase,
  MapPin,
  FileText,
  AlertCircle,
  CheckCircle2,
  Clock,
  ArrowRight,
  Search,
  XCircle,
} from "lucide-react";
import { authApi } from "../../api/authApi";

export const CoordinatorApplyPage = () => {
  const [activeTab, setActiveTab] = useState("apply"); // "apply" | "status"

  // Application Form State
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [department, setDepartment] = useState("");
  const [designation, setDesignation] = useState("");
  const [experience, setExperience] = useState("");
  const [officeLocation, setOfficeLocation] = useState("");

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
      department: department.trim(),
      designation: designation.trim(),
      experience: experience.trim() || undefined,
      office_location: officeLocation.trim() || undefined,
    };

    try {
      const res = await authApi.applyCoordinator(payload);
      setSubmittedApp(res);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to submit coordinator application. Please verify details."
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
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 selection:bg-amber-500/30 selection:text-amber-200">
      <div className="sm:mx-auto sm:w-full sm:max-w-2xl text-center">
        <Link to="/" className="inline-flex items-center gap-2.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 via-amber-400 to-yellow-300 flex items-center justify-center text-slate-950 shadow-xl shadow-amber-500/30">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </Link>
        <h2 className="mt-4 text-2xl sm:text-3xl font-black tracking-tight text-white">
          Event Coordinator Candidacy Portal
        </h2>
        <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-lg mx-auto">
          Apply to lead college fest events, schedule venues, and supervise judging. Coordinators are verified and appointed by the Fest Admin Executive Council.
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
                ? "bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20"
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
                ? "bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20"
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
                <div className="w-16 h-16 mx-auto rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Clock className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-white">Application Received!</h3>
                <p className="text-xs sm:text-sm text-slate-300 max-w-md mx-auto leading-relaxed">
                  Your coordinator application for <span className="text-amber-400 font-semibold">{submittedApp.email}</span> has been stored with status{" "}
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    PENDING REVIEW
                  </span>.
                </p>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-left text-xs space-y-1.5 max-w-md mx-auto">
                  <div className="text-slate-400">Application ID: <span className="text-white font-mono font-bold">#{submittedApp.id}</span></div>
                  <div className="text-slate-400">Applicant: <span className="text-white font-medium">{submittedApp.full_name}</span></div>
                  <div className="text-slate-400">Department: <span className="text-white font-medium">{submittedApp.department} ({submittedApp.designation})</span></div>
                  <div className="text-slate-400">Submitted At: <span className="text-slate-300">{new Date(submittedApp.created_at).toLocaleString()}</span></div>
                </div>
                <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
                  <button
                    onClick={() => {
                      setSubmittedApp(null);
                      setFullName("");
                      setEmail("");
                      setPassword("");
                      setPhone("");
                      setDepartment("");
                      setDesignation("");
                      setExperience("");
                      setOfficeLocation("");
                    }}
                    className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all border border-slate-700"
                  >
                    Submit Another Application
                  </button>
                  <Link
                    to="/login"
                    className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold transition-all shadow-lg shadow-amber-500/20"
                  >
                    Return to Login
                  </Link>
                </div>
              </div>
            ) : (
              <form onSubmit={handleApply} className="space-y-5">
                {error && (
                  <div className="flex items-start gap-2.5 p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                    <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                    <span>{error}</span>
                  </div>
                )}

                <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs leading-relaxed">
                  <span className="font-semibold">Security Note:</span> Registering here will <strong>not</strong> grant immediate Coordinator privileges. Fest Administrators will review your department and credentials before approving your coordinator dashboard access.
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Full Name */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Full Name *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <User className="w-4 h-4" />
                      </div>
                      <input
                        type="text"
                        required
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="Dr. Alan Turing"
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors"
                      />
                    </div>
                  </div>

                  {/* Email */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      College / Institutional Email *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <Mail className="w-4 h-4" />
                      </div>
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="coordinator@college.edu"
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors"
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Password */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Account Password *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <Lock className="w-4 h-4" />
                      </div>
                      <input
                        type="password"
                        required
                        minLength={6}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Min. 6 characters"
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors"
                      />
                    </div>
                    <span className="text-[11px] text-slate-500 mt-1 block">
                      Used to log into your account once approved
                    </span>
                  </div>

                  {/* Phone */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Contact Phone
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <Phone className="w-4 h-4" />
                      </div>
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="+91 98765 43210"
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors"
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Department */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Department / Faculty *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <Building className="w-4 h-4" />
                      </div>
                      <input
                        type="text"
                        required
                        value={department}
                        onChange={(e) => setDepartment(e.target.value)}
                        placeholder="Computer Science & Engg."
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors"
                      />
                    </div>
                  </div>

                  {/* Designation */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Designation / Club Role *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <Briefcase className="w-4 h-4" />
                      </div>
                      <input
                        type="text"
                        required
                        value={designation}
                        onChange={(e) => setDesignation(e.target.value)}
                        placeholder="Assistant Professor / Club Head"
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors"
                      />
                    </div>
                  </div>
                </div>

                {/* Office Location */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Office / Lab Location
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                      <MapPin className="w-4 h-4" />
                    </div>
                    <input
                      type="text"
                      value={officeLocation}
                      onChange={(e) => setOfficeLocation(e.target.value)}
                      placeholder="Block B, Room 302"
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors"
                    />
                  </div>
                </div>

                {/* Experience / Statement */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Event Management Experience & Planned Fest Track
                  </label>
                  <div className="relative">
                    <div className="absolute top-3 left-3.5 pointer-events-none text-slate-500">
                      <FileText className="w-4 h-4" />
                    </div>
                    <textarea
                      rows={3}
                      value={experience}
                      onChange={(e) => setExperience(e.target.value)}
                      placeholder="Outline past hackathons, cultural festivals, or specific events you plan to coordinate..."
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors resize-none"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-4 rounded-xl font-bold text-xs sm:text-sm text-slate-950 bg-gradient-to-r from-amber-500 via-amber-400 to-yellow-300 hover:from-amber-400 hover:to-yellow-200 transition-all shadow-lg shadow-amber-500/20 disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                      <span>Submitting Candidacy...</span>
                    </>
                  ) : (
                    <>
                      <span>Submit Coordinator Application</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            )
          ) : (
            /* Check Application Status Tab */
            <div className="space-y-6">
              <form onSubmit={handleCheckStatus} className="space-y-4">
                <label className="block text-xs font-semibold text-slate-300">
                  Lookup by Email
                </label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={statusEmail}
                      onChange={(e) => setStatusEmail(e.target.value)}
                      placeholder="Enter the email used for application"
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition-colors"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={statusLoading}
                    className="px-5 py-2.5 rounded-xl font-semibold text-xs sm:text-sm text-slate-950 bg-amber-500 hover:bg-amber-400 transition-colors disabled:opacity-50 flex items-center gap-1.5"
                  >
                    {statusLoading ? (
                      <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <>
                        <Search className="w-4 h-4" />
                        <span>Search</span>
                      </>
                    )}
                  </button>
                </div>
              </form>

              {statusError && (
                <div className="flex items-start gap-2.5 p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                  <span>{statusError}</span>
                </div>
              )}

              {statusResult && (
                <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <span className="text-xs text-slate-400 font-medium">Application Status</span>
                    {statusResult.status === "APPROVED" ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        <CheckCircle2 className="w-3.5 h-3.5" /> APPROVED
                      </span>
                    ) : statusResult.status === "REJECTED" ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                        <XCircle className="w-3.5 h-3.5" /> REJECTED
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        <Clock className="w-3.5 h-3.5" /> PENDING REVIEW
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <span className="text-slate-500">Applicant:</span>
                      <p className="text-white font-medium mt-0.5">{statusResult.full_name}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Department:</span>
                      <p className="text-white font-medium mt-0.5">{statusResult.department}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Designation:</span>
                      <p className="text-white font-medium mt-0.5">{statusResult.designation}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Submitted:</span>
                      <p className="text-slate-300 mt-0.5">{new Date(statusResult.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  {statusResult.admin_notes && (
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                      <span className="text-slate-400 font-semibold block mb-1">Admin Feedback:</span>
                      <p className="text-slate-300">{statusResult.admin_notes}</p>
                    </div>
                  )}

                  {statusResult.status === "APPROVED" && (
                    <div className="pt-2">
                      <Link
                        to="/login"
                        className="w-full py-2.5 px-4 rounded-xl font-bold text-xs text-slate-950 bg-emerald-400 hover:bg-emerald-300 transition-colors flex items-center justify-center gap-2"
                      >
                        <span>Sign In to Coordinator Console</span>
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="mt-8 pt-5 border-t border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Standard student attendee?</span>
              <Link to="/register" className="font-semibold text-amber-400 hover:text-amber-300">
                Student Registration →
              </Link>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Invited as a Judge or Sponsor?</span>
              <Link to="/invite/accept" className="font-semibold text-blue-400 hover:text-blue-300">
                Redeem Invitation Token →
              </Link>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Already have an active account?</span>
              <Link to="/login" className="font-semibold text-indigo-400 hover:text-indigo-300">
                Sign In →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoordinatorApplyPage;
