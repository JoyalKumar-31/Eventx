import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Search, Filter, Sparkles, AlertCircle } from "lucide-react";
import { eventApi } from "../../api/eventApi";
import { registrationApi } from "../../api/registrationApi";
import { useAuth } from "../../auth/AuthContext";
import { EventCard } from "../../components/EventCard";
import { EmptyState } from "../../components/EmptyState";
import { PaymentModal } from "../../components/PaymentModal";

export const EventsPage = () => {
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("search") || "");
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get("category") || "");
  const [selectedFormat, setSelectedFormat] = useState(searchParams.get("format") || "ALL");
  const [loading, setLoading] = useState(true);
  const [registeredEventIds, setRegisteredEventIds] = useState(new Set());
  const [selectedEventForPayment, setSelectedEventForPayment] = useState(null);
  const [notificationMsg, setNotificationMsg] = useState(null);

  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (selectedCategory) params.category_id = selectedCategory;
      if (selectedFormat === "SOLO") params.is_team = false;
      if (selectedFormat === "TEAM") params.is_team = true;

      const data = await eventApi.getEvents(params);
      setEvents(data);

      if (isAuthenticated && user?.role === "STUDENT") {
        const myRegs = await registrationApi.getMyRegistrations();
        const ids = new Set(myRegs.map((r) => r.event_id));
        setRegisteredEventIds(ids);
      }
    } catch (err) {
      console.error("Failed to load events:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchCats = async () => {
      try {
        const cats = await eventApi.getCategories();
        setCategories(cats);
      } catch (err) {}
    };
    fetchCats();
  }, []);

  useEffect(() => {
    fetchEvents();
  }, [selectedCategory, selectedFormat]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchEvents();
  };

  const handleRegister = async (event) => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    if (user.role !== "STUDENT" && user.role !== "ADMIN") {
      alert("Only students can enroll in fest competitions.");
      return;
    }

    if (event.is_team_event) {
      navigate(`/student/teams?event=${event.id}`);
      return;
    }

    try {
      const reg = await registrationApi.register({ event_id: event.id });
      setRegisteredEventIds((prev) => new Set([...prev, event.id]));

      if (event.registration_fee > 0) {
        setSelectedEventForPayment(reg);
      } else {
        setNotificationMsg(`Registered successfully for "${event.title}"! Entry pass is generated.`);
        setTimeout(() => setNotificationMsg(null), 5000);
      }
    } catch (err) {
      alert(err.response?.data?.message || "Failed to register for this event.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">Event Catalog</h1>
        <p className="mt-1 text-xs sm:text-sm text-slate-400">
          Discover and register for campus competitions, hackathons, and cultural stages.
        </p>
      </div>

      {notificationMsg && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between shadow-lg">
          <span>{notificationMsg}</span>
          <button onClick={() => setNotificationMsg(null)} className="text-emerald-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between p-4 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search events by title or keyword..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </form>

        {/* Category Filter */}
        <div className="flex items-center gap-2">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2.5 rounded-xl text-xs bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>

          {/* Format Filter */}
          <select
            value={selectedFormat}
            onChange={(e) => setSelectedFormat(e.target.value)}
            className="px-3 py-2.5 rounded-xl text-xs bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="ALL">All Formats</option>
            <option value="SOLO">Solo Entry</option>
            <option value="TEAM">Team Event</option>
          </select>
        </div>
      </div>

      {/* Events Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-72 rounded-2xl bg-slate-900/40 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : events.length === 0 ? (
        <EmptyState
          title="No events found"
          description="Try broadening your search query or selecting a different category filter."
          actionText="Clear Filters"
          onAction={() => {
            setSearch("");
            setSelectedCategory("");
            setSelectedFormat("ALL");
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.map((event) => (
            <EventCard
              key={event.id}
              event={event}
              onRegister={handleRegister}
              isRegistered={registeredEventIds.has(event.id)}
            />
          ))}
        </div>
      )}

      {/* Payment Checkout Modal if Event has Fee */}
      {selectedEventForPayment && (
        <PaymentModal
          isOpen={!!selectedEventForPayment}
          onClose={() => setSelectedEventForPayment(null)}
          registration={selectedEventForPayment}
          onPaymentSuccess={() => {
            setSelectedEventForPayment(null);
            fetchEvents();
          }}
        />
      )}
    </div>
  );
};

export default EventsPage;
