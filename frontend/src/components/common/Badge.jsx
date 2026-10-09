import React from 'react';

export function Badge({ status = 'created', className = '' }) {
  const normalized = (status || '').toLowerCase().replace(/[\s_-]+/g, '');

  const config = {
    uploaded: {
      label: 'Uploaded',
      bg: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    },
    analysed: {
      label: 'Analyzed',
      bg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
    },
    analyzing: {
      label: 'Analyzing',
      bg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 animate-pulse',
    },
    edited: {
      label: 'Edited',
      bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    },
    editing: {
      label: 'Editing',
      bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse',
    },
    approved: {
      label: 'Approved',
      bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    },
    modelready: {
      label: '3D Ready',
      bg: 'bg-brand-500/15 text-brand-300 border-brand-500/40 shadow-glow/30',
    },
    '3dready': {
      label: '3D Ready',
      bg: 'bg-brand-500/15 text-brand-300 border-brand-500/40 shadow-glow/30',
    },
    '3dprocessing': {
      label: '3D Generating',
      bg: 'bg-purple-500/10 text-purple-400 border-purple-500/30 animate-pulse',
    },
    created: {
      label: 'Created',
      bg: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
    },
  };

  const current = config[normalized] || {
    label: status || 'Pending',
    bg: 'bg-slate-800 text-slate-300 border-slate-700',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${current.bg} ${className}`}
    >
      {current.label}
    </span>
  );
}

export default Badge;
