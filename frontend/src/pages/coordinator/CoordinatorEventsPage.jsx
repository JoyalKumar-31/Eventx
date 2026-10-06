import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import {
  Calendar,
  PlusCircle,
  Edit,
  Trash2,
  Globe,
  Eye,
  CheckCircle,
  XCircle,
  AlertCircle,
  Upload,
  Layers,
  MapPin,
  DollarSign,
  FileText,
  Clock,
  ArrowLeft,
  ImageIcon,
} from "lucide-react";
import { eventApi } from "../../api/eventApi";
import { publicApi } from "../../api/publicApi";
import StatusBadge from "../../components/StatusBadge";
import EmptyState from "../../components/EmptyState";
import ImageUploadSection from "../../components/ImageUploadSection";
import EventPreviewModal from "../../components/EventPreviewModal";

const extractErrorMessage = (err, fallback = "An error occurred.") => {
  if (!err) return fallback;
  const detail = err.response?.data?.detail;
  if (!detail) {
    return err.response?.data?.message || err.message || fallback;
  }
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => `${d.loc ? d.loc.slice(-1)[0] + ": " : ""}${d.msg || JSON.stringify(d)}`).join("; ");
  }
  if (typeof detail === "object") {
    return detail.message || JSON.stringify(detail);
  }
  return String(detail);
};

const safeIsoDate = (dateVal, fallbackHoursFromNow = 24) => {
  if (dateVal) {
    const d = new Date(dateVal);
    if (!isNaN(d.getTime())) {
      return d.toISOString();
    }
  }
  const fallback = new Date(Date.now() + fallbackHoursFromNow * 3600 * 1000);
  return fallback.toISOString();
};

