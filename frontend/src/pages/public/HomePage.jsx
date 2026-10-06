import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Sparkles,
  ArrowRight,
  Calendar,
  Users,
  Award,
  ShieldCheck,
  Ticket,
  Trophy,
  HelpCircle,
  Megaphone,
  Star,
  ChevronDown
} from "lucide-react";
import { publicApi } from "../../api/publicApi";
import { eventApi } from "../../api/eventApi";
import { sponsorApi } from "../../api/sponsorApi";
import { announcementApi } from "../../api/announcementApi";
import { EventCard } from "../../components/EventCard";
import { EmptyState } from "../../components/EmptyState";

export const HomePage = () => {
  const [stats, setStats] = useState({ total_events: 0, total_participants: 0, total_categories: 0, total_venues: 0 });
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [sponsors, setSponsors] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [faqOpen, setFaqOpen] = useState(null);

  useEffect(() => {
    const loadHomeData = async () => {
      try {
        const [statsData, eventsData, catsData, sponsorsData, annData] = await Promise.allSettled([
          publicApi.getStats(),
          eventApi.getEvents({ limit: 6 }),
          eventApi.getCategories(),
          sponsorApi.getActivePromotions(),
          announcementApi.getAnnouncements(),
        ]);

        if (statsData.status === "fulfilled") setStats(statsData.value);
        if (eventsData.status === "fulfilled") setEvents(eventsData.value);
        if (catsData.status === "fulfilled") setCategories(catsData.value);
        if (sponsorsData.status === "fulfilled") setSponsors(sponsorsData.value);
        if (annData.status === "fulfilled") setAnnouncements(annData.value);
      } catch (err) {
        console.error("Home data fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    loadHomeData();
  }, []);

  const faqs = [
    {
      q: "How do I register for fest events?",
      a: "Create an account as a Student or sign in. Browse events, check eligibility, select your event, and click Register. For team events, you can create a team and invite classmates or join an existing team via invite code.",
    },
    {
      q: "How does the digital QR entry pass work?",
      a: "Once your registration is confirmed (and fee verified if applicable), a tamper-resistant QR code pass is automatically generated on your dashboard. Present this pass on your phone at event check-in points.",
    },
    {
      q: "When and where do I get my certificate?",
      a: "After judging evaluations are completed and coordinators publish official results, verified PDF certificates of excellence and participation become immediately downloadable from your Student Portal.",
    },
    {
      q: "How are competition scores calculated?",
      a: "Assigned judges evaluate submissions across structured criteria (e.g., technical difficulty, innovation, presentation). Aggregated weighted scores auto-generate dynamic real-time leaderboards.",
    },
  ];

  return (
    <div className="space-y-24 pb-20">
      {/* 1. Hero Section with Permanent Cinematic Background Video */}
      <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden rounded-3xl border border-slate-800/80 mx-2 sm:mx-6 lg:mx-8 shadow-2xl bg-black">
        {/* Permanent Background Video Layer */}
        <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover opacity-75 filter brightness-90 contrast-110"
          >
            <source src="/hero-video.mp4" type="video/mp4" />
          </video>

          {/* Clean Cinematic Dark Overlays */}
          <div className="absolute inset-0 bg-black/45" />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-black/60" />
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10 py-20 flex flex-col items-center">
          {/* Top Pill Tag (matches reference) */}
          <div className="inline-flex items-center px-4 py-1 rounded-full border border-white/30 bg-black/40 backdrop-blur-md text-white text-[11px] sm:text-xs font-semibold tracking-widest uppercase mb-10 shadow-lg">
            <span>COLLEGE FESTIVAL 2026</span>
          </div>

          {/* Subtitle (matches reference) */}
          <p className="text-base sm:text-xl font-medium text-white/95 tracking-wide mb-3 drop-shadow-md">
            Annual Cultural, Sports & Technical Extravaganza
          </p>

          {/* Main Headline: "You're Invited" with elegant italic serif (matches reference) */}
          <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black text-white tracking-tight drop-shadow-2xl mb-8">
            You're <span className="font-serif italic font-normal tracking-normal text-white">Invited</span>
          </h1>

          <p className="text-sm sm:text-base text-slate-200/90 max-w-xl mx-auto mb-10 leading-relaxed font-light drop-shadow">
            Experience 50+ flagship competitions, esports showdowns, hackathons, musical star nights, and real-time fest leaderboards.
          </p>

          {/* Rounded White Pill Button (matches reference) */}
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/events"
              className="inline-flex items-center gap-2.5 px-8 py-3.5 rounded-full bg-white hover:bg-slate-100 text-slate-950 font-bold text-sm sm:text-base transition-all shadow-2xl hover:scale-105 duration-200"
            >
              <span>Explore Events</span>
              <ArrowRight className="w-4 h-4 text-slate-950" />
            </Link>

            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-black/50 hover:bg-black/70 text-white font-semibold text-sm sm:text-base border border-white/25 backdrop-blur-md transition-all shadow-xl hover:scale-105 duration-200"
            >
              <span>Student Register</span>
            </Link>

            <Link
              to="/login"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full bg-slate-900/60 hover:bg-slate-900 text-slate-300 hover:text-white font-medium text-sm border border-slate-700/60 backdrop-blur-md transition-all"
            >
              <span>Portal Login</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 2. Fest Statistics (Calculated strictly from Real Database) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 sm:p-8 rounded-3xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-xl">
          <div className="text-center p-3">
            <div className="text-3xl sm:text-4xl font-extrabold text-white">
              {stats.total_events}
            </div>
            <p className="mt-1 text-xs text-slate-400 font-medium">Published Events</p>
          </div>
          <div className="text-center p-3 border-l border-slate-800/80">
            <div className="text-3xl sm:text-4xl font-extrabold text-indigo-400">
              {stats.total_participants}
            </div>
            <p className="mt-1 text-xs text-slate-400 font-medium">Registered Participants</p>
          </div>
          <div className="text-center p-3 border-l border-slate-800/80">
            <div className="text-3xl sm:text-4xl font-extrabold text-white">
              {stats.total_categories}
            </div>
            <p className="mt-1 text-xs text-slate-400 font-medium">Event Categories</p>
          </div>
          <div className="text-center p-3 border-l border-slate-800/80">
            <div className="text-3xl sm:text-4xl font-extrabold text-emerald-400">
              {stats.total_venues}
            </div>
            <p className="mt-1 text-xs text-slate-400 font-medium">Campus Venues</p>
          </div>
        </div>
      </section>

      {/* 3. Event Categories Carousel / Grid */}
      {categories.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Explore by Category</h2>
              <p className="text-xs text-slate-400 mt-1">Competitions across technical, cultural, and sports domains</p>
            </div>
            <Link to="/events" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
              <span>View all</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {categories.map((cat) => (
              <Link
                key={cat.id}
                to={`/events?category=${cat.id}`}
                className="group p-4 rounded-2xl border border-slate-800 bg-slate-900/50 hover:bg-slate-850 hover:border-slate-700 transition-all text-center flex flex-col items-center justify-center shadow-xs"
              >
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-2.5 group-hover:scale-110 transition-transform">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h4 className="text-xs font-bold text-slate-200 group-hover:text-indigo-400">{cat.name}</h4>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* 4. Upcoming & Featured Events */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Upcoming Competitions</h2>
            <p className="text-xs text-slate-400 mt-1">Real events ready for enrollment and team formation</p>
          </div>
          <Link to="/events" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
            <span>Explore catalog</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {events.length === 0 ? (
          <EmptyState
            title="No events scheduled yet"
            description="Event coordinators have not published competitions yet. Check back soon!"
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </section>

      {/* 5. How It Works Pipeline */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 sm:p-12 rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/90 to-slate-950">
          <div className="text-center max-w-xl mx-auto mb-12">
            <span className="text-xs uppercase font-bold tracking-widest text-indigo-400">Seamless Workflow</span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">The Fest Journey</h2>
            <p className="text-xs text-slate-400 mt-2">
              From registration to digital stage scoring and verifiable certificate issuance.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 text-center">
            {[
              { step: "01", title: "Register", desc: "Select solo or team event & verify student identity.", icon: Users },
              { step: "02", title: "Payment", desc: "Secure checkout with instant automated invoice.", icon: Ticket },
              { step: "03", title: "QR Entry", desc: "Digital ticket pass scanned at the campus venue.", icon: ShieldCheck },
              { step: "04", title: "Judging", desc: "Multi-criteria live scoring & dynamic auto-ranking.", icon: Trophy },
              { step: "05", title: "Certificate", desc: "Download high-res PDF certificate with verification hash.", icon: Award },
            ].map((st, i) => {
              const Icon = st.icon;
              return (
                <div key={st.step} className="p-5 rounded-2xl border border-slate-800/80 bg-slate-950/60 relative">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto mb-3">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-bold text-slate-500 tracking-wider">STEP {st.step}</span>
                  <h4 className="text-sm font-bold text-white mt-1">{st.title}</h4>
                  <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{st.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 6. Active Sponsors Section */}
      {sponsors.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <span className="text-xs uppercase font-bold tracking-widest text-sky-400">Partners & Sponsors</span>
            <h2 className="text-2xl font-bold text-white mt-1">Empowering Campus Talent</h2>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {sponsors.map((sp) => (
              <div
                key={sp.id}
                onClick={() => sp.target_url && sponsorApi.trackClick(sp.id)}
                className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900 text-center flex flex-col items-center justify-center transition-all"
              >
                {sp.asset_url ? (
                  <img src={sp.asset_url} alt={sp.title} className="h-10 object-contain mb-2" />
                ) : (
                  <Star className="w-6 h-6 text-sky-400 mb-2" />
                )}
                <span className="text-xs font-semibold text-slate-200">{sp.title}</span>
                <span className="text-[10px] text-slate-500 uppercase mt-0.5">{sp.slot_type}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 7. Announcements / Campus Notices */}
      {announcements.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="p-6 sm:p-8 rounded-3xl border border-indigo-500/20 bg-indigo-950/15">
            <div className="flex items-center gap-2 text-indigo-400 mb-4">
              <Megaphone className="w-5 h-5" />
              <h3 className="text-base font-bold text-white">Official Fest Broadcasts</h3>
            </div>
            <div className="space-y-3">
              {announcements.slice(0, 3).map((a) => (
                <div key={a.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-slate-200">{a.title}</h5>
                    <span className="text-[10px] text-slate-500">{new Date(a.created_at).toLocaleDateString()}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400 leading-relaxed">{a.content}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* 8. FAQ Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-white tracking-tight">Frequently Asked Questions</h2>
          <p className="text-xs text-slate-400 mt-1">Everything you need to know about fest participation</p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden"
            >
              <button
                onClick={() => setFaqOpen(faqOpen === idx ? null : idx)}
                className="w-full p-4 text-left flex items-center justify-between text-xs font-bold text-slate-200 hover:text-white"
              >
                <span>{faq.q}</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${faqOpen === idx ? "rotate-180 text-indigo-400" : "text-slate-500"}`} />
              </button>
              {faqOpen === idx && (
                <div className="px-4 pb-4 text-xs text-slate-400 leading-relaxed border-t border-slate-800/60 pt-3">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default HomePage;
