import React from 'react';
import { Search, Filter } from 'lucide-react';

export function HistoryFilters({
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusChange,
}) {
  const statusOptions = [
    { value: 'all', label: 'All Statuses' },
    { value: 'model_ready', label: '3D Ready' },
    { value: 'edited', label: 'AI Edited' },
    { value: 'analysed', label: 'Analyzed' },
    { value: 'created', label: 'Created' },
  ];

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 w-full">
      {/* Search Input */}
      <div className="relative w-full sm:w-72">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search by title or prompt..."
          className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-3.5 py-2 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all"
        />
      </div>

      {/* Status Filter Dropdown */}
      <div className="flex items-center gap-2 w-full sm:w-auto">
        <Filter className="w-4 h-4 text-slate-500 flex-shrink-0" />
        <select
          value={statusFilter}
          onChange={(e) => onStatusChange(e.target.value)}
          className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all cursor-pointer w-full sm:w-auto"
        >
          {statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

export default HistoryFilters;
