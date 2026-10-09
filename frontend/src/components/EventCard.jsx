import React from "react";
import { Link } from "react-router-dom";
import { Calendar, MapPin, Users, Ticket, ArrowUpRight } from "lucide-react";
import { StatusBadge } from "./StatusBadge";

export const EventCard = ({
  event,
  onRegister,
  isRegistered = false,
  registrationStatus = null,
}) => {
  const {
    id,
    title,
    description,
    category,
    venue,
    start_time,
    registration_fee,
    max_participants,
    current_participants,
    is_team_event,
    cover_image,
    banner_image_url,
    status,
  } = event;

  // Determine cover image URL from backend API response
  const imageUrl = cover_image?.url || banner_image_url || null;

  // Formatted date
  const dateStr = start_time
    ? new Date(start_time).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "TBA";

  // Category fallback gradient styles if no image uploaded yet
  const getCategoryFallbackStyle = (catName = "") => {
    const lower = catName.toLowerCase();
    if (lower.includes("tech") || lower.includes("hack") || lower.includes("code")) {
      return "from-cyan-900/80 via-blue-950 to-slate-950";
    }
    if (lower.includes("cultur") || lower.includes("dance") || lower.includes("music") || lower.includes("art")) {
      return "from-fuchsia-900/80 via-purple-950 to-slate-950";
    }
    if (lower.includes("sport") || lower.includes("game") || lower.includes("esport")) {
      return "from-amber-900/80 via-orange-950 to-slate-950";
    }
    return "from-indigo-900/80 via-slate-900 to-slate-950";
  };

  const spotsLeft = Math.max(0, (max_participants || 0) - (current_participants || 0));
  const isFull = spotsLeft === 0;

  return (
    <div className="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70 shadow-lg shadow-black/30 backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-slate-700 hover:shadow-2xl hover:shadow-indigo-950/30">
      {/* Visual Cover Banner / Background */}
      <div className="relative h-48 w-full overflow-hidden bg-slate-950">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={title}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div
            className={`h-full w-full bg-gradient-to-br ${getCategoryFallbackStyle(
              category?.name
            )} flex items-center justify-center p-6 text-center`}
          >
            <div className="flex flex-col items-center">
              <span className="text-xs uppercase tracking-widest text-indigo-300/80 font-semibold">
                {category?.name || "Fest Event"}
              </span>
              <p className="mt-1 text-sm font-medium text-slate-300 line-clamp-1">{title}</p>
            </div>
          </div>
        )}

        {/* Readability Gradient Layer */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent" />

        {/* Top Badges */}
        <div className="absolute top-3 left-3 right-3 flex items-center justify-between gap-2">
          {category?.name && (
            <span className="px-2.5 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider bg-slate-900/80 border border-slate-700 text-slate-200 backdrop-blur-md shadow-sm">
              {category.name}
            </span>
          )}

          {registrationStatus ? (
            <StatusBadge status={registrationStatus} />
          ) : (
            <StatusBadge status={status} />
          )}
        </div>

        {/* Spots Left Pill */}
        <div className="absolute bottom-2.5 right-3">
          <span
            className={`text-xs px-2 py-0.5 rounded-md font-medium backdrop-blur-md ${
              isFull
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                : "bg-slate-900/80 text-slate-300 border border-slate-700/50"
            }`}
          >
            {isFull ? "Event Full" : `${spotsLeft} slots left`}
          </span>
        </div>
      </div>

      {/* Card Content & Metadata */}
      <div className="flex flex-1 flex-col p-5">
        <h4 className="text-lg font-bold text-white tracking-tight line-clamp-1 group-hover:text-indigo-400 transition-colors">
          {title}
        </h4>

        <p className="mt-1.5 text-xs text-slate-400 line-clamp-2 leading-relaxed">
          {description}
        </p>

        {/* Event Schedule & Venue info */}
        <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-300">
          <div className="flex items-center gap-1.5 truncate">
            <Calendar className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span className="truncate">{dateStr}</span>
          </div>

          <div className="flex items-center gap-1.5 truncate">
            <MapPin className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span className="truncate">{venue?.name || "Main Campus"}</span>
          </div>

          <div className="flex items-center gap-1.5 truncate">
            <Users className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span>{is_team_event ? "Team Participation" : "Solo Entry"}</span>
          </div>

          <div className="flex items-center gap-1.5 truncate">
            <Ticket className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span className="font-semibold text-emerald-400">
              {registration_fee > 0 ? `₹${registration_fee.toFixed(0)}` : "Free Registration"}
            </span>
          </div>
        </div>

        {/* Card Actions */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center gap-3">
          <Link
            to={`/events/${id}`}
            className="flex-1 inline-flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60 transition-colors text-center"
          >
            <span>Explore</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>

          {isRegistered ? (
            <Link
              to="/student/registrations"
              className="flex-1 inline-flex items-center justify-center px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 text-center"
            >
              Registered
            </Link>
          ) : (
            onRegister && (
              <button
                onClick={() => onRegister(event)}
                disabled={isFull || status === "REGISTRATION_CLOSED"}
                className={`flex-1 inline-flex items-center justify-center px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isFull || status === "REGISTRATION_CLOSED"
                    ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-800"
                    : "bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold shadow-md shadow-amber-500/20 cursor-pointer"
                }`}
              >
                Register
              </button>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default EventCard;
