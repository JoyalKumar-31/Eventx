import React from "react";

export const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = "indigo" }) => {
  const colorMap = {
    indigo: "from-indigo-500/20 to-indigo-600/5 text-indigo-400 border-indigo-500/20",
    emerald: "from-emerald-500/20 to-emerald-600/5 text-emerald-400 border-emerald-500/20",
    amber: "from-amber-500/20 to-amber-600/5 text-amber-400 border-amber-500/20",
    purple: "from-purple-500/20 to-purple-600/5 text-purple-400 border-purple-500/20",
    sky: "from-amber-500/20 to-amber-600/5 text-amber-300 border-amber-500/20",
    rose: "from-rose-500/20 to-rose-600/5 text-rose-400 border-rose-500/20",
  };

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border bg-gradient-to-br ${
        colorMap[color] || colorMap.indigo
      } bg-slate-900/60 p-6 backdrop-blur-xl transition-all duration-300 hover:border-slate-700/60 hover:-translate-y-0.5 shadow-lg shadow-black/20`}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-400">{title}</p>
        {Icon && (
          <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/40 text-slate-200">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-3xl font-bold tracking-tight text-white">{value}</h3>
        {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
      </div>
      {trend && (
        <div className="mt-3 flex items-center text-xs font-medium text-emerald-400">
          <span>{trend}</span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
