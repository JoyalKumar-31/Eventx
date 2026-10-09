import React, { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  KeyRound,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Lock,
  User,
  Phone,
  Building,
  Globe,
  FileText,
  ArrowRight,
  Sparkles,
  Gavel,
  Briefcase,
  Clock,
} from "lucide-react";
import { invitationApi } from "../../api/invitationApi";
import { useAuth, getRoleDashboardPath } from "../../auth/AuthContext";

export const AcceptInvitationPage = () => {
  const [searchParams] = useSearchParams();
  const initialToken = searchParams.get("token") || "";

  const [tokenInput, setTokenInput] = useState(initialToken);
  const [tokenState, setTokenState] = useState(initialToken ? "verifying" : "idle"); // idle, verifying, valid, invalid
  const [invitationData, setInvitationData] = useState(null);
  const [verificationError, setVerificationError] = useState(null);

  // Form Fields for Account Setup
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [bio, setBio] = useState("");
  const [website, setWebsite] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const { setAuthSession } = useAuth();
  const navigate = useNavigate();

  // Verify token when component mounts if token exists in URL
  useEffect(() => {
    if (initialToken) {
      verifyToken(initialToken);
    }
  }, [initialToken]);

  const verifyToken = async (tok) => {
    if (!tok || !tok.trim()) return;
    setTokenState("verifying");
    setVerificationError(null);
    try {
      const data = await invitationApi.verifyInvitation(tok.trim());
      setInvitationData(data);
      setTokenState("valid");
    } catch (err) {
      setTokenState("invalid");
      setVerificationError(
        err.response?.data?.detail ||
        "The invitation token is invalid, expired, or has already been accepted."
      );
    }
  };

  const handleManualVerify = (e) => {
    e.preventDefault();
    verifyToken(tokenInput);
  };

  const handleAccept = async (e) => {
    e.preventDefault();
    if (submitting || !invitationData) return;
    setSubmitError(null);

    if (password !== confirmPassword) {
      setSubmitError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        token: tokenInput.trim(),
        email: invitationData.email,
        password,
        full_name: fullName.trim(),
        phone: phone.trim() || undefined,
        bio: bio.trim() || undefined,
        website: website.trim() || undefined,
      };

      const res = await invitationApi.acceptInvitation(payload);
      
      // Save authenticated session in AuthContext & LocalStorage
      const userSession = {
        id: res.user_id,
        email: res.email,
        full_name: res.full_name,
        role: res.role,
      };
      setAuthSession(res.access_token, userSession);

      // Navigate to destination role dashboard
      const dest = getRoleDashboardPath(res.role);
      navigate(dest, { replace: true });
    } catch (err) {
      setSubmitError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to accept invitation. Please check your inputs and try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 selection:bg-blue-500/30 selection:text-blue-200">
      <div className="sm:mx-auto sm:w-full sm:max-w-lg text-center">
        <Link to="/" className="inline-flex items-center gap-2.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-500 via-indigo-500 to-cyan-400 flex items-center justify-center text-white shadow-xl shadow-blue-500/30">
            <KeyRound className="w-6 h-6" />
          </div>
        </Link>
        <h2 className="mt-4 text-2xl sm:text-3xl font-black tracking-tight text-white">
          Redeem Official Invitation
        </h2>
        <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-md mx-auto">
          Single-use cryptographic onboarding for festival Judges and Official Sponsors.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-xl px-4 sm:px-0">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 sm:p-10 backdrop-blur-xl shadow-2xl shadow-black/40">
          
          {/* STEP 1: Enter / Verify Token */}
          {tokenState !== "valid" ? (
            <div className="space-y-6">
              <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs leading-relaxed">
                <span className="font-semibold">Security Protocol:</span> EventX uses administrator-issued tokens to guarantee that only verified domain experts serve as Judges and accredited partners join as Sponsors.
              </div>

              {verificationError && (
                <div className="flex items-start gap-2.5 p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                  <span>{verificationError}</span>
                </div>
              )}

              <form onSubmit={handleManualVerify} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Invitation Security Code / Token *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                      <KeyRound className="w-4 h-4" />
                    </div>
                    <input
                      type="text"
                      required
                      value={tokenInput}
                      onChange={(e) => setTokenInput(e.target.value)}
                      placeholder="Paste your 32-character invite token"
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono placeholder-slate-600 text-xs sm:text-sm focus:outline-none focus:border-blue-400 transition-colors"
                    />
                  </div>
                  <span className="text-[11px] text-slate-500 mt-1 block">
                    Found in the invitation email or letter provided by Fest Management
                  </span>
                </div>

                <button
                  type="submit"
                  disabled={tokenState === "verifying" || !tokenInput.trim()}
                  className="w-full py-3 px-4 rounded-xl font-bold text-xs sm:text-sm text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
                >
                  {tokenState === "verifying" ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Verifying Cryptographic Token...</span>
                    </>
                  ) : (
                    <>
                      <span>Verify & Continue</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            </div>
          ) : (
            /* STEP 2: Token Verified - Fill Account Details */
            <form onSubmit={handleAccept} className="space-y-5">
              {/* Verified Token Banner */}
              <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-950/40 via-indigo-950/30 to-slate-900 border border-blue-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> Verified Invitation
                  </span>
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    {invitationData.role === "JUDGE" ? (
                      <>
                        <Gavel className="w-3 h-3" /> Event Judge
                      </>
                    ) : (
                      <>
                        <Briefcase className="w-3 h-3" /> Sponsor Partner
                      </>
                    )}
                  </span>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1 text-slate-300">
                  <div>
                    <span className="text-slate-500 block">Bound Email:</span>
                    <strong className="text-white font-mono">{invitationData.email}</strong>
                  </div>
                  {invitationData.organization && (
                    <div>
                      <span className="text-slate-500 block">Organization:</span>
                      <strong className="text-white">{invitationData.organization}</strong>
                    </div>
                  )}
                  {invitationData.specialization && (
                    <div>
                      <span className="text-slate-500 block">Specialization / Domain:</span>
                      <strong className="text-slate-300">{invitationData.specialization}</strong>
                    </div>
                  )}
                  <div>
                    <span className="text-slate-500 block">Valid Until:</span>
                    <span className="text-amber-300 font-mono text-[11px]">
                      {new Date(invitationData.expires_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 pt-1 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                  Email is locked to prevent token interception.
                </div>
              </div>

              {submitError && (
                <div className="flex items-start gap-2.5 p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                  <span>{submitError}</span>
                </div>
              )}

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
                    placeholder="Enter your official full name"
                    className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-blue-400 transition-colors"
                  />
                </div>
              </div>

              {/* Password Fields */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Create Password *
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
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-blue-400 transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Confirm Password *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type="password"
                      required
                      minLength={6}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Repeat password"
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-blue-400 transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Phone & Website */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Phone Number
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
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-blue-400 transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Portfolio / Website / LinkedIn
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                      <Globe className="w-4 h-4" />
                    </div>
                    <input
                      type="url"
                      value={website}
                      onChange={(e) => setWebsite(e.target.value)}
                      placeholder="https://linkedin.com/in/..."
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-blue-400 transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Bio */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Professional Bio / Domain Profile
                </label>
                <div className="relative">
                  <div className="absolute top-3 left-3.5 pointer-events-none text-slate-500">
                    <FileText className="w-4 h-4" />
                  </div>
                  <textarea
                    rows={2}
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    placeholder="Short summary displayed on festival evaluation sheets..."
                    className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-blue-400 transition-colors resize-none"
                  />
                </div>
              </div>

              <div className="pt-2 flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setTokenState("idle");
                    setInvitationData(null);
                  }}
                  className="px-4 py-3 rounded-xl font-semibold text-xs text-slate-300 bg-slate-800 hover:bg-slate-700 transition-colors"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-3 px-4 rounded-xl font-bold text-xs sm:text-sm text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 transition-all shadow-lg shadow-blue-600/30 disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
                >
                  {submitting ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Activating Account...</span>
                    </>
                  ) : (
                    <>
                      <span>Accept Invitation & Enter Dashboard</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </form>
          )}

          <div className="mt-8 pt-5 border-t border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Are you a student participant?</span>
              <Link to="/register" className="font-semibold text-amber-400 hover:text-amber-300">
                Student Sign Up →
              </Link>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Applying as an Event Coordinator?</span>
              <Link to="/apply/coordinator" className="font-semibold text-amber-400 hover:text-amber-300">
                Coordinator Application →
              </Link>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Already activated your account?</span>
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

export default AcceptInvitationPage;