export default function CoordinatorEventsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const isNew = searchParams.get("action") === "new";
  const editId = searchParams.get("edit");
  const isEditing = Boolean(isNew || editId);

  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [currentEventId, setCurrentEventId] = useState(editId ? Number(editId) : null);
  const [title, setTitle] = useState("");
  const [shortDescription, setShortDescription] = useState("");
  const [fullDescription, setFullDescription] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [eventType, setEventType] = useState("TECHNICAL");
  const [eventFormat, setEventFormat] = useState("SOLO");
  const [minTeamSize, setMinTeamSize] = useState(1);
  const [maxTeamSize, setMaxTeamSize] = useState(1);
  const [registrationFee, setRegistrationFee] = useState(0);
  const [maxParticipants, setMaxParticipants] = useState(100);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [regDeadline, setRegDeadline] = useState("");
  const [venueId, setVenueId] = useState("");

  // Venue Management State
  const [showVenueModal, setShowVenueModal] = useState(false);
  const [venueModalMode, setVenueModalMode] = useState("create");
  const [venueName, setVenueName] = useState("");
  const [venueBuilding, setVenueBuilding] = useState("");
  const [venueFloor, setVenueFloor] = useState("");
  const [venueRoom, setVenueRoom] = useState("");
  const [venueCapacity, setVenueCapacity] = useState(100);
  const [venueMapLink, setVenueMapLink] = useState("");
  const [venueSaving, setVenueSaving] = useState(false);
  const [venueError, setVenueError] = useState(null);

  // Visuals / Media
  const [primaryMediaUrl, setPrimaryMediaUrl] = useState(null);
  const [uploadedMediaId, setUploadedMediaId] = useState(null);

  // Rules & Rounds
  const [rules, setRules] = useState([]);
  const [newRuleTitle, setNewRuleTitle] = useState("");
  const [newRuleDesc, setNewRuleDesc] = useState("");

  const [rounds, setRounds] = useState([]);
  const [newRoundName, setNewRoundName] = useState("");
  const [newRoundDesc, setNewRoundDesc] = useState("");

  // Feedback & Preview
  const [formError, setFormError] = useState(null);
  const [formSuccess, setFormSuccess] = useState(null);
  const [saving, setSaving] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (editId) {
      loadEventForEdit(Number(editId));
    } else if (isNew) {
      resetForm();
    }
  }, [editId, isNew]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [eventsData, catData, venuesData] = await Promise.all([
        eventApi.getMyCoordinatedEvents().catch(() => []),
        eventApi.getCategories().catch(() => []),
        eventApi.getVenues().catch(() => []),
      ]);
      setEvents(eventsData || []);
      setCategories(catData || []);
      setVenues(venuesData || []);

      if (catData && catData.length > 0 && !categoryId) {
        setCategoryId(catData[0].id);
      }
      if (venuesData && venuesData.length > 0 && !venueId) {
        setVenueId(venuesData[0].id);
      }
    } catch (err) {
      console.error("Failed to load initial data", err);
    } finally {
      setLoading(false);
    }
  };

  const loadEventForEdit = async (id) => {
    try {
      setLoading(true);
      const evt = await eventApi.getEventById(id);
      if (!evt) return;

      setCurrentEventId(evt.id);
      setTitle(evt.title || "");
      setShortDescription(evt.short_description || evt.description || "");
      setFullDescription(evt.full_description || evt.description || "");
      setCategoryId(evt.category_id || "");
      setEventType(evt.event_type || "GAMING");
      setEventFormat(evt.is_team_event ? "TEAM" : (evt.event_format || "SOLO"));
      setMinTeamSize(evt.min_team_size || 1);
      setMaxTeamSize(evt.max_team_size || 1);
      setRegistrationFee(evt.registration_fee || 0);
      setMaxParticipants(evt.max_participants || 100);
      setStartDate(evt.start_time ? evt.start_time.substring(0, 16) : (evt.start_date ? evt.start_date.substring(0, 16) : ""));
      setEndDate(evt.end_time ? evt.end_time.substring(0, 16) : (evt.end_date ? evt.end_date.substring(0, 16) : ""));
      setRegDeadline(evt.registration_deadline ? evt.registration_deadline.substring(0, 16) : "");
      setVenueId(evt.venue_id || "");
      setPrimaryMediaUrl(evt.primary_media_url || null);
      setRules(evt.rules || []);
      setRounds(evt.rounds || []);
    } catch (err) {
      console.error("Failed to load event details", err);
      setFormError(extractErrorMessage(err, "Could not load event for editing."));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAddVenue = () => {
    setVenueModalMode("create");
    setVenueName("");
    setVenueBuilding("");
    setVenueFloor("");
    setVenueRoom("");
    setVenueCapacity(100);
    setVenueMapLink("");
    setVenueError(null);
    setShowVenueModal(true);
  };

  const handleOpenEditVenue = () => {
    const selected = venues.find((v) => Number(v.id) === Number(venueId));
    if (!selected) {
      alert("Please select a venue first to edit its specifications.");
      return;
    }
    setVenueModalMode("edit");
    setVenueName(selected.name || "");
    setVenueBuilding(selected.building || "");
    setVenueFloor(selected.floor || "");
    setVenueRoom(selected.room_number || "");
    setVenueCapacity(selected.capacity || 100);
    setVenueMapLink(selected.coordinates_or_map_link || "");
    setVenueError(null);
    setShowVenueModal(true);
  };

  const handleSaveVenue = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!venueName.trim()) {
      setVenueError("Venue name is required.");
      return;
    }
    if (!venueBuilding.trim()) {
      setVenueError("Building / Complex is required.");
      return;
    }

    try {
      setVenueSaving(true);
      setVenueError(null);
      const payload = {
        name: venueName.trim(),
        building: venueBuilding.trim(),
        floor: venueFloor.trim() || null,
        room_number: venueRoom.trim() || null,
        capacity: Number(venueCapacity) || 100,
        coordinates_or_map_link: venueMapLink.trim() || null,
        is_active: true,
      };

      if (venueModalMode === "create") {
        const created = await eventApi.createVenue(payload);
        setVenues((prev) => [...prev, created]);
        setVenueId(created.id);
        setFormSuccess(`Venue "${created.name}" created and assigned!`);
      } else {
        const updated = await eventApi.updateVenue(Number(venueId), payload);
        setVenues((prev) => prev.map((v) => (v.id === updated.id ? updated : v)));
        setFormSuccess(`Venue "${updated.name}" specifications updated successfully!`);
      }
      setShowVenueModal(false);
    } catch (err) {
      console.error("Failed to save venue", err);
      setVenueError(extractErrorMessage(err, "Failed to save venue specifications."));
    } finally {
      setVenueSaving(false);
    }
  };

  const resetForm = () => {
    setCurrentEventId(null);
    setTitle("");
    setShortDescription("");
    setFullDescription("");
    setEventType("TECHNICAL");
    setEventFormat("SOLO");
    setMinTeamSize(1);
    setMaxTeamSize(1);
    setRegistrationFee(0);
    setMaxParticipants(100);
    setStartDate("");
    setEndDate("");
    setRegDeadline("");
    setPrimaryMediaUrl(null);
    setUploadedMediaId(null);
    setRules([]);
    setRounds([]);
    setFormError(null);
    setFormSuccess(null);
  };

  const handleSaveEvent = async (shouldPublish = true) => {
    if (!title.trim()) {
      setFormError("Event Title is required.");
      return;
    }
    try {
      setSaving(true);
      setFormError(null);

      const startTimeIso = safeIsoDate(startDate, 24);
      const endTimeIso = safeIsoDate(endDate, 30);
      const regDeadlineIso = safeIsoDate(regDeadline, 12);

      const payload = {
        title: title.trim(),
        description: fullDescription.trim() || shortDescription.trim() || title.trim(),
        category_id: categoryId ? Number(categoryId) : (categories[0]?.id || 1),
        venue_id: venueId ? Number(venueId) : null,
        start_time: startTimeIso,
        end_time: endTimeIso,
        registration_deadline: regDeadlineIso,
        max_participants: Number(maxParticipants) || 100,
        is_team_event: eventFormat === "TEAM" || eventFormat === "HYBRID",
        min_team_size: Number(minTeamSize) || 1,
        max_team_size: Number(maxTeamSize) || 1,
        registration_fee: Number(registrationFee) || 0,
        prize_pool: "₹25,000",
        status: shouldPublish ? "PUBLISHED" : "DRAFT",
        rules: rules.map((r, i) => ({
          title: r.title,
          description: r.description,
          rule_order: i + 1,
        })),
        rounds: rounds.map((r, i) => ({
          name: r.name,
          description: r.description,
          round_number: i + 1,
        })),
      };

      let saved;
      if (currentEventId) {
        saved = await eventApi.updateEvent(currentEventId, payload);
        if (shouldPublish) {
          try {
            await eventApi.publishEvent(currentEventId);
          } catch (_) {}
        }
        setFormSuccess(
          shouldPublish
            ? "Event saved and published! It is now live in the student dashboard."
            : "Event saved as draft."
        );
      } else {
        saved = await eventApi.createEvent(payload);
        if (shouldPublish) {
          try {
            await eventApi.publishEvent(saved.id);
          } catch (_) {}
        }
        setCurrentEventId(saved.id);
        setFormSuccess(
          shouldPublish
            ? "Event created and published! It is now live in the student dashboard."
            : "Draft event created! You can now upload cover visuals."
        );
        navigate(`/coordinator/events?edit=${saved.id}`, { replace: true });
      }
      fetchInitialData();
    } catch (err) {
      console.error("Failed to save event", err);
      setFormError(extractErrorMessage(err, "Failed to save event."));
    } finally {
      setSaving(false);
    }
  };

  const handleSaveDraft = () => handleSaveEvent(false);
  const handleSaveAndPublish = () => handleSaveEvent(true);

  const handlePublish = async (idToPublish) => {
    const targetId = idToPublish || currentEventId;
    if (!targetId) {
      setFormError("Please save the event before publishing.");
      return;
    }
    try {
      setSaving(true);
      setFormError(null);
      await eventApi.publishEvent(targetId);
      setFormSuccess("Event published successfully! It is now live in the fest discovery catalog.");
      fetchInitialData();
      if (isEditing) {
        loadEventForEdit(targetId);
      }
    } catch (err) {
      console.error("Failed to publish event", err);
      setFormError(extractErrorMessage(err, "Failed to publish event."));
    } finally {
      setSaving(false);
    }
  };

  const handleUnpublish = async (id) => {
    try {
      await eventApi.unpublishEvent(id);
      fetchInitialData();
    } catch (err) {
      console.error("Failed to unpublish event", err);
      alert("Failed to unpublish event.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this event? This action cannot be undone.")) return;
    try {
      await eventApi.deleteEvent(id);
      fetchInitialData();
      if (editId === String(id)) {
        navigate("/coordinator/events");
      }
    } catch (err) {
      console.error("Failed to delete event", err);
      alert("Failed to delete event.");
    }
  };

  const handleImageUploaded = (media) => {
    setPrimaryMediaUrl(media.media_url);
    setUploadedMediaId(media.id);
    setFormSuccess("Cover image uploaded and linked to event!");
    fetchInitialData();
  };

  const handleImageRemoved = async () => {
    if (uploadedMediaId && currentEventId) {
      try {
        await eventApi.deleteEventMedia(currentEventId, uploadedMediaId);
      } catch (err) {
        console.error("Failed to delete media", err);
      }
    }
    setPrimaryMediaUrl(null);
    setUploadedMediaId(null);
  };

  const addRule = () => {
    if (!newRuleTitle.trim()) return;
    setRules([...rules, { title: newRuleTitle.trim(), description: newRuleDesc.trim() }]);
    setNewRuleTitle("");
    setNewRuleDesc("");
  };

  const removeRule = (idx) => {
    setRules(rules.filter((_, i) => i !== idx));
  };

  const addRound = () => {
    if (!newRoundName.trim()) return;
    setRounds([...rounds, { name: newRoundName.trim(), description: newRoundDesc.trim() }]);
    setNewRoundName("");
    setNewRoundDesc("");
  };

  const removeRound = (idx) => {
    setRounds(rounds.filter((_, i) => i !== idx));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            {isEditing ? (currentEventId ? "Edit Festival Event" : "Create New Event") : "Coordinated Events"}
          </h1>
          <p className="text-slate-400 text-sm">
            {isEditing
              ? "Configure event specifics, upload custom 16:9 banner visuals, specify rules and rounds, and publish to the fest catalog."
              : "Review and manage competitive events assigned to your coordination desk."}
          </p>
        </div>

        {isEditing ? (
          <button
            onClick={() => navigate("/coordinator/events")}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-all flex items-center gap-1.5 self-start sm:self-center border border-slate-700"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Events List
          </button>
        ) : (
          <button
            onClick={() => navigate("/coordinator/events?action=new")}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all flex items-center gap-2 self-start sm:self-center shadow-lg shadow-blue-600/20"
          >
            <PlusCircle className="w-4 h-4" /> Create New Event
          </button>
        )}
      </div>

      {/* Alerts */}
      {formSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center justify-between">
          <span>{formSuccess}</span>
          <button onClick={() => setFormSuccess(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}
      {formError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center justify-between">
          <span>{formError}</span>
          <button onClick={() => setFormError(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Main View: Edit/Create Mode OR Events Table */}
      {isEditing ? (
        <div className="space-y-8">
          {/* Section 1: Event Details */}
          <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <FileText className="w-5 h-5 text-blue-400" />
              1. Event Details & Overview
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Event Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. RoboWars Championship 2026"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Short Tagline / Catchphrase (1-2 sentences) *
                </label>
                <input
                  type="text"
                  placeholder="e.g. The premier battleground for autonomous robotic gladiators."
                  value={shortDescription}
                  onChange={(e) => setShortDescription(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Full Detailed Description & Problem Statement
                </label>
                <textarea
                  rows={4}
                  placeholder="Comprehensive event details, guidelines, stage setups, scoring overview..."
                  value={fullDescription}
                  onChange={(e) => setFullDescription(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Fest Category *
                  </label>
                  <select
                    value={categoryId}
                    onChange={(e) => setCategoryId(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Event Type *
                  </label>
                  <select
                    value={eventType}
                    onChange={(e) => setEventType(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="TECHNICAL">TECHNICAL</option>
                    <option value="CULTURAL">CULTURAL</option>
                    <option value="SPORTS">SPORTS</option>
                    <option value="MANAGEMENT">MANAGEMENT</option>
                    <option value="GAMING">GAMING</option>
                    <option value="WORKSHOP">WORKSHOP</option>
                    <option value="OTHER">OTHER</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Format (Solo / Team) *
                  </label>
                  <select
                    value={eventFormat}
                    onChange={(e) => setEventFormat(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="SOLO">Solo (Individual)</option>
                    <option value="TEAM">Team Squad</option>
                    <option value="HYBRID">Hybrid</option>
                  </select>
                </div>
              </div>

              {eventFormat !== "SOLO" && (
                <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-950 border border-slate-800">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Min Team Members
                    </label>
                    <input
                      type="number"
                      min={1}
                      value={minTeamSize}
                      onChange={(e) => setMinTeamSize(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Max Team Members
                    </label>
                    <input
                      type="number"
                      min={1}
                      value={maxTeamSize}
                      onChange={(e) => setMaxTeamSize(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Section 2: Visual / Media Management */}
          <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <ImageIcon className="w-5 h-5 text-indigo-400" />
              2. Event Visual / Media Cover (Mandatory Visual Management)
            </h2>

            {currentEventId ? (
              <ImageUploadSection
                eventId={currentEventId}
                initialMediaUrl={primaryMediaUrl}
                onMediaUploaded={handleImageUploaded}
                onMediaRemoved={handleImageRemoved}
              />
            ) : (
              <div className="p-6 rounded-2xl bg-slate-950 border border-dashed border-slate-800 text-center space-y-3">
                <Upload className="w-10 h-10 text-slate-600 mx-auto" />
                <h4 className="text-sm font-bold text-slate-300">
                  Save Draft First to Enable Image Uploading
                </h4>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Click "Save as Draft" below to allocate the official event record. You can then immediately upload your 16:9 custom cover image here.
                </p>
                <button
                  type="button"
                  onClick={handleSaveDraft}
                  disabled={saving || !title.trim()}
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold transition-all shadow-md shadow-blue-600/30"
                >
                  {saving ? "Saving Draft..." : "Save Draft Now"}
                </button>
              </div>
            )}
          </div>

          {/* Section 3: Schedule & Venue */}
          <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Calendar className="w-5 h-5 text-emerald-400" />
              3. Schedule & Venue Allotment
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Start Date & Time
                </label>
                <input
                  type="datetime-local"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  End Date & Time
                </label>
                <input
                  type="datetime-local"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Registration Deadline
                </label>
                <input
                  type="datetime-local"
                  value={regDeadline}
                  onChange={(e) => setRegDeadline(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-semibold text-slate-300">
                    Allotted Venue
                  </label>
                  <div className="flex items-center gap-2">
                    {venueId && (
                      <button
                        type="button"
                        onClick={handleOpenEditVenue}
                        className="text-[11px] text-blue-400 hover:text-blue-300 font-semibold hover:underline flex items-center gap-0.5"
                      >
                        <Edit className="w-3 h-3" /> Edit
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={handleOpenAddVenue}
                      className="text-[11px] text-emerald-400 hover:text-emerald-300 font-semibold hover:underline flex items-center gap-0.5"
                    >
                      <PlusCircle className="w-3 h-3" /> + New Venue
                    </button>
                  </div>
                </div>
                <select
                  value={venueId}
                  onChange={(e) => setVenueId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">No Venue / Virtual</option>
                  {venues.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name} ({v.building || "Campus"}) — Cap: {v.capacity || 100}
                    </option>
                  ))}
                </select>
                {venueId && venues.find((v) => Number(v.id) === Number(venueId)) && (
                  <div className="mt-1 text-[11px] text-slate-400 truncate">
                    {(() => {
                      const v = venues.find((v) => Number(v.id) === Number(venueId));
                      return `${v.building || ""}${v.floor ? " • " + v.floor : ""}${v.room_number ? " • Room " + v.room_number : ""} (Capacity: ${v.capacity || 100})`;
                    })()}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Section 4: Registration & Pricing */}
          <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <DollarSign className="w-5 h-5 text-amber-400" />
              4. Registration & Ticket Pricing
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Registration Fee (INR ₹) — Set 0 for Free
                </label>
                <input
                  type="number"
                  min={0}
                  step="1"
                  value={registrationFee}
                  onChange={(e) => setRegistrationFee(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  {registrationFee > 0 ? `Participants will be invoiced ₹${registrationFee} via checkout gateway.` : "Free Event - Instant QR Pass generation upon registration."}
                </span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Maximum Capacity / Cap
                </label>
                <input
                  type="number"
                  min={1}
                  value={maxParticipants}
                  onChange={(e) => setMaxParticipants(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Section 5: Rules & Rounds */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Rules */}
            <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-indigo-400" /> Event Rules & Code of Conduct
              </h3>

              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Rule Title (e.g. Robot Weight Limit)"
                  value={newRuleTitle}
                  onChange={(e) => setNewRuleTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500"
                />
                <textarea
                  rows={2}
                  placeholder="Detailed rule specifics..."
                  value={newRuleDesc}
                  onChange={(e) => setNewRuleDesc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500"
                />
                <button
                  type="button"
                  onClick={addRule}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors flex items-center gap-1"
                >
                  <PlusCircle className="w-3.5 h-3.5" /> Add Rule
                </button>
              </div>

              <div className="space-y-2 pt-2 border-t border-slate-800">
                {rules.map((rule, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start justify-between gap-3 text-xs"
                  >
                    <div>
                      <strong className="text-white block">{rule.title}</strong>
                      <p className="text-slate-400 text-[11px] mt-0.5">{rule.description}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeRule(idx)}
                      className="text-slate-500 hover:text-rose-400"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Rounds */}
            <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-400" /> Competitive Rounds & Stages
              </h3>

              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Round Name (e.g. Preliminary Screening)"
                  value={newRoundName}
                  onChange={(e) => setNewRoundName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500"
                />
                <textarea
                  rows={2}
                  placeholder="Round rules, qualification criteria..."
                  value={newRoundDesc}
                  onChange={(e) => setNewRoundDesc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500"
                />
                <button
                  type="button"
                  onClick={addRound}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors flex items-center gap-1"
                >
                  <PlusCircle className="w-3.5 h-3.5" /> Add Round
                </button>
              </div>

              <div className="space-y-2 pt-2 border-t border-slate-800">
                {rounds.map((round, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start justify-between gap-3 text-xs"
                  >
                    <div>
                      <strong className="text-white block">Round {idx + 1}: {round.name}</strong>
                      <p className="text-slate-400 text-[11px] mt-0.5">{round.description}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeRound(idx)}
                      className="text-slate-500 hover:text-rose-400"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Action Bar */}
          <div className="sticky bottom-6 z-20 p-4 rounded-2xl bg-slate-900/90 backdrop-blur-md border border-slate-800 flex flex-wrap items-center justify-between gap-4 shadow-2xl">
            <div className="text-xs text-slate-400">
              {currentEventId ? `Editing Event #${currentEventId}` : "New Unsaved Draft"}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => setShowPreviewModal(true)}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 border border-slate-700 transition-colors"
              >
                <Eye className="w-4 h-4 text-indigo-400" />
                Preview Card & Hero
              </button>

              <button
                type="button"
                onClick={handleSaveDraft}
                disabled={saving}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-300 text-xs font-semibold transition-colors"
              >
                {saving ? "Saving..." : "Save as Draft"}
              </button>

              <button
                type="button"
                onClick={handleSaveAndPublish}
                disabled={saving}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
              >
                <Globe className="w-4 h-4" />
                {saving ? "Saving..." : "Save & Make Live"}
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Event Table View */
        <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
          {loading ? (
            <div className="p-6 space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 bg-slate-950 rounded-2xl animate-pulse" />
              ))}
            </div>
          ) : events.length === 0 ? (
            <EmptyState
              icon={Calendar}
              title="No Coordinated Events Found"
              description="You have not created any events yet. Click below to launch your first festival competition."
              actionText="Create New Event"
              actionHref="/coordinator/events?action=new"
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="px-6 py-4">Event & Visual</th>
                    <th className="px-6 py-4">Category & Format</th>
                    <th className="px-6 py-4">Schedule</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Registrations</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {events.map((evt) => (
                    <tr key={evt.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          {evt.primary_media_url ? (
                            <img
                              src={evt.primary_media_url}
                              alt={evt.title}
                              className="w-12 h-12 rounded-xl object-cover border border-slate-800 shrink-0"
                            />
                          ) : (
                            <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-slate-500 shrink-0">
                              <Calendar className="w-5 h-5" />
                            </div>
                          )}
                          <div>
                            <div className="font-bold text-white text-sm">{evt.title}</div>
                            <div className="text-[11px] text-slate-400 line-clamp-1">{evt.short_description}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="font-semibold text-slate-200">{evt.category?.name || "General"}</span>
                        <div className="text-[11px] text-slate-500">{evt.event_format}</div>
                      </td>
                      <td className="px-6 py-4 text-slate-400">
                        {evt.start_date ? new Date(evt.start_date).toLocaleDateString() : "TBA"}
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={evt.status} />
                      </td>
                      <td className="px-6 py-4 font-mono font-bold text-white">
                        {evt.registrations?.length || 0} / {evt.max_participants || "∞"}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => navigate(`/coordinator/events?edit=${evt.id}`)}
                            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                            title="Edit Event & Visuals"
                          >
                            <Edit className="w-3.5 h-3.5" />
                          </button>

                          {evt.status === "PUBLISHED" ? (
                            <button
                              onClick={() => handleUnpublish(evt.id)}
                              className="p-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 transition-colors"
                              title="Unpublish (Convert to Draft)"
                            >
                              <XCircle className="w-3.5 h-3.5" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handlePublish(evt.id)}
                              className="p-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors"
                              title="Publish Event"
                            >
                              <Globe className="w-3.5 h-3.5" />
                            </button>
                          )}

                          <button
                            onClick={() => handleDelete(evt.id)}
                            className="p-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-colors"
                            title="Delete Event"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Pre-Publish Card & Hero Preview Modal */}
      {showPreviewModal && (
        <EventPreviewModal
          event={{
            title: title || "Untitled Event",
            short_description: shortDescription || "No short description provided.",
            full_description: fullDescription || "No details provided.",
            category: categories.find((c) => String(c.id) === String(categoryId)) || { name: "General" },
            venue: venues.find((v) => String(v.id) === String(venueId)) || { name: "Campus Hub" },
            start_date: startDate,
            end_date: endDate,
            registration_fee: registrationFee,
            event_format: eventFormat,
            primary_media_url: primaryMediaUrl,
          }}
          onClose={() => setShowPreviewModal(false)}
        />
      )}

      {/* Venue Modal (Create & Edit) */}
      {showVenueModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-6 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                  <MapPin className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">
                    {venueModalMode === "create" ? "Add Festival Venue" : "Edit Venue Specifications"}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {venueModalMode === "create" ? "Register a new campus ground, hall, or arena" : "Update venue details, capacity, and coordinates"}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowVenueModal(false)}
                className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center text-sm transition-all"
              >
                ✕
              </button>
            </div>

            {venueError && (
              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold">
                {venueError}
              </div>
            )}

            <form onSubmit={handleSaveVenue} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Venue Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Campus Esports Arena or Hall 101"
                  value={venueName}
                  onChange={(e) => setVenueName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Building / Complex *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Tech Park Block 2"
                    value={venueBuilding}
                    onChange={(e) => setVenueBuilding(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Floor
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 2nd Floor or Ground"
                    value={venueFloor}
                    onChange={(e) => setVenueFloor(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Room / Lab Number
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Lab 204 or Arena A"
                    value={venueRoom}
                    onChange={(e) => setVenueRoom(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Capacity
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={venueCapacity}
                    onChange={(e) => setVenueCapacity(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Campus Map Link / Coordinates (Optional)
                </label>
                <input
                  type="text"
                  placeholder="https://maps.google.com/?q=..."
                  value={venueMapLink}
                  onChange={(e) => setVenueMapLink(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowVenueModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={venueSaving}
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold transition-all shadow-md shadow-blue-600/30 flex items-center gap-1.5"
                >
                  {venueSaving ? "Saving..." : (venueModalMode === "create" ? "Add Venue" : "Update Venue")}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
