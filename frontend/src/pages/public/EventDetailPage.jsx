import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Calendar, MapPin, Users, Ticket, ShieldAlert, CheckCircle, ArrowLeft, Mail, Award, Clock } from "lucide-react";
import { eventApi } from "../../api/eventApi";
import { registrationApi } from "../../api/registrationApi";
import { useAuth } from "../../auth/AuthContext";
import { StatusBadge } from "../../components/StatusBadge";
import { PaymentModal } from "../../components/PaymentModal";

export const EventDetailPage = () => {
  const { id } = useParams();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [isRegistered, setIsRegistered] = useState(false);
  const [paymentReg, setPaymentReg] = useState(null);

  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      try {
        const data = await eventApi.getEventById(id);
        setEvent(data);

        if (isAuthenticated && user?.role === "STUDENT") {
          const myRegs = await registrationApi.getMyRegistrations();
          const found = myRegs.find((r) => r.event_id === parseInt(id));
          if (found) setIsRegistered(true);
        }
      } catch (err) {
        setError(err.response?.data?.message || "Failed to load event details.");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id, isAuthenticated]);

  const handleRegister = async () => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    if (user?.role !== "STUDENT" && user?.role !== "ADMIN") {
      alert("Only students may register for competitions.");
      return;
    }

    if (event.is_team_event) {
      navigate(`/student/teams?event=${event.id}`);
      return;
    }

    try {
      const reg = await registrationApi.register({ event_id: event.id });
      setIsRegistered(true);
      if (event.registration_fee > 0) {
        setPaymentReg(reg);
      } else {
        alert("Registration confirmed! Entry pass is now available in your dashboard.");
      }
    } catch (err) {
      alert(err.response?.data?.message || "Registration failed.");
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="mt-4 text-xs text-slate-400">Loading competition details...</p>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center">
        <ShieldAlert className="w-12 h-12 text-rose-400 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white">Event Unavailable</h2>
        <p className="mt-2 text-xs text-slate-400">{error || "Event not found"}</p>
        <Link to="/events" className="mt-6 inline-flex items-center gap-2 text-xs font-semibold text-indigo-400 hover:text-indigo-300">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to catalog</span>
        </Link>
      </div>
    );
  }

  const coverUrl = event.cover_image?.url || event.banner_image_url || null;
  const spotsLeft = Math.max(0, event.max_participants - event.current_participants);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back Link */}
      <div>
        <Link to="/events" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to All Events</span>
        </Link>
      </div>

      {/* Hero Event Cover Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-950 aspect-[21/9] min-h-[300px] shadow-2xl">
        {coverUrl ? (
          <img src={coverUrl} alt={event.title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-gradient-to-tr from-indigo-950 via-slate-900 to-black flex items-center justify-center p-8">
            <span className="text-sm font-semibold uppercase tracking-widest text-indigo-400/80">
              {event.category?.name || "Campus Fest Event"}
            </span>
          </div>
        )}

        {/* Readability Gradient Layer */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent p-6 sm:p-10 flex flex-col justify-end">
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="px-3 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider bg-slate-900/80 border border-slate-700 text-indigo-300 backdrop-blur-md">
              {event.category?.name || "General"}
            </span>
            <StatusBadge status={event.status} />
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            {event.title}
          </h1>

          <div className="mt-4 flex flex-wrap items-center gap-4 sm:gap-6 text-xs text-slate-200">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-indigo-400" />
              {new Date(event.start_time).toLocaleDateString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
            </span>
            <span className="flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-indigo-400" />
              {event.venue?.name || "Campus Auditorium"}
            </span>
            <span className="flex items-center gap-1.5">
              <Users className="w-4 h-4 text-indigo-400" />
              {event.is_team_event ? `Team (${event.min_team_size}-${event.max_team_size} members)` : "Solo Entry"}
            </span>
            <span className="flex items-center gap-1.5 text-emerald-400 font-bold">
              <Ticket className="w-4 h-4 text-emerald-400" />
              {event.registration_fee > 0 ? `₹${event.registration_fee.toFixed(0)}` : "Free Entry"}
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Details + Registration Action Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left 2 Cols: Tabs & Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Navigation Tabs */}
          <div className="flex items-center gap-1 p-1 rounded-2xl bg-slate-900 border border-slate-800 text-xs font-semibold overflow-x-auto">
            {["overview", "rules", "rounds", "schedule"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-2 px-3 rounded-xl capitalize transition-all whitespace-nowrap cursor-pointer ${
                  activeTab === tab
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab 1: Overview */}
          {activeTab === "overview" && (
            <div className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-md">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">About The Competition</h3>
                <p className="mt-2 text-xs sm:text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                  {event.description}
                </p>
              </div>

              {event.prize_pool && (
                <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center gap-3">
                  <Award className="w-6 h-6 text-amber-400 shrink-0" />
                  <div>
                    <h5 className="text-xs font-bold text-amber-300">Prize Pool / Awards</h5>
                    <p className="text-xs text-slate-300 mt-0.5">{event.prize_pool}</p>
                  </div>
                </div>
              )}

              {event.coordinator && (
                <div className="pt-4 border-t border-slate-800 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">
                    {event.coordinator.full_name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-white">{event.coordinator.full_name}</p>
                    <span className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                      <Mail className="w-3 h-3" />
                      {event.coordinator.email}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Rules */}
          {activeTab === "rules" && (
            <div className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-md">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Competition Rules & Eligibility</h3>
              {event.rules && event.rules.length > 0 ? (
                <div className="space-y-3">
                  {event.rules.map((rule, idx) => (
                    <div key={rule.id} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <h4 className="text-xs font-bold text-indigo-300">
                        {rule.rule_order}. {rule.title}
                      </h4>
                      <p className="mt-1 text-xs text-slate-400 leading-relaxed">{rule.description}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No specific rules posted yet. Standard university conduct applies.</p>
              )}
            </div>
          )}

          {/* Tab 3: Rounds */}
          {activeTab === "rounds" && (
            <div className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-md">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Event Rounds</h3>
              {event.rounds && event.rounds.length > 0 ? (
                <div className="space-y-3">
                  {event.rounds.map((rnd) => (
                    <div key={rnd.id} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-white">
                          Round {rnd.round_number}: {rnd.name}
                        </h4>
                      </div>
                      {rnd.description && <p className="mt-1 text-xs text-slate-400">{rnd.description}</p>}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">Single-round competition format.</p>
              )}
            </div>
          )}

          {/* Tab 4: Schedule */}
          {activeTab === "schedule" && (
            <div className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-md">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Timeline & Venues</h3>
              {event.schedules && event.schedules.length > 0 ? (
                <div className="space-y-3">
                  {event.schedules.map((sc) => (
                    <div key={sc.id} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between">
                      <div>
                        <h4 className="text-xs font-bold text-white">{sc.title}</h4>
                        <span className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                          <Clock className="w-3 h-3 text-indigo-400" />
                          {new Date(sc.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} - {new Date(sc.end_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </span>
                      </div>
                      <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
                        {sc.venue?.name || "Main Venue"}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">Schedule timeline will be confirmed prior to fest opening.</p>
              )}
            </div>
          )}
        </div>

        {/* Right 1 Col: Registration CTA Box */}
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 backdrop-blur-xl shadow-xl space-y-5">
          <div>
            <span className="text-xs uppercase font-bold tracking-wider text-slate-400">Registration Status</span>
            <div className="mt-1 flex items-center justify-between">
              <span className="text-2xl font-extrabold text-white">
                {event.registration_fee > 0 ? `₹${event.registration_fee.toFixed(0)}` : "Free"}
              </span>
              <span className="text-xs text-slate-400">
                {spotsLeft} / {event.max_participants} slots open
              </span>
            </div>
          </div>

          <div className="space-y-2 border-t border-slate-800 pt-4 text-xs text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-400">Deadline:</span>
              <span className="font-semibold text-white">
                {new Date(event.registration_deadline).toLocaleDateString([], { month: "short", day: "numeric" })}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Participation:</span>
              <span className="font-semibold text-white">
                {event.is_team_event ? "Team Required" : "Individual"}
              </span>
            </div>
          </div>

          {isRegistered ? (
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-center">
              <CheckCircle className="w-6 h-6 text-emerald-400 mx-auto mb-1.5" />
              <p className="text-xs font-bold text-white">You Are Registered!</p>
              <Link
                to="/student/passes"
                className="mt-2 inline-block text-xs font-semibold text-indigo-400 hover:text-indigo-300 underline underline-offset-2"
              >
                View Your Digital QR Pass
              </Link>
            </div>
          ) : (
            <button
              onClick={handleRegister}
              disabled={spotsLeft === 0 || event.status === "REGISTRATION_CLOSED"}
              className="w-full py-3 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition-all shadow-md shadow-indigo-600/20 cursor-pointer"
            >
              {spotsLeft === 0 ? "Event Full" : event.is_team_event ? "Register with Team" : "Register Now"}
            </button>
          )}
        </div>
      </div>

      {paymentReg && (
        <PaymentModal
          isOpen={!!paymentReg}
          onClose={() => setPaymentReg(null)}
          registration={paymentReg}
          onPaymentSuccess={() => setPaymentReg(null)}
        />
      )}
    </div>
  );
};

export default EventDetailPage;
