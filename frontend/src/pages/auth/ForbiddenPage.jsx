import React from "react";
import { Link } from "react-router-dom";
import { ShieldAlert, ArrowLeft, Home } from "lucide-react";
import { useAuth, getRoleDashboardPath } from "../../auth/AuthContext";

export const ForbiddenPage = () => {
  const { user } = useAuth();
  const dashboardPath = user ? getRoleDashboardPath(user.role) : "/login";

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 mb-6 shadow-xl">
        <ShieldAlert className="w-8 h-8" />
      </div>

      <span className="text-xs font-bold uppercase tracking-widest text-rose-400">
        403 Forbidden Access
      </span>

      <h1 className="mt-2 text-3xl font-extrabold text-white tracking-tight">
        Access Denied
      </h1>

      <p className="mt-2 text-sm text-slate-400 max-w-md">
        You do not have the authorization privileges required to access this system module.
        Role-based permissions are strictly enforced by the backend API.
      </p>

      <div className="mt-8 flex items-center gap-4">
        <Link
          to={dashboardPath}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
        >
          <Home className="w-4 h-4" />
          <span>Fest Portal Home</span>
        </Link>
      </div>
    </div>
  );
};

export default ForbiddenPage;
