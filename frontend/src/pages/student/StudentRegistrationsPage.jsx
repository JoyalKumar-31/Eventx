import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Calendar,
  CreditCard,
  QrCode,
  Users,
  Search,
  CheckCircle,
  Clock,
  ExternalLink,
  Lock,
} from "lucide-react";
import { registrationApi } from "../../api/registrationApi";
import StatusBadge from "../../components/StatusBadge";
import EmptyState from "../../components/EmptyState";
import QRPassModal from "../../components/QRPassModal";
import PaymentModal from "../../components/PaymentModal";

export default function StudentRegistrationsPage() {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("ALL");

  // Modals state
  const [passRegId, setPassRegId] = useState(null);
  const [paymentReg, setPaymentReg] = useState(null);

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const fetchRegistrations = async () => {
    try {
      setLoading(true);
      const data = await registrationApi.getMyRegistrations();
      setRegistrations(data || []);
    } catch (err) {
      console.error("Failed to load registrations", err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = registrations.filter((r) => {
    const eventTitle = r.event_title || r.event?.title || "";
    const teamName = r.team_name || r.team?.name || "";
    const matchesSearch =
      eventTitle.toLowerCase().includes(search.toLowerCase()) ||
      teamName.toLowerCase().includes(search.toLowerCase());
    const statusVal = r.status || "";
    const matchesStatus =
      filterStatus === "ALL" ||
      statusVal === filterStatus ||
      (filterStatus === "PENDING" && (statusVal === "PENDING" || statusVal === "PENDING_PAYMENT"));
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            My Registrations
          </h1>
          <p className="text-slate-400 text-sm">
            Track your competitive entries, manage payments, and generate digital gate passes.
          </p>
        </div>
        <Link
          to="/events"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all self-start sm:self-center shadow-lg shadow-indigo-600/20"
        >
          <Calendar className="w-4 h-4" /> Register More Events
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by event or team..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          {["ALL", "CONFIRMED", "PENDING", "CANCELLED"].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                filterStatus === status
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Registrations List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 rounded-2xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No Registrations Found"
          description="You haven't registered for any events matching your current filter."
          actionText="Browse Events"
          actionHref="/events"
        />
      ) : (
        <div className="space-y-4">
          {filtered.map((reg) => {
            const fee = Number(reg.registration_fee ?? reg.event?.registration_fee ?? 0);
            const isPaid = fee === 0 || reg.payment_status === "PAID" || reg.payment_status === "SUCCESS";
            const eventTitle = reg.event_title || reg.event?.title || `Event #${reg.event_id}`;
            const teamName = reg.team_name || reg.team?.name;

            return (
              <div
                key={reg.id}
                className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-6"
              >
                {/* Event info */}
                <div className="space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusBadge status={isPaid ? reg.status : "PENDING_PAYMENT"} />
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold uppercase tracking-wider ${
                        isPaid
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      }`}
                    >
                      {isPaid ? "Payment: Cleared" : "Payment: Pending"}
                    </span>
                    <span className="text-xs text-slate-500">
                      Reg ID: #{reg.id}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-white hover:text-indigo-400 transition-colors">
                    <Link to={`/events/${reg.event_id}`}>
                      {eventTitle}
                    </Link>
                  </h3>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
                    {(reg.event?.category?.name || reg.category_name) && (
                      <span>Category: <strong className="text-slate-200">{reg.event?.category?.name || reg.category_name}</strong></span>
                    )}
                    <span>Format: <strong className="text-slate-200">{teamName ? "TEAM" : (reg.event?.event_format || "SOLO")}</strong></span>
                    {teamName && (
                      <span className="flex items-center gap-1 text-indigo-300">
                        <Users className="w-3.5 h-3.5" /> Team: {teamName}
                      </span>
                    )}
                    {fee > 0 && (
                      <span>Fee: <strong className="text-white">₹{fee}</strong></span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap items-center gap-3 self-end md:self-center shrink-0">
                  {!isPaid && (
                    <button
                      onClick={() => setPaymentReg(reg)}
                      className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-all flex items-center gap-1.5 shadow-lg shadow-amber-500/20"
                    >
                      <CreditCard className="w-4 h-4" /> Pay ₹{fee}
                    </button>
                  )}

                  {isPaid ? (
                    <button
                      onClick={() => setPassRegId(reg.id)}
                      className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all flex items-center gap-1.5 shadow-lg shadow-indigo-600/20"
                    >
                      <QrCode className="w-4 h-4" /> View Entry Pass
                    </button>
                  ) : (
                    <div
                      className="px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 font-medium text-xs flex items-center gap-1.5 opacity-90 cursor-not-allowed select-none"
                      title="Entry pass and QR code will unlock once payment is cleared"
                    >
                      <Lock className="w-3.5 h-3.5 text-amber-400" />
                      <span>Pass Locked (Pay to View)</span>
                    </div>
                  )}

                  <Link
                    to={`/events/${reg.event_id}`}
                    className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all text-xs"
                    title="View Event Details"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* QR Pass Modal */}
      {passRegId && (
        <QRPassModal
          registrationId={passRegId}
          onClose={() => setPassRegId(null)}
        />
      )}

      {/* Payment Checkout Modal */}
      {paymentReg && (
        <PaymentModal
          registration={paymentReg}
          onClose={() => setPaymentReg(null)}
          onSuccess={() => {
            setPaymentReg(null);
            fetchRegistrations();
          }}
        />
      )}
    </div>
  );
}
