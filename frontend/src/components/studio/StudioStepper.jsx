import React from 'react';
import { Upload, Search, Wand2, SplitSquareVertical, Box, Check } from 'lucide-react';

const STEPS = [
  { id: 'upload', name: 'Upload', icon: Upload, stages: ['idle', 'uploading', 'uploaded'] },
  { id: 'analyze', name: 'Analyze', icon: Search, stages: ['analyzing', 'analyzed'] },
  { id: 'customize', name: 'Customize', icon: Wand2, stages: ['generating'] },
  { id: 'compare', name: 'Review', icon: SplitSquareVertical, stages: ['result', 'approved'] },
  { id: '3d', name: '3D Space', icon: Box, stages: ['making3d', 'done'] },
];

export function StudioStepper({ currentStage = 'idle' }) {
  const getStepStatus = (stepIndex) => {
    const currentStepIndex = STEPS.findIndex((s) => s.stages.includes(currentStage));
    const activeIndex = currentStepIndex >= 0 ? currentStepIndex : 0;

    if (stepIndex < activeIndex) return 'complete';
    if (stepIndex === activeIndex) return 'current';
    return 'upcoming';
  };

  return (
    <div className="w-full bg-dark-850/80 border-b border-slate-800 py-3 px-4 sm:px-8">
      <nav aria-label="Progress" className="max-w-4xl mx-auto">
        <ol className="flex items-center justify-between">
          {STEPS.map((step, index) => {
            const status = getStepStatus(index);
            const Icon = step.icon;

            return (
              <li key={step.id} className="relative flex-1 flex items-center">
                <div className="flex items-center gap-2.5 group">
                  <span
                    className={`w-8 h-8 rounded-xl flex items-center justify-center transition-all ${
                      status === 'complete'
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                        : status === 'current'
                        ? 'bg-brand-600 text-white shadow-glow border border-brand-400'
                        : 'bg-slate-800 text-slate-500 border border-slate-700/60'
                    }`}
                  >
                    {status === 'complete' ? (
                      <Check className="w-4 h-4" />
                    ) : (
                      <Icon className="w-4 h-4" />
                    )}
                  </span>
                  <span
                    className={`text-xs font-medium hidden sm:inline-block ${
                      status === 'complete'
                        ? 'text-slate-300'
                        : status === 'current'
                        ? 'text-white font-semibold'
                        : 'text-slate-500'
                    }`}
                  >
                    {step.name}
                  </span>
                </div>

                {index < STEPS.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-3 transition-colors ${
                      status === 'complete' ? 'bg-emerald-500/50' : 'bg-slate-800'
                    }`}
                    aria-hidden="true"
                  />
                )}
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  );
}

export default StudioStepper;
