import { create } from 'zustand';
import authService from '../services/authService';

export const useAuthStore = create((set) => ({
  user: authService.getStoredUser(),
  token: authService.getToken(),
  isAuthenticated: !!authService.getToken(),
  isLoading: false,

  setAuth: (data) => {
    authService.saveAuth(data);
    set({
      user: data.user,
      token: data.access_token,
      isAuthenticated: true,
    });
  },

  logout: async () => {
    await authService.logout();
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  initAuth: async () => {
    const token = authService.getToken();
    if (!token) {
      set({ user: null, token: null, isAuthenticated: false });
      return;
    }
    try {
      set({ isLoading: true });
      const profile = await authService.getMe();
      set({ user: profile, isAuthenticated: true });
    } catch {
      // If token invalid/expired, drop it cleanly
      await authService.logout();
      set({ user: null, token: null, isAuthenticated: false });
    } finally {
      set({ isLoading: false });
    }
  },
}));

export default useAuthStore;
