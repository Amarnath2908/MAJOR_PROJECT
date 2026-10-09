import api from './api';

export const authService = {
  /**
   * Register a new user
   * @param {{ username: string, email: string, password: string, full_name?: string }} data
   * @returns {Promise<{ access_token: string, token_type: string, expires_in: number, user: object }>}
   */
  async register(data) {
    const payload = {
      username: data.username,
      email: data.email,
      password: data.password,
      ...(data.full_name ? { full_name: data.full_name } : {}),
    };
    const response = await api.post('/auth/register', payload);
    return response.data;
  },

  /**
   * Log in with email and password
   * @param {{ email: string, password: string }} data
   * @returns {Promise<{ access_token: string, token_type: string, expires_in: number, user: object }>}
   */
  async login(data) {
    const response = await api.post('/auth/login', {
      email: data.email,
      password: data.password,
    });
    return response.data;
  },

  /**
   * Get current authenticated user profile
   * @returns {Promise<object>}
   */
  async getMe() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  /**
   * Logout user (notifies backend and client drops token)
   */
  async logout() {
    try {
      await api.post('/auth/logout');
    } catch {
      // client-side cleanup regardless
    } finally {
      localStorage.removeItem('designverse_token');
      localStorage.removeItem('designverse_user');
    }
  },

  getToken() {
    return localStorage.getItem('designverse_token');
  },

  saveAuth(data) {
    if (data.access_token) {
      localStorage.setItem('designverse_token', data.access_token);
    }
    if (data.user) {
      localStorage.setItem('designverse_user', JSON.stringify(data.user));
    }
  },

  getStoredUser() {
    try {
      const raw = localStorage.getItem('designverse_user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
};

export default authService;
