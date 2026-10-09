import React, { useState } from 'react';
import { Tag, Check, Search, Sparkles, Loader2 } from 'lucide-react';

export function DetectedObjects({
  objects = [],
  detections = [],
  selectedObject,
  selectedDetection,
  onSelectObject,
  onSelectDetection,
  onReScan,
  isAnalyzing = false,
}) {
  const [customTerm, setCustomTerm] = useState('');
  const hasDetections = detections && detections.length > 0;
  const itemsCount = hasDetections ? detections.length : objects.length;

  const handleCustomScan = (termToScan) => {
    const query = (termToScan || customTerm).trim();
    if (!query || isAnalyzing) return;
    onReScan?.(query);
  };

  const quickPills = ['door', 'table', 'cabinet', 'lamp', 'wall', 'window'];

  return (
    <div className="flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <Tag className="w-3.5 h-3.5 text-cyan-400" />
          Detected Elements ({itemsCount})
        </span>
        <span className="text-[11px] text-slate-500">
          {hasDetections ? 'Click to highlight mask' : 'Click to target'}
        </span>
      </div>

      {/* Detected Elements Chips */}
      {itemsCount > 0 ? (
        <div className="flex flex-wrap gap-2">
          {hasDetections
            ? detections.map((det, idx) => {
                const isSelected =
                  selectedDetection?.object_id === det.object_id ||
                  selectedObject?.toLowerCase() === det.label.toLowerCase();

                const confPct = Math.round(det.confidence * 100);

                return (
                  <button
                    key={det.object_id || idx}
                    type="button"
                    onClick={() => {
                      if (isSelected) {
                        onSelectDetection?.(null);
                        onSelectObject?.(null);
                      } else {
                        onSelectDetection?.(det);
                        onSelectObject?.(det.label);
                      }
                    }}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer ${
                      isSelected
                        ? 'bg-brand-600 text-white shadow-glow/60 border border-brand-400 scale-[1.03]'
                        : 'bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 hover:text-white'
                    }`}
                  >
                    {isSelected && <Check className="w-3 h-3 text-white" />}
                    <span className="capitalize">{det.label}</span>
                    <span
                      className={`text-[10px] px-1 py-0.2 rounded font-mono ${
                        isSelected ? 'bg-brand-800/70 text-cyan-200' : 'bg-slate-900/80 text-slate-400'
                      }`}
                    >
                      {confPct}%
                    </span>
                    {det.mask_url && (
                      <span
                        title="SAM mask generated"
                        className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"
                      />
                    )}
                  </button>
                );
              })
            : objects.map((obj) => {
                const isSelected = selectedObject?.toLowerCase() === obj.toLowerCase();

                return (
                  <button
                    key={obj}
                    type="button"
                    onClick={() => onSelectObject(isSelected ? null : obj)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer ${
                      isSelected
                        ? 'bg-brand-600 text-white shadow-glow/60 border border-brand-400 scale-[1.03]'
                        : 'bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 hover:text-white'
                    }`}
                  >
                    {isSelected && <Check className="w-3 h-3 text-white" />}
                    <span>{obj}</span>
                  </button>
                );
              })}
        </div>
      ) : (
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
          <p className="text-xs text-slate-400">
            No elements detected with this prompt. Try one of the quick tags below.
          </p>
        </div>
      )}

      {/* Dynamic Element Detection Bar */}
      {onReScan && (
        <div className="pt-2 border-t border-slate-800/80 flex flex-col gap-2">
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-brand-400" />
              Detect specific element:
            </span>
            <span className="text-[10px] text-slate-500">DINO + SAM on demand</span>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleCustomScan();
            }}
            className="flex gap-1.5"
          >
            <div className="relative flex-1">
              <input
                type="text"
                value={customTerm}
                onChange={(e) => setCustomTerm(e.target.value)}
                placeholder="e.g. door, table, cabinet..."
                className="w-full pl-7 pr-2 py-1.5 bg-slate-900/90 border border-slate-700/70 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2 top-2" />
            </div>
            <button
              type="submit"
              disabled={!customTerm.trim() || isAnalyzing}
              className="px-2.5 py-1.5 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white rounded-lg text-xs font-medium flex items-center gap-1 transition-all"
            >
              {isAnalyzing ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <span>Detect</span>
              )}
            </button>
          </form>

          {/* Quick pills */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[10px] text-slate-500">Quick detect:</span>
            {quickPills.map((pill) => (
              <button
                key={pill}
                type="button"
                disabled={isAnalyzing}
                onClick={() => handleCustomScan(pill)}
                className="px-2 py-0.5 rounded-md bg-slate-800/60 hover:bg-slate-700/80 text-[11px] text-slate-300 hover:text-white border border-slate-700/50 transition-colors"
              >
                + {pill}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default DetectedObjects;
