import React from "react";

export const StatusBadge = ({ status }) => {
  if (!status) return null;

  const getStyle = () => {
    switch (status.toUpperCase()) {
      case "PUBLISHED":
      case "CONFIRMED":
      case "SUCCESS":
      case "VALID":
      case "ACTIVE":
      case "COMPLETE":
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      case "PENDING":
      case "PENDING_PAYMENT":
      case "FORMING":
      case "SCHEDULED":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "DRAFT":
        return "bg-slate-500/15 text-slate-300 border-slate-500/30";
      case "CANCELLED":
      case "FAILED":
      case "DUPLICATE_ATTEMPT":
      case "REJECTED":
        return "bg-rose-500/15 text-rose-400 border-rose-500/30";
      case "ONGOING":
      case "ATTENDED":
        return "bg-indigo-500/15 text-indigo-400 border-indigo-500/30";
      case "COMPLETED":
        return "bg-amber-500/15 text-amber-300 border-amber-500/30";
      default:
        return "bg-slate-700/30 text-slate-300 border-slate-600/30";
    }
  };

  const formatText = (str) => {
    return str.replace(/_/g, " ");
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStyle()}`}
    >
      {formatText(status)}
    </span>
  );
};

export default StatusBadge;
