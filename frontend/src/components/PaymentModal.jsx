import React, { useState } from "react";
import { X, CreditCard, CheckCircle2, ShieldCheck, ArrowRight, FileText } from "lucide-react";
import { paymentApi } from "../api/paymentApi";

export const PaymentModal = ({ isOpen = true, onClose, registration, onPaymentSuccess, onSuccess }) => {
  const [method, setMethod] = useState("UPI");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successData, setSuccessData] = useState(null);

  const handleSuccess = onPaymentSuccess || onSuccess;

  if (isOpen === false || !registration) return null;

  const baseAmount = registration.event?.registration_fee || registration.amount || 150.0;
  const tax = baseAmount * 0.18;
  const total = baseAmount + tax;

  const handleCheckout = async () => {
    setLoading(true);
    setError(null);

    try {
      // 1. Create payment order in database
      const order = await paymentApi.createOrder(registration.id);

      // 2. Complete payment verification via backend service
      const txnId = `TXN_${Date.now()}_${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
      const verified = await paymentApi.verifyPayment({
        payment_id: order.id,
        transaction_id: txnId,
        payment_method: method,
        simulate_status: "SUCCESS",
      });

      setSuccessData(verified);
      if (handleSuccess) handleSuccess(verified);
    } catch (err) {
      setError(err.response?.data?.message || "Payment processing failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-md rounded-3xl border border-slate-700 bg-slate-900 p-6 md:p-8 shadow-2xl my-8">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2 text-indigo-400">
            <CreditCard className="w-5 h-5" />
            <h3 className="text-lg font-bold text-white">Event Registration Fee</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {successData ? (
          <div className="mt-6 text-center">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="mt-4 text-xl font-bold text-white">Payment Confirmed!</h3>
            <p className="mt-1 text-xs text-slate-400">
              Your registration is confirmed. Digital pass is ready for check-in.
            </p>

            {successData.invoice && (
              <div className="mt-4 p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-left text-xs space-y-1.5">
                <div className="flex justify-between text-slate-400">
                  <span>Invoice Number:</span>
                  <span className="font-semibold text-white">{successData.invoice.invoice_number}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Total Amount Paid:</span>
                  <span className="font-semibold text-emerald-400">₹{successData.invoice.total_amount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Payment Method:</span>
                  <span className="text-slate-200">{method}</span>
                </div>
              </div>
            )}

            <button
              onClick={onClose}
              className="mt-6 w-full py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/20"
            >
              Done
            </button>
          </div>
        ) : (
          <div className="mt-6 space-y-6">
            <div>
              <span className="text-xs uppercase tracking-wider text-slate-400">Registration For</span>
              <h4 className="text-base font-bold text-white mt-0.5">
                {registration.event_title || registration.event?.title}
              </h4>
              <p className="text-xs text-slate-400">
                Ticket ID: {registration.registration_number}
              </p>
            </div>

            {/* Fee Breakdown */}
            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Base Entry Fee</span>
                <span className="text-slate-200">₹{baseAmount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Campus Tech & Taxes (18%)</span>
                <span className="text-slate-200">₹{tax.toFixed(2)}</span>
              </div>
              <div className="pt-2 border-t border-slate-800 flex justify-between font-bold text-sm text-white">
                <span>Total Payable</span>
                <span className="text-emerald-400">₹{total.toFixed(2)}</span>
              </div>
            </div>

            {/* Payment Method Selector */}
            <div>
              <label className="text-xs font-semibold text-slate-300">Select Payment Option</label>
              <div className="mt-2 grid grid-cols-3 gap-2">
                {["UPI", "CARD", "NETBANKING"].map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => setMethod(opt)}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all text-center ${
                      method === opt
                        ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-sm"
                        : "bg-slate-950/50 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            {error && (
              <p className="text-xs text-rose-400 bg-rose-500/10 p-3 rounded-xl border border-rose-500/20">
                {error}
              </p>
            )}

            <button
              onClick={handleCheckout}
              disabled={loading}
              className="w-full py-3 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white transition-all shadow-md shadow-emerald-600/20 cursor-pointer flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Processing Secure Checkout...</span>
                </>
              ) : (
                <>
                  <span>Pay ₹{total.toFixed(2)}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PaymentModal;
