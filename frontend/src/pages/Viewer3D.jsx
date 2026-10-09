import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Box, ArrowLeft, Layers, Sparkles } from 'lucide-react';
import useStudioStore from '../store/studioStore';
import ModelViewer from '../components/viewer/ModelViewer';
import Button from '../components/common/Button';

export function Viewer3D() {
  const navigate = useNavigate();
  const { model3dUrl, prompt, targetObject, originalFileName } = useStudioStore();

  // If accessed directly without an active 3D model, fallback sample or prompt user
  const effectiveModelUrl = model3dUrl || 'storage/models3d/sample.glb';

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full flex flex-col gap-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/studio')}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
            title="Back to Studio"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          <div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-white flex items-center gap-2">
              <Box className="w-6 h-6 text-cyan-400" />
              Interactive 3D Space Viewer
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              InstantMesh single-image neural reconstruction (.GLB format)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/studio">
            <Button variant="secondary" size="sm" leftIcon={<Sparkles className="w-4 h-4 text-brand-400" />}>
              Modify Prompt
            </Button>
          </Link>

          <Link to="/dashboard">
            <Button size="sm" leftIcon={<Layers className="w-4 h-4" />}>
              Dashboard
            </Button>
          </Link>
        </div>
      </div>

      {/* Main 3D Canvas Viewer */}
      <ModelViewer
        modelUrl={effectiveModelUrl}
        title={originalFileName || 'Space 3D Model'}
        onBackToStudio={() => navigate('/studio')}
      />

      {/* Details Box */}
      <div className="p-4 rounded-2xl glass-panel border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs">
        <div className="space-y-1">
          <span className="text-slate-500 font-semibold uppercase tracking-wider block">
            Applied AI Customization
          </span>
          <p className="text-white font-medium italic">
            "{prompt || 'Default 3D Room Reconstruction'}"
          </p>
        </div>

        {targetObject && (
          <div className="px-3 py-1.5 rounded-xl bg-brand-500/15 border border-brand-500/30 text-brand-300 font-semibold">
            Target Focus: {targetObject}
          </div>
        )}
      </div>
    </div>
  );
}

export default Viewer3D;
