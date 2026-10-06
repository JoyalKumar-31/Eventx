import React, { useState, useEffect } from "react";
import { MapPin, Users, Building, Search, Compass, Info } from "lucide-react";
import { publicApi } from "../../api/publicApi";
import EmptyState from "../../components/EmptyState";

export default function VenuesPage() {
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchVenues();
  }, []);

  const fetchVenues = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await publicApi.getVenues();
      setVenues(data || []);
    } catch (err) {
      console.error("Failed to load venues", err);
      setError("Unable to load campus venues. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const filteredVenues = venues.filter(
    (v) =>
      v.name?.toLowerCase().includes(search.toLowerCase()) ||
      v.building?.toLowerCase().includes(search.toLowerCase()) ||
      v.code?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <Compass className="w-3.5 h-3.5" /> Campus Directory
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
            Festival Venues & Arenas
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-base sm:text-lg">
            Discover stages, auditoriums, high-tech labs, and sports complexes hosting events across the campus.
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md">
          <div className="relative w-full sm:w-96">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by venue name, building, or code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
            />
          </div>
          <span className="text-xs text-slate-400 hidden sm:inline">
            Showing {filteredVenues.length} of {venues.length} venues
          </span>
        </div>

        {/* Venue Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-56 rounded-2xl bg-slate-900 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-center">
            {error}
          </div>
        ) : filteredVenues.length === 0 ? (
          <EmptyState
            icon={MapPin}
            title="No Venues Found"
            description="No venues matched your search criteria."
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVenues.map((venue) => (
              <div
                key={venue.id}
                className="group relative p-6 rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all hover:shadow-xl hover:shadow-emerald-500/5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {venue.code || `V-${venue.id}`}
                    </span>
                    {venue.capacity && (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                        <Users className="w-3 h-3" /> {venue.capacity} seats
                      </span>
                    )}
                  </div>

                  <h3 className="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors mb-2">
                    {venue.name}
                  </h3>

                  <div className="space-y-1.5 text-xs text-slate-400 mb-4">
                    <div className="flex items-center gap-2">
                      <Building className="w-3.5 h-3.5 text-slate-500" />
                      <span>
                        {venue.building || "Main Campus"}
                        {venue.floor ? ` • Floor ${venue.floor}` : ""}
                        {venue.room_number ? ` • Room ${venue.room_number}` : ""}
                      </span>
                    </div>
                  </div>

                  {venue.facilities && (
                    <div className="mt-3 pt-3 border-t border-slate-800/80">
                      <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
                        <Info className="w-3 h-3" /> Facilities & Amenities
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {venue.facilities}
                      </p>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
                  <span>Status: <strong className="text-emerald-400 font-medium">Active Hub</strong></span>
                  <span className="group-hover:translate-x-1 transition-transform text-slate-400">
                    Campus Map Ref →
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
