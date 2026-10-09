import { create } from 'zustand';

/**
 * Finite Studio Stages:
 * 'idle' -> 'uploading' -> 'uploaded' -> 'analyzing' -> 'analyzed'
 * -> 'generating' -> 'result' -> 'approved' -> 'making3d' -> 'done' | 'error'
 */

const initialState = {
  stage: 'idle',
  activeProjectId: null,
  activeImageId: null,
  originalImageUrl: null,
  originalFileName: null,
  detectedObjects: [],
  detections: [],
  selectedDetection: null,
  selectedObject: null,
  prompt: '',
  targetObject: null,
  editedImageUrl: null,
  model3dUrl: null,
  editHistory: [],
  errorMessage: null,
  stepMessage: '',
  isApproved: false,
};

export const useStudioStore = create((set, get) => ({
  ...initialState,

  setStage: (stage) => set({ stage, errorMessage: null }),
  setStepMessage: (stepMessage) => set({ stepMessage }),
  setError: (errorMessage) => set({ stage: 'error', errorMessage }),

  startNewProject: () => set({ ...initialState, stage: 'idle' }),

  setUploadedImage: ({ imageId, imageUrl, fileName }) =>
    set({
      activeImageId: imageId,
      originalImageUrl: imageUrl,
      originalFileName: fileName,
      stage: 'uploaded',
      errorMessage: null,
    }),

  setAnalysisResult: ({ objects, detections, projectId }) =>
    set({
      detectedObjects: objects || [],
      detections: detections || [],
      ...(projectId ? { activeProjectId: projectId } : {}),
      stage: 'analyzed',
      stepMessage: '',
    }),

  setSelectedObject: (obj) => set({ selectedObject: obj }),
  setSelectedDetection: (det) => set({
    selectedDetection: det,
    selectedObject: det?.label || null,
  }),
  setPrompt: (prompt) => set({ prompt }),
  setTargetObject: (targetObject) => set({ targetObject }),

  setEditResult: ({ projectId, editedImage, prompt, targetObject }) => {
    const currentHistory = get().editHistory;
    const newEntry = {
      prompt,
      editedImageUrl: editedImage,
      timestamp: new Date().toISOString(),
      targetObject: targetObject || get().targetObject,
    };

    set({
      activeProjectId: projectId,
      editedImageUrl: editedImage,
      editHistory: [newEntry, ...currentHistory],
      stage: 'result',
      isApproved: false,
      stepMessage: '',
    });
  },

  approveDesign: () =>
    set({
      isApproved: true,
      stage: 'approved',
    }),

  set3DResult: ({ modelUrl }) =>
    set({
      model3dUrl: modelUrl,
      stage: 'done',
      stepMessage: '',
    }),

  editAgain: () =>
    set({
      stage: 'analyzed',
      isApproved: false,
    }),

  reset: () => set(initialState),
}));

export default useStudioStore;
