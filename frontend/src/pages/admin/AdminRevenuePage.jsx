import React, { useState, useEffect } from "react";
import {
  DollarSign,
  TrendingUp,
  FileText,
  Search,
  CheckCircle2,
  Calendar,
  CreditCard,
  Printer,
  ShieldCheck,
} from "lucide-react";
import { paymentApi } from "../../api/paymentApi";
import StatusBadge from "../../components/StatusBadge";
import EmptyState from "../../components/EmptyState";
import StatCard from "../../components/StatCard";

export default function AdminRevenuePage() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const data = await paymentApi.getAllPayments();
      setPayments(data || []);
    } catch (err) {
      console.error("Failed to load revenue", err);
    } finally {
      setLoading(false);
    }
  };

  const totalGross = payments
    .filter((p) => p.status === "COMPLETED")
    .reduce((sum, p) => sum + Number(p.amount || 0), 0);

  const totalTaxes = payments
    .filter((p) => p.status === "COMPLETED")
    .reduce((sum, p) => {
      const inv = p.invoices?.[0];
      return sum + Number(inv?.tax_amount || 0);
    }, 0);

  const filtered = payments.filter(
    (p) =>
      p.order_id?.toLowerCase().includes(search.toLowerCase()) ||
      p.transaction_id?.toLowerCase().includes(search.toLowerCase()) ||
      p.registration?.user?.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      p.registration?.event?.title?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Fiscal Operations & Revenue Reconciliation
        </h1>
        <p className="text-slate-400 text-sm">
          Festival transaction ledgers, payment gateway reconciliation, and itemized invoice auditing.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          title="Total Gross Revenue"
          value={`₹${totalGross.toLocaleString()}`}
          subtitle="Cleared participant transactions"
          icon={DollarSign}
          color="emerald"
        />
        <StatCard
          title="Taxes Collected (GST)"
          value={`₹${totalTaxes.toLocaleString()}`}
          subtitle="Auto-calculated invoice tax"
          icon={TrendingUp}
          color="blue"
        />
        <StatCard
          title="Total Transactions"
          value={payments.length}
          subtitle={`${payments.filter((p) => p.status === "COMPLETED").length} Successful`}
          icon={CreditCard}
          color="purple"
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by participant, order, or event..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
          />
        </div>
        <span className="text-xs text-slate-400 hidden sm:inline">
          {filtered.length} transactions found
        </span>
      </div>

      {/* Ledger Table */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-slate-900 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={DollarSign}
          title="No Transactions Found"
          description="There are currently no transactions matching your search."
        />
      ) : (
        <div className="rounded-3xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Transaction / Order</th>
                  <th className="px-6 py-4">Participant</th>
                  <th className="px-6 py-4">Event</th>
                  <th className="px-6 py-4">Amount</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4 text-right">Invoice</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-mono">
                      <div className="text-white font-bold">{item.transaction_id || item.order_id}</div>
                      <div className="text-[10px] text-slate-500">Method: {item.payment_method || "GATEWAY"}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-white font-bold">
                        {item.registration?.user?.full_name || "Student"}
                      </div>
                      <div className="text-[10px] text-slate-500">{item.registration?.user?.email}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-white font-medium">
                        {item.registration?.event?.title || `Event #${item.registration?.event_id}`}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono font-bold text-white text-sm">
                      ₹{item.amount}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {item.invoices && item.invoices.length > 0 ? (
                        <button
                          onClick={() => setSelectedInvoice(item.invoices[0])}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 font-medium transition-colors"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          View Receipt
                        </button>
                      ) : (
                        <span className="text-slate-600 italic">No receipt</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Invoice Modal */}
      {selectedInvoice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> Verified Tax Invoice
                </span>
                <h3 className="text-xl font-black text-white font-mono mt-0.5">
                  {selectedInvoice.invoice_number}
                </h3>
              </div>
              <button
                onClick={() => setSelectedInvoice(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="rounded-xl bg-slate-950 p-4 border border-slate-800 space-y-3 text-xs">
              <div className="flex justify-between text-slate-400 font-semibold border-b border-slate-800 pb-2">
                <span>Description</span>
                <span>Amount</span>
              </div>
              <div className="flex justify-between text-white">
                <span>Registration Entry Ticket</span>
                <span className="font-mono font-bold">₹{selectedInvoice.subtotal}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Tax (GST)</span>
                <span className="font-mono">₹{selectedInvoice.tax_amount}</span>
              </div>
              <div className="flex justify-between text-base font-extrabold text-white border-t border-slate-800 pt-2">
                <span>Total Amount Paid</span>
                <span className="font-mono text-emerald-400">₹{selectedInvoice.total_amount}</span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => window.print()}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                <Printer className="w-3.5 h-3.5" /> Print Invoice
              </button>
              <button
                onClick={() => setSelectedInvoice(null)}
                className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
