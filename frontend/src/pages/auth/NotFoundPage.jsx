import React from "react";
import { Link } from "react-router-dom";
import { HelpCircle, Home } from "lucide-react";

export const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-6 shadow-xl">
        <HelpCircle className="w-8 h-8" />
      </div>

      <span className="text-xs font-bold uppercase tracking-widest text-indigo-400">
        404 Page Not Found
      </span>

      <h1 className="mt-2 text-3xl font-extrabold text-white tracking-tight">
        Lost on Campus?
      </h1>

      <p className="mt-2 text-sm text-slate-400 max-w-md">
        The requested fest destination or resource could not be found.
      </p>

      <div className="mt-8">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all"
        >
          <Home className="w-4 h-4" />
          <span>Back to Fest Home</span>
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;
