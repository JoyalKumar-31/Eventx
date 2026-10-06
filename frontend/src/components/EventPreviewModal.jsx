import React from "react";
import { X, Calendar, MapPin, Users, Ticket, CheckCircle2 } from "lucide-react";
import { EventCard } from "./EventCard";

export const EventPreviewModal = ({
  isOpen = true,
  onClose,
  formData = {},
  coverImagePreview,
  categories = [],
  venues = [],
  event = null,
}) => {
  if (isOpen === false) return null;

  const data = event || formData;
  const categoryObj = data.category || categories.find((c) => c.id === parseInt(data.category_id)) || {
    name: "General",
  };
  const venueObj = data.venue || venues.find((v) => v.id === parseInt(data.venue_id)) || {
    name: "Main Campus Arena",
    building: "Auditorium Block",
  };

  const previewEvent = {
    id: data.id || 0,
    title: data.title || "Untitled Fest Event",
    description: data.short_description || data.description || "No event description provided yet.",
    category: categoryObj,
    venue: venueObj,
    start_time: data.start_date || data.start_time,
    registration_fee: parseFloat(data.registration_fee) || 0,
    max_participants: parseInt(data.max_participants) || 50,
    current_participants: 0,
    is_team_event: data.event_format === "TEAM" || data.is_team_event,
    cover_image: (data.primary_media_url || coverImagePreview) ? { url: data.primary_media_url || coverImagePreview } : null,
    status: "DRAFT",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-4xl rounded-3xl border border-slate-700 bg-slate-900 p-6 md:p-8 shadow-2xl my-8">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <span>Event Live Preview</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Coordinator Mode
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Review how attendees will experience your event across cards and details before publishing.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          {/* Section 1: Preview on Cards */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              1. Catalog & Discovery Card Preview
            </h4>
            <div className="max-w-sm">
              <EventCard event={previewEvent} />
            </div>
          </div>

          {/* Section 2: Preview on Detail Hero Banner */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              2. Event Hero Banner Preview
            </h4>
            <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 aspect-video shadow-lg">
              {coverImagePreview ? (
                <img
                  src={coverImagePreview}
                  alt="Cover Hero Preview"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-indigo-900 via-slate-900 to-black flex items-center justify-center p-6 text-center">
                  <span className="text-sm font-medium text-slate-400">Default Category Banner</span>
                </div>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent p-5 flex flex-col justify-end">
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                  {categoryObj.name}
                </span>
                <h2 className="text-xl font-bold text-white mt-1">{previewEvent.title}</h2>
                <div className="mt-2 flex items-center gap-4 text-xs text-slate-300">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                    {formData.start_time ? new Date(formData.start_time).toLocaleDateString() : "TBA"}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                    {venueObj.name}
                  </span>
                </div>
              </div>
            </div>

            {/* Rules / Rounds checklist preview */}
            <div className="mt-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
              <h5 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Event Structure
              </h5>
              <div className="mt-2 space-y-1.5 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Fee: {previewEvent.registration_fee > 0 ? `₹${previewEvent.registration_fee}` : "Free"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Format: {formData.is_team_event ? `Team Event (${formData.min_team_size}-${formData.max_team_size} members)` : "Solo Entry"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Capacity: {formData.max_participants || 50} Participants</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/20"
          >
            Back to Editor
          </button>
        </div>
      </div>
    </div>
  );
};

export default EventPreviewModal;
