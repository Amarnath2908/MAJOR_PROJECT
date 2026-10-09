import api from './api';

export const projectService = {
  /**
   * Get paginated project history
   * @param {number} [page=1]
   * @param {number} [pageSize=20]
   * @returns {Promise<{ projects: Array<object>, total: number, status: string }>}
   */
  async getHistory(page = 1, pageSize = 20) {
    const response = await api.get('/history/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  /**
   * Get single project detail by UUID
   * @param {string} projectId
   * @returns {Promise<object>}
   */
  async getProject(projectId) {
    const response = await api.get(`/history/${projectId}`);
    return response.data;
  },

  /**
   * Delete project by UUID
   * @param {string} projectId
   * @returns {Promise<{ status: string, message: string }>}
   */
  async deleteProject(projectId) {
    const response = await api.delete(`/history/${projectId}`);
    return response.data;
  },

  /**
   * Approve project design
   * @param {string} projectId
   * @returns {Promise<{ project_id: string, status: string, message: string }>}
   */
  async approveProject(projectId) {
    const response = await api.post('/editor/approve', { project_id: projectId });
    return response.data;
  },
};

export default projectService;
