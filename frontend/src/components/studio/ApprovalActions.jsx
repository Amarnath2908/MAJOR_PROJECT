import React from 'react';
import { RotateCcw, CheckCircle2, Box, Sparkles } from 'lucide-react';
import Button from '../common/Button';

export function ApprovalActions({
  isApproved,
  onApprove,
  onEditAgain,
  onMakeIt3D,
  isGenerating3D,
}) {
  return (
    <div className="p-4 rounded-2xl bg-dark-850/80 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
      {/* Status note */}
      <div className="flex items-center gap-2.5">
        {isApproved ? (
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
            <CheckCircle2 className="w-5 h-5" />
            <span>Design Approved! Ready to generate your interactive 3D model.</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-slate-400 text-xs">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span>Satisfied with this customized look? Approve it to convert into 3D.</span>
          </div>
        )}
      </div>

      {/* Buttons */}
      <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
        {/* Edit Again button */}
        <Button
          variant="secondary"
          size="md"
          onClick={onEditAgain}
          disabled={isGenerating3D}
          leftIcon={<RotateCcw className="w-4 h-4" />}
        >
          Edit Again
        </Button>

        {/* Approve or Make 3D */}
        {!isApproved ? (
          <Button
            variant="primary"
            size="md"
            onClick={onApprove}
            leftIcon={<CheckCircle2 className="w-4 h-4" />}
          >
            Approve Design
          </Button>
        ) : (
          <Button
            variant="cyan"
            size="md"
            onClick={onMakeIt3D}
            isLoading={isGenerating3D}
            leftIcon={<Box className="w-4 h-4" />}
            className="animate-pulse"
          >
            MAKE IT 3D
          </Button>
        )}
      </div>
    </div>
  );
}

export default ApprovalActions;
