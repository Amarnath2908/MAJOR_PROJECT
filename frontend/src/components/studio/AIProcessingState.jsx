import React from 'react';
import { Loader2, Sparkles, Box, ShieldAlert } from 'lucide-react';
import Button from '../common/Button';

export function AIProcessingState({
  title = 'AI is transforming your space',
  currentStep,
  elapsed = 0,
  onCancel,
  type = 'edit', // 'analysis' | 'edit' | '3d'
}) {
  const icons = {
    analysis: <Sparkles className="w-8 h-8 text-cyan-400" />,
    edit: <Sparkles className="w-8 h-8 text-brand-400" />,
    '3d': <Box className="w-8 h-8 text-cyan-400" />,
  };

  return (
    <div
      aria-live="polite"
      className="w-full flex flex-col items-center justify-center p-8 border border-slate-700/80 rounded-3xl bg-slate-900/80 backdrop-blur-xl shadow-2xl text-center"
    >
      <div className="relative mb-5">
        <div className="w-20 h-20 rounded-3xl bg-slate-800/80 border border-slate-700 flex items-center justify-center shadow-glow">
          {icons[type] || icons.edit}
        </div>
        <Loader2 className="w-24 h-24 text-brand-500 absolute -inset-2 animate-spin opacity-40 pointer-events-none" />
      </div>

      <h3 className="text-lg font-bold text-white tracking-tight mb-1">{title}</h3>

      {currentStep ? (
        <p className="text-sm text-brand-300 font-medium animate-pulse mb-3 max-w-sm">
          {currentStep}
        </p>
      ) : (
        <p className="text-sm text-slate-400 mb-3">Processing design request...</p>
      )}

      <div className="flex items-center gap-2 text-xs text-slate-400 mb-6 bg-slate-800/60 px-3 py-1.5 rounded-full border border-slate-700/50">
        <span>Elapsed:</span>
        <span className="font-mono text-slate-300">{elapsed}s</span>
      </div>

      {onCancel && (
        <Button variant="ghost" size="sm" onClick={onCancel} className="text-slate-400 hover:text-red-400">
          Cancel Operation
        </Button>
      )}
    </div>
  );
}

export default AIProcessingState;
