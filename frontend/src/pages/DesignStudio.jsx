import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  UploadCloud,
  Wand2,
  Box,
  RotateCcw,
  CheckCircle2,
  ArrowRight,
  AlertCircle,
  Eye,
} from 'lucide-react';

import useStudioStore from '../store/studioStore';
import {
  useUploadMutation,
  useAnalyzeMutation,
  useGenerateEditMutation,
  useApproveProjectMutation,
  useMake3DMutation,
} from '../queries/useQueries';
import useAsyncJob from '../hooks/useAsyncJob';

import StudioStepper from '../components/studio/StudioStepper';
import ImageUploader from '../components/studio/ImageUploader';
import DetectedObjects from '../components/studio/DetectedObjects';
import PromptEditor from '../components/studio/PromptEditor';
import ImageComparison from '../components/studio/ImageComparison';
import ApprovalActions from '../components/studio/ApprovalActions';
import AIProcessingState from '../components/studio/AIProcessingState';
import Button from '../components/common/Button';
import ErrorMessage from '../components/common/ErrorMessage';
import { resolveAssetUrl } from '../services/api';

export function DesignStudio() {
  const navigate = useNavigate();

  // Zustand client studio state machine
  const {
    stage,
    setStage,
    activeProjectId,
    activeImageId,
    originalImageUrl,
    originalFileName,
    detectedObjects,
    detections,
    selectedDetection,
    selectedObject,
    prompt,
    targetObject,
    editedImageUrl,
    model3dUrl,
    isApproved,
    setUploadedImage,
    setAnalysisResult,
    setSelectedObject,
    setSelectedDetection,
    setPrompt,
    setTargetObject,
    setEditResult,
    approveDesign,
    set3DResult,
    editAgain,
    startNewProject,
    setError,
    errorMessage,
  } = useStudioStore();

  const [showMaskOverlay, setShowMaskOverlay] = useState(true);

  // Mutations
  const uploadMutation = useUploadMutation();
  const analyzeMutation = useAnalyzeMutation();
  const editMutation = useGenerateEditMutation();
  const approveMutation = useApproveProjectMutation();
  const make3DMutation = useMake3DMutation();

  // Async job runner with progress & cancellation
  const { runJob, cancelJob, isRunning, step, elapsed } = useAsyncJob();

  const [uploadProgress, setUploadProgress] = useState(0);

  // ── Step 1: Upload & Auto-Analyze ──────────────────────────────────────────
  const handleImageUpload = async (file, previewUrl) => {
    setStage('uploading');
    setUploadProgress(0);

    try {
      const uploadResult = await uploadMutation.mutateAsync({
        file,
        onProgress: (p) => setUploadProgress(p),
      });

      setUploadedImage({
        imageId: uploadResult.image_id,
        imageUrl: uploadResult.image_path,
        fileName: uploadResult.original_filename,
      });

      // Auto-trigger analysis
      await handleRunAnalysis(uploadResult.image_id);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to upload image. Please try again.';
      setError(msg);
    }
  };

  // ── Step 2: Run AI Scene Analysis ─────────────────────────────────────────
  const handleRunAnalysis = async (imageId, customPrompt) => {
    const idToAnalyze = imageId || activeImageId;
    if (!idToAnalyze) return;

    setStage('analyzing');

    try {
      await runJob(
        [
          { message: 'Scanning image with GroundingDINO...', delayMs: 1200 },
          { message: 'Detecting boundaries and calculating confidence...', delayMs: 1500 },
          { message: 'Generating precision segmentation masks with SAM ViT-B...', delayMs: 1200 },
        ],
        async ({ signal }) => {
          const DEFAULT_ROOM_PROMPT = 'sofa . door . table . cabinet . lamp . window . television . wall . ceiling';
          const promptToUse = customPrompt || (prompt.trim() ? prompt : DEFAULT_ROOM_PROMPT);
          const res = await analyzeMutation.mutateAsync({
            image_id: idToAnalyze,
            prompt: promptToUse,
            signal,
          });

          const rawDetections = res.detections || [];
          const labels = rawDetections.map((d) => d.label);
          const finalObjects =
            res.objects && res.objects.length > 0
              ? res.objects
              : (labels.length > 0 ? Array.from(new Set(labels)) : [promptToUse]);

          setAnalysisResult({
            objects: finalObjects,
            detections: rawDetections,
          });

          // Auto-select first detection if available
          if (rawDetections.length > 0) {
            setSelectedDetection(rawDetections[0]);
          }

          return res;
        }
      );
    } catch (err) {
      if (err.name !== 'CanceledError') {
        const msg = err.response?.data?.detail || 'Scene analysis failed. Please try again.';
        setError(msg);
      }
    }
  };

  // ── Step 3: Prompt AI Image Customization ─────────────────────────────────
  const handleGenerateEdit = async () => {
    if (!activeImageId || !prompt) return;

    setStage('generating');

    try {
      await runJob(
        [
          { message: `Locating target (${targetObject || 'selected region'}) with SAM...`, delayMs: 1500 },
          { message: 'Generating segmentation mask...', delayMs: 1500 },
          { message: 'Applying diffusion inpainting with natural prompt...', delayMs: 2000 },
          { message: 'Blending texture, shadow, and lighting...', delayMs: 1500 },
        ],
        async ({ signal }) => {
          const res = await editMutation.mutateAsync({
            image_id: activeImageId,
            prompt,
            project_id: activeProjectId,
            target_object: targetObject,
            signal,
          });

          setEditResult({
            projectId: res.project_id,
            editedImage: res.edited_image,
            prompt: res.prompt,
            targetObject: res.target_object || targetObject,
          });
          return res;
        }
      );
    } catch (err) {
      if (err.name !== 'CanceledError') {
        const msg = err.response?.data?.detail || 'Image customization failed. Please try again.';
        setError(msg);
      }
    }
  };

  // ── Step 3.5: Approve Design ─────────────────────────────────────────────
  const handleApproveDesign = async () => {
    if (activeProjectId) {
      try {
        await approveMutation.mutateAsync(activeProjectId);
      } catch (err) {
        console.error('Failed to update project approval in database:', err);
      }
    }
    approveDesign();
  };

  // ── Step 4: Make It 3D ───────────────────────────────────────────────────
  const handleMakeIt3D = async () => {
    if (!activeProjectId) return;

    setStage('making3d');

    try {
      await runJob(
        [
          { message: 'Estimating depth map with Depth Anything...', delayMs: 1600 },
          { message: 'Synthesizing multi-view spatial perspective...', delayMs: 1800 },
          { message: 'Reconstructing 3D mesh geometry...', delayMs: 2000 },
          { message: 'Exporting optimized .GLB interactive file...', delayMs: 1500 },
        ],
        async ({ signal }) => {
          const res = await make3DMutation.mutateAsync({
            project_id: activeProjectId,
            image_id: activeImageId,
            signal,
          });

          set3DResult({ modelUrl: res.model });
          return res;
        }
      );
    } catch (err) {
      if (err.name !== 'CanceledError') {
        const msg = err.response?.data?.detail || '3D Model generation failed. Please try again.';
        setError(msg);
      }
    }
  };

  const handleOpen3DViewer = () => {
    if (model3dUrl) {
      navigate('/viewer');
    }
  };

  return (
    <div className="flex-1 flex flex-col w-full bg-[#0b0f19]">
      {/* Top Stepper Bar */}
      <StudioStepper currentStage={stage} />

      {/* Main Studio Body */}
      <div className="flex-1 max-w-7xl mx-auto w-full p-4 sm:p-6 lg:p-8 flex flex-col lg:flex-row gap-6">
        {/* ── Left Workspace (Image Canvas) ─────────────────────────────────── */}
        <div className="flex-1 flex flex-col gap-4">
          {/* Top workspace bar */}
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Workspace Canvas
              </span>
              {originalFileName && (
                <span className="text-xs text-slate-500 truncate max-w-xs">
                  &bull; {originalFileName}
                </span>
              )}
            </div>

            {stage !== 'idle' && (
              <Button
                variant="ghost"
                size="sm"
                onClick={startNewProject}
                leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
              >
                Reset Studio
              </Button>
            )}
          </div>

          {/* Error Banner if error stage */}
          {stage === 'error' && (
            <ErrorMessage
              title="Pipeline Execution Error"
              message={errorMessage}
              onRetry={() => {
                if (!activeImageId) {
                  setStage('idle');
                } else if (editedImageUrl) {
                  setStage('result');
                } else {
                  setStage('analyzed');
                }
              }}
            />
          )}

          {/* Workspace display based on current stage */}
          {stage === 'idle' || stage === 'uploading' ? (
            <div className="flex-1 min-h-[460px] glass-panel rounded-3xl p-6 flex items-center justify-center">
              <ImageUploader
                onImageSelected={handleImageUpload}
                isUploading={stage === 'uploading'}
                uploadProgress={uploadProgress}
              />
            </div>
          ) : stage === 'analyzing' ? (
            <div className="flex-1 min-h-[460px] flex items-center justify-center">
              <AIProcessingState
                type="analysis"
                title="Analyzing Room & Identifying Objects"
                currentStep={step}
                elapsed={elapsed}
                onCancel={cancelJob}
              />
            </div>
          ) : stage === 'generating' ? (
            <div className="flex-1 min-h-[460px] flex items-center justify-center">
              <AIProcessingState
                type="edit"
                title="Applying AI Customization"
                currentStep={step}
                elapsed={elapsed}
                onCancel={cancelJob}
              />
            </div>
          ) : stage === 'making3d' ? (
            <div className="flex-1 min-h-[460px] flex items-center justify-center">
              <AIProcessingState
                type="3d"
                title="Generating 3D Spatial Model"
                currentStep={step}
                elapsed={elapsed}
                onCancel={cancelJob}
              />
            </div>
          ) : stage === 'result' || stage === 'approved' || stage === 'done' ? (
            <div className="flex-1 flex flex-col gap-4">
              <ImageComparison
                originalImage={originalImageUrl}
                editedImage={editedImageUrl}
                prompt={prompt}
                targetObject={targetObject}
              />

              {/* Approval Bar */}
              <ApprovalActions
                isApproved={isApproved}
                onApprove={handleApproveDesign}
                onEditAgain={editAgain}
                onMakeIt3D={handleMakeIt3D}
                isGenerating3D={stage === 'making3d'}
              />

              {/* Ready for 3D Banner */}
              {stage === 'done' && model3dUrl && (
                <div className="p-4 rounded-2xl bg-gradient-to-r from-brand-900/80 via-dark-850 to-cyan-950/80 border border-brand-500/40 flex flex-col sm:flex-row items-center justify-between gap-4 animate-in fade-in duration-300">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-300 flex items-center justify-center">
                      <Box className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">3D Space Model Ready!</h4>
                      <p className="text-xs text-slate-300">
                        Interact, rotate, zoom, and inspect your redesigned room in real-time 3D.
                      </p>
                    </div>
                  </div>

                  <Button
                    variant="cyan"
                    size="md"
                    onClick={handleOpen3DViewer}
                    rightIcon={<ArrowRight className="w-4 h-4" />}
                  >
                    Open 3D Viewer
                  </Button>
                </div>
              )}
            </div>
          ) : (
            /* 'uploaded' or 'analyzed' stage */
            <div className="flex-1 min-h-[460px] glass-panel rounded-3xl p-4 flex flex-col items-center justify-center overflow-hidden relative group">
              {originalImageUrl && (
                <div className="relative w-full h-full max-h-[500px] flex items-center justify-center">
                  <img
                    src={resolveAssetUrl(originalImageUrl)}
                    alt="Source space"
                    className="w-full h-full max-h-[500px] object-contain rounded-2xl"
                  />
                  {showMaskOverlay && selectedDetection?.mask_url && (
                    <img
                      src={resolveAssetUrl(selectedDetection.mask_url)}
                      alt={`SAM Mask - ${selectedDetection.label}`}
                      className="absolute inset-0 w-full h-full max-h-[500px] object-contain rounded-2xl pointer-events-none mix-blend-screen opacity-75 filter drop-shadow-[0_0_12px_rgba(34,197,94,0.8)]"
                    />
                  )}
                </div>
              )}
              {selectedDetection?.mask_url && (
                <div className="absolute top-6 right-6 flex items-center gap-2 bg-slate-900/85 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700 text-xs text-slate-300 shadow-xl">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  <span>
                    SAM Mask: <strong className="capitalize">{selectedDetection.label}</strong> ({Math.round(selectedDetection.confidence * 100)}%)
                  </span>
                  <button
                    type="button"
                    onClick={() => setShowMaskOverlay(!showMaskOverlay)}
                    className="ml-2 text-cyan-400 hover:text-cyan-300 underline text-[11px]"
                  >
                    {showMaskOverlay ? 'Hide Mask' : 'Show Mask'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── Right Panel (AI Control Center) ───────────────────────────────── */}
        <div className="w-full lg:w-96 flex-shrink-0 flex flex-col gap-5">
          <div className="glass-panel p-5 rounded-3xl border border-slate-800 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-brand-400" />
                AI Space Controls
              </h3>
              <span className="text-[11px] text-slate-400 font-mono uppercase">
                Stage: {stage}
              </span>
            </div>

            {/* Detected Objects Section */}
            {(detectedObjects.length > 0 || detections.length > 0 || stage === 'analyzed') && (
              <DetectedObjects
                objects={detectedObjects}
                detections={detections}
                selectedObject={selectedObject}
                selectedDetection={selectedDetection}
                onSelectObject={setSelectedObject}
                onSelectDetection={setSelectedDetection}
                onReScan={(term) => handleRunAnalysis(activeImageId, term)}
                isAnalyzing={stage === 'analyzing'}
              />
            )}

            {/* Prompt Editor */}
            {stage !== 'idle' && stage !== 'uploading' && (
              <div className="pt-2">
                <PromptEditor
                  prompt={prompt}
                  setPrompt={setPrompt}
                  targetObject={targetObject}
                  setTargetObject={setTargetObject}
                  detectedObjects={detectedObjects}
                  selectedObject={selectedObject}
                  onSubmit={handleGenerateEdit}
                  isGenerating={stage === 'generating'}
                />
              </div>
            )}

            {/* Hint when in idle */}
            {stage === 'idle' && (
              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                <UploadCloud className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400">
                  Upload an image on the canvas to begin AI space detection and prompt-guided redesign.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DesignStudio;
