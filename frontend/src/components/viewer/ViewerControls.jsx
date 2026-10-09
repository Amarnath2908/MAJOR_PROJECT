import React from 'react';
import {
  RotateCcw,
  Maximize2,
  Minimize2,
  Download,
  Play,
  Pause,
  Grid,
} from 'lucide-react';
import Button from '../common/Button';

export function ViewerControls({
  onResetView,
  isFullscreen,
  onToggleFullscreen,
  onDownloadGlb,
  isAutoRotating,
  onToggleAutoRotate,
  showGrid,
  onToggleGrid,
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-dark-850/90 backdrop-blur-md border border-slate-800 rounded-2xl">
      {/* Visual Toggles */}
      <div className="flex items-center gap-1.5">
        <button
          type="button"
          onClick={onToggleAutoRotate}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors cursor-pointer ${
            isAutoRotating
              ? 'bg-brand-600/30 text-brand-300 border-brand-500/40'
              : 'bg-slate-800/80 text-slate-400 border-slate-700/60 hover:text-white'
          }`}
          title="Toggle Auto Rotation"
        >
          {isAutoRotating ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          <span>Auto-Rotate</span>
        </button>

        <button
          type="button"
          onClick={onToggleGrid}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors cursor-pointer ${
            showGrid
              ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
              : 'bg-slate-800/80 text-slate-400 border-slate-700/60 hover:text-white'
          }`}
          title="Toggle Ground Grid"
        >
          <Grid className="w-3.5 h-3.5" />
          <span>Grid</span>
        </button>
      </div>

      {/* Camera and Download Actions */}
      <div className="flex items-center gap-2">
        <Button
          size="sm"
          variant="secondary"
          onClick={onResetView}
          leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
          title="Reset Camera View"
        >
          Reset View
        </Button>

        <Button
          size="sm"
          variant="secondary"
          onClick={onToggleFullscreen}
          leftIcon={
            isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />
          }
          title="Toggle Fullscreen"
        >
          {isFullscreen ? 'Exit Full' : 'Fullscreen'}
        </Button>

        {onDownloadGlb && (
          <Button
            size="sm"
            variant="cyan"
            onClick={onDownloadGlb}
            leftIcon={<Download className="w-3.5 h-3.5" />}
            title="Download GLB Model File"
          >
            Download GLB
          </Button>
        )}
      </div>
    </div>
  );
}

export default ViewerControls;
