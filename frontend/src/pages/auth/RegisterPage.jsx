import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, Mail, Lock, User, Phone, ArrowRight, AlertCircle } from "lucide-react";
import { useAuth, getRoleDashboardPath } from "../../auth/AuthContext";

export const RegisterPage = () => {
  const [role, setRole] = useState("STUDENT");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");

  // Student Profile Fields
  const [collegeName, setCollegeName] = useState("");
  const [studentId, setStudentId] = useState("");
  const [department, setDepartment] = useState("");
  const [yearOfStudy, setYearOfStudy] = useState("1st Year");

  // Coordinator Profile Fields
  const [coordDept, setCoordDept] = useState("");
  const [coordDesignation, setCoordDesignation] = useState("");

  // Judge Profile Fields
  const [judgeOrg, setJudgeOrg] = useState("");
  const [judgeSpecialization, setJudgeSpecialization] = useState("");

  // Sponsor Profile Fields
  const [companyName, setCompanyName] = useState("");
  const [industry, setIndustry] = useState("");
  const [website, setWebsite] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { register, login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const payload = {
      email,
      password,
      full_name: fullName,
      role,
      phone,
    };

    if (role === "STUDENT") {
      payload.student_profile = {
        college_name: collegeName,
        student_id_number: studentId,
        department,
        year_of_study: yearOfStudy,
      };
    } else if (role === "EVENT_COORDINATOR") {
      payload.coordinator_profile = {
        department: coordDept,
        designation: coordDesignation,
      };
    } else if (role === "JUDGE") {
      payload.judge_profile = {
        organization: judgeOrg,
        specialization: judgeSpecialization,
      };
    } else if (role === "SPONSOR") {
      payload.sponsor_profile = {
        company_name: companyName,
        industry,
        website,
      };
    }

    try {
      await register(payload);
      // Auto-login upon registration
      const user = await login(email, password);
      const dest = getRoleDashboardPath(user.role);
      navigate(dest, { replace: true });
    } catch (err) {
      setError(
        err.response?.data?.message || "Registration failed. Please check your information."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 selection:bg-amber-500/30 selection:text-amber-200">
      <div className="sm:mx-auto sm:w-full sm:max-w-lg text-center">
        <Link to="/" className="inline-flex items-center gap-2.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 via-amber-400 to-yellow-300 flex items-center justify-center text-slate-950 shadow-xl shadow-amber-500/30">
            <Sparkles className="w-6 h-6" />
          </div>
        </Link>
        <h2 className="mt-4 text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
          Create Fest Account
        </h2>
        <p className="mt-2 text-xs sm:text-sm text-slate-400">
          Join the university fest platform as a student participant, coordinator, judge, or partner.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-lg px-4 sm:px-0">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 sm:p-8 backdrop-blur-xl shadow-2xl shadow-black/40">
          {error && (
            <div className="mb-6 flex items-start gap-2.5 p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          {/* Account Role Tabs */}
          <div className="mb-6">
            <label className="block text-xs font-semibold text-slate-300 mb-2">Account Type</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 p-1 rounded-2xl bg-slate-950 border border-slate-800">
              {[
                { id: "STUDENT", label: "Student" },
                { id: "EVENT_COORDINATOR", label: "Coordinator" },
                { id: "JUDGE", label: "Judge" },
                { id: "SPONSOR", label: "Sponsor" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setRole(tab.id)}
                  className={`py-2 px-2 rounded-xl text-xs font-semibold transition-all text-center ${
                    role === tab.id
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Common Details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300">Full Name</label>
                <div className="mt-1 relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Alex Morgan"
                    className="w-full pl-9 pr-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Phone Number</label>
                <div className="mt-1 relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                    <Phone className="w-4 h-4" />
                  </div>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 9876543210"
                    className="w-full pl-9 pr-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300">Email Address</label>
                <div className="mt-1 relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="alex@institution.edu"
                    className="w-full pl-9 pr-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Password</label>
                <div className="mt-1 relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min 6 characters"
                    className="w-full pl-9 pr-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
            </div>

            {/* Role-Specific Profile Sections */}
            {role === "STUDENT" && (
              <div className="pt-3 border-t border-slate-800 space-y-3">
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block">
                  Student Verification Details
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300">College / Institute Name</label>
                    <input
                      type="text"
                      required
                      value={collegeName}
                      onChange={(e) => setCollegeName(e.target.value)}
                      placeholder="Indian Institute of Technology"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Student Roll / ID Number</label>
                    <input
                      type="text"
                      required
                      value={studentId}
                      onChange={(e) => setStudentId(e.target.value)}
                      placeholder="2024CS1092"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Department / Major</label>
                    <input
                      type="text"
                      required
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      placeholder="Computer Science & Engg"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Year of Study</label>
                    <select
                      value={yearOfStudy}
                      onChange={(e) => setYearOfStudy(e.target.value)}
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="1st Year">1st Year</option>
                      <option value="2nd Year">2nd Year</option>
                      <option value="3rd Year">3rd Year</option>
                      <option value="4th Year">4th Year</option>
                      <option value="Postgraduate">Postgraduate</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {role === "EVENT_COORDINATOR" && (
              <div className="pt-3 border-t border-slate-800 space-y-3">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block">
                  Coordinator Profile
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Department / Society</label>
                    <input
                      type="text"
                      required
                      value={coordDept}
                      onChange={(e) => setCoordDept(e.target.value)}
                      placeholder="Technical Arts Society"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Designation / Role</label>
                    <input
                      type="text"
                      required
                      value={coordDesignation}
                      onChange={(e) => setCoordDesignation(e.target.value)}
                      placeholder="Lead Organizer / Faculty"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {role === "JUDGE" && (
              <div className="pt-3 border-t border-slate-800 space-y-3">
                <span className="text-xs font-bold text-amber-400 uppercase tracking-wider block">
                  Judge Profile
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Organization / Affiliation</label>
                    <input
                      type="text"
                      required
                      value={judgeOrg}
                      onChange={(e) => setJudgeOrg(e.target.value)}
                      placeholder="Google DeepMind / Faculty"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Area of Specialization</label>
                    <input
                      type="text"
                      required
                      value={judgeSpecialization}
                      onChange={(e) => setJudgeSpecialization(e.target.value)}
                      placeholder="Artificial Intelligence & Robotics"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {role === "SPONSOR" && (
              <div className="pt-3 border-t border-slate-800 space-y-3">
                <span className="text-xs font-bold text-sky-400 uppercase tracking-wider block">
                  Sponsor Organization
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Company Name</label>
                    <input
                      type="text"
                      required
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="TechCorp Innovations"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Industry Sector</label>
                    <input
                      type="text"
                      required
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      placeholder="Software & Hardware"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Website</label>
                    <input
                      type="url"
                      value={website}
                      onChange={(e) => setWebsite(e.target.value)}
                      placeholder="https://company.com"
                      className="mt-1 w-full px-3 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-4 w-full py-3 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition-all shadow-md shadow-indigo-600/20 cursor-pointer flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Complete Registration</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-slate-800 text-center">
            <p className="text-xs text-slate-400">
              Already have an account?{" "}
              <Link to="/login" className="font-semibold text-indigo-400 hover:text-indigo-300">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
