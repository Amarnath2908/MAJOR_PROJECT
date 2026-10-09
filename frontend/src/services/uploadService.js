import api from './api';

export const uploadService = {
  /**
   * Upload an image file to the backend
   * @param {File} file - The file to upload
   * @param {Function} [onProgress] - Optional progress callback
   * @returns {Promise<{
   *   image_id: string,
   *   image_path: string,
   *   original_filename: string,
   *   file_size_mb: number,
   *   mime_type: string,
   *   width: number,
   *   height: number,
   *   status: string
   * }>}
   */
  async uploadImage(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  },

  /**
   * Fetch metadata for an uploaded image
   * @param {string} imageId
   */
  async getImageMetadata(imageId) {
    const response = await api.get(`/upload/${imageId}`);
    return response.data;
  },
};

export default uploadService;
