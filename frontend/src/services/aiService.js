import api from './api';

export const aiService = {
  /**
   * Run AI object detection / scene analysis on an uploaded image
   * (Uses real GroundingDINO + SAM inference via /analysis/detect)
   * @param {{ image_id: string, prompt: string }} params
   * @param {AbortSignal} [signal]
   * @returns {Promise<{
   *   success: boolean,
   *   prompt: string,
   *   image_id: string,
   *   detections: Array<{
   *     object_id: string,
   *     label: string,
   *     confidence: number,
   *     bbox: { x1: number, y1: number, x2: number, y2: number },
   *     mask_url: string|null,
   *     mask_score: number
   *   }>,
   *   count: number,
   *   message: string
   * }>}
   */
  async analyzeImage({ image_id, prompt }, signal) {
    const response = await api.post(
      '/analysis/detect',
      { image_id, prompt: prompt || 'objects' },
      { signal }
    );
    return response.data;
  },

  /**
   * Run prompt-based AI image editing / inpainting
   * (Interfaces with backend SAM + ImageEditor mock)
   * @param {{ image_id: string, prompt: string, project_id?: string, target_object?: string }} params
   * @param {AbortSignal} [signal]
   * @returns {Promise<{
   *   project_id: string,
   *   image_id: string,
   *   prompt: string,
   *   target_object?: string,
   *   edited_image: string,
   *   status: string,
   *   message: string
   * }>}
   */
  async generateEdit({ image_id, prompt, project_id, target_object }, signal) {
    const payload = {
      image_id,
      prompt,
      ...(project_id ? { project_id } : {}),
      ...(target_object ? { target_object } : {}),
    };
    const response = await api.post('/editor/edit', payload, { signal });
    return response.data;
  },

  /**
   * Run 3D model generation
   * (Interfaces with backend InstantMesh / mesh_generator mock)
   * @param {{ project_id: string, image_id?: string }} params
   * @param {AbortSignal} [signal]
   * @returns {Promise<{ project_id: string, model: string, status: string, message: string }>}
   */
  async generate3D({ project_id, image_id }, signal) {
    const payload = {
      project_id,
      ...(image_id ? { image_id } : {}),
    };
    const response = await api.post('/viewer/generate3d', payload, { signal });
    return response.data;
  },

  /**
   * Extracts or infers the target object from natural language prompt and detected objects
   * e.g. "Change the sofa to blue leather" + ["Wall", "Sofa", "Floor"] -> "Sofa"
   * @param {string} prompt
   * @param {string[]} detectedObjects
   * @returns {string|null}
   */
  identifyTargetObject(prompt, detectedObjects = []) {
    if (!prompt) return null;
    const lower = prompt.toLowerCase();
    // 1. Direct match against detected objects list
    for (const obj of detectedObjects) {
      if (lower.includes(obj.toLowerCase())) {
        return obj;
      }
    }

    // 2. Common spatial/interior synonyms if detected objects doesn't directly hit
    const commonObjects = [
      'sofa', 'couch', 'chair', 'table', 'wall', 'floor', 'ceiling',
      'lamp', 'light', 'curtain', 'window', 'door', 'bed', 'cabinet',
      'desk', 'rug', 'carpet', 'shelf', 'plant', 'tv', 'cushion',
    ];
    for (const item of commonObjects) {
      if (lower.includes(item)) {
        return item.charAt(0).toUpperCase() + item.slice(1);
      }
    }

    return null;
  },
};

export default aiService;
