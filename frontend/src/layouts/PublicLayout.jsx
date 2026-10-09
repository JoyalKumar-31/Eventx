import React, { useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { Sparkles, Calendar, MapPin, Award, Megaphone, ShieldCheck, Menu, X, ArrowRight, User as UserIcon, LogOut } from "lucide-react";
import { useAuth, getRoleDashboardPath } from "../auth/AuthContext";
import FestAICopilot from "../components/FestAICopilot";

export const PublicLayout = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Events", path: "/events" },
    { name: "Schedule", path: "/schedule" },
    { name: "Venues", path: "/venues" },
    { name: "Announcements", path: "/announcements" },
    { name: "Results", path: "/results" },
    { name: "Verify Certificate", path: "/verify-certificate" },
  ];

  const isActive = (path) => {
    if (path === "/" && location.pathname !== "/") return false;
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo / Brand */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-amber-400 to-yellow-300 flex items-center justify-center text-slate-950 shadow-lg shadow-amber-500/30 group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="text-base font-extrabold tracking-tight text-white block leading-none">
                CAMPUS<span className="text-amber-400">FEST</span>
              </span>
              <span className="text-[10px] tracking-wider uppercase text-slate-400 font-semibold block mt-0.5">
                University Fest Portal
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive(link.path)
                    ? "bg-slate-800 text-amber-400 border border-slate-700/60 shadow-xs"
                    : "text-slate-300 hover:text-white hover:bg-slate-900"
                }`}
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* Right Auth CTA / User Profile */}
          <div className="hidden sm:flex items-center gap-3">
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <Link
                  to={getRoleDashboardPath(user?.role)}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all shadow-md shadow-amber-500/20"
                >
                  <UserIcon className="w-3.5 h-3.5" />
                  <span>Dashboard ({user?.role})</span>
                </Link>
                <button
                  onClick={logout}
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-slate-900 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-900 transition-colors"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all shadow-md shadow-amber-500/20"
                >
                  <span>Register</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden px-4 pt-2 pb-6 border-t border-slate-800 bg-slate-950/95 backdrop-blur-xl">
            <div className="flex flex-col gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-4 py-2.5 rounded-xl text-sm font-semibold ${
                    isActive(link.path)
                      ? "bg-slate-800 text-indigo-400"
                      : "text-slate-300 hover:bg-slate-900"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-slate-800 flex flex-col gap-2">
              {isAuthenticated ? (
                <>
                  <Link
                    to={getRoleDashboardPath(user?.role)}
                    onClick={() => setMobileMenuOpen(false)}
                    className="w-full text-center py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 text-white"
                  >
                    Open Dashboard ({user?.role})
                  </Link>
                  <button
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full text-center py-2 rounded-xl text-sm text-rose-400 bg-slate-900"
                  >
                    Log Out
                  </button>
                </>
              ) : (
                <div className="flex items-center gap-2">
                  <Link
                    to="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex-1 text-center py-2.5 rounded-xl text-sm font-semibold text-slate-300 bg-slate-900 border border-slate-800"
                  >
                    Log In
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex-1 text-center py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 text-white"
                  >
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Outlet */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* University Fest Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/90 text-slate-400 text-xs py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 font-bold text-white text-base">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <span>CAMPUSFEST 2026</span>
            </div>
            <p className="mt-2 text-slate-400 leading-relaxed">
              Official full-stack digital fest management platform. Real-time registrations, QR ticketing, digital scoring, automated certificates, and live event analytics.
            </p>
          </div>

          <div>
            <h5 className="font-semibold text-slate-200 uppercase tracking-wider mb-3">Fest Events</h5>
            <ul className="space-y-2">
              <li><Link to="/events" className="hover:text-white transition-colors">Browse All Events</Link></li>
              <li><Link to="/schedule" className="hover:text-white transition-colors">Event Timeline</Link></li>
              <li><Link to="/venues" className="hover:text-white transition-colors">Campus Venues</Link></li>
              <li><Link to="/results" className="hover:text-white transition-colors">Winners & Leaderboard</Link></li>
            </ul>
          </div>

          <div>
            <h5 className="font-semibold text-slate-200 uppercase tracking-wider mb-3">Verification & Portals</h5>
            <ul className="space-y-2">
              <li><Link to="/verify-certificate" className="hover:text-white transition-colors">Verify Certificate</Link></li>
              <li><Link to="/announcements" className="hover:text-white transition-colors">Fest Announcements</Link></li>
              <li><Link to="/login" className="hover:text-white transition-colors">Coordinator Portal</Link></li>
              <li><Link to="/login" className="hover:text-white transition-colors">Judge Portal</Link></li>
            </ul>
          </div>

          <div>
            <h5 className="font-semibold text-slate-200 uppercase tracking-wider mb-3">University Information</h5>
            <p className="leading-relaxed">
              Organized by the Council of Student Affairs & Technical Societies.<br />
              All rights reserved. Powered by FastAPI & React.
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 pt-6 border-t border-slate-900 text-center text-slate-400 text-xs">
          © 2026 College Fest Management Platform. Designed for Real Production Deployments.
        </div>
      </footer>

      {/* Fest AI Multi-Agent Copilot */}
      <FestAICopilot />
    </div>
  );
};
