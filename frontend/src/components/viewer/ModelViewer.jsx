import React, { Suspense, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, Grid, Html } from '@react-three/drei';
import ModelLoader from './ModelLoader';
import ViewerControls from './ViewerControls';
import ViewerErrorBoundary from './ViewerErrorBoundary';
import { resolveAssetUrl } from '../../services/api';
import Loader from '../common/Loader';

function CanvasLoader() {
  return (
    <Html center>
      <div className="p-4 rounded-2xl bg-dark-900/90 border border-slate-800 backdrop-blur-md shadow-2xl flex flex-col items-center">
        <Loader text="Streaming 3D GLB Model..." size="md" />
      </div>
    </Html>
  );
}

export function ModelViewer({
  modelUrl,
  title = '3D Space Reconstruction',
  onBackToStudio,
}) {
  const containerRef = useRef(null);
  const controlsRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isAutoRotating, setIsAutoRotating] = useState(false);
  const [showGrid, setShowGrid] = useState(true);

  const fullUrl = resolveAssetUrl(modelUrl);

  const handleResetView = () => {
    if (controlsRef.current) {
      controlsRef.current.reset();
    }
  };

  const handleToggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().then(() => setIsFullscreen(true)).catch(() => {});
    } else {
      document.exitFullscreen().then(() => setIsFullscreen(false)).catch(() => {});
    }
  };

  const handleDownloadGlb = () => {
    if (!fullUrl) return;
    const a = document.createElement('a');
    a.href = fullUrl;
    a.download = `${title.toLowerCase().replace(/\s+/g, '_')}_model.glb`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div
      ref={containerRef}
      className={`relative w-full flex flex-col rounded-3xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl ${
        isFullscreen ? 'h-screen' : 'h-[640px]'
      }`}
    >
      {/* 3D Canvas Canvas */}
      <div className="flex-1 w-full h-full relative">
        <ViewerErrorBoundary onReset={handleResetView}>
          <Canvas
            camera={{ position: [0, 2, 5], fov: 45 }}
            dpr={[1, 2]} // Cap device pixel ratio for demo performance
            className="w-full h-full"
          >
            <ambientLight intensity={0.7} />
            <directionalLight position={[10, 10, 5]} intensity={1.2} castShadow />
            <directionalLight position={[-10, 10, -5]} intensity={0.5} />
            <pointLight position={[0, 4, 0]} intensity={0.8} />

            <Suspense fallback={<CanvasLoader />}>
              {fullUrl && <ModelLoader url={fullUrl} />}
              <Environment preset="city" />
            </Suspense>

            {showGrid && (
              <Grid
                renderOrder={-1}
                position={[0, -0.01, 0]}
                infiniteGrid
                cellSize={0.5}
                cellThickness={0.6}
                cellColor="#334155"
                sectionSize={2}
                sectionThickness={1.2}
                sectionColor="#6366f1"
                fadeDistance={25}
              />
            )}

            <OrbitControls
              ref={controlsRef}
              autoRotate={isAutoRotating}
              autoRotateSpeed={1.5}
              enableDamping
              dampingFactor={0.05}
              minDistance={1}
              maxDistance={15}
            />
          </Canvas>
        </ViewerErrorBoundary>

        {/* Orbit hint overlay */}
        <div className="absolute top-4 left-4 pointer-events-none bg-dark-900/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-800 text-[11px] text-slate-400">
          Left Click + Drag: Rotate &bull; Right Click: Pan &bull; Scroll: Zoom
        </div>
      </div>

      {/* Control Bar Overlay */}
      <div className="p-3 border-t border-slate-800/80 bg-dark-900/90">
        <ViewerControls
          onResetView={handleResetView}
          isFullscreen={isFullscreen}
          onToggleFullscreen={handleToggleFullscreen}
          onDownloadGlb={handleDownloadGlb}
          isAutoRotating={isAutoRotating}
          onToggleAutoRotate={() => setIsAutoRotating(!isAutoRotating)}
          showGrid={showGrid}
          onToggleGrid={() => setShowGrid(!showGrid)}
        />
      </div>
    </div>
  );
}

export default ModelViewer;
