import React from 'react';

export function StatsCard({ title, value, icon, change, subtitle }) {
  return (
    <div className="glass-panel glass-panel-hover p-5 rounded-2xl flex items-center justify-between">
      <div className="flex flex-col">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <span className="text-2xl font-bold text-white mt-1 tracking-tight">{value}</span>
        {subtitle && <span className="text-[11px] text-slate-500 mt-0.5">{subtitle}</span>}
      </div>

      <div className="w-12 h-12 rounded-2xl bg-brand-600/15 border border-brand-500/20 flex items-center justify-center text-brand-400">
        {icon}
      </div>
    </div>
  );
}

export default StatsCard;
