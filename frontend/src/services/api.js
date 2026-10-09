import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // 60s for AI processing operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('designverse_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 Unauthorized globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and broadcast logout if unauthorized
      localStorage.removeItem('designverse_token');
      localStorage.removeItem('designverse_user');
      if (window.location.pathname !== '/auth' && window.location.pathname !== '/') {
        window.location.href = `/auth?redirect=${encodeURIComponent(window.location.pathname)}`;
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Normalizes backend storage paths into full reachable URLs.
 * e.g., 'storage/uploads/abc.jpg' -> 'http://localhost:8000/storage/uploads/abc.jpg'
 * For protected image endpoints, appends authentication token query param for <img> tag compatibility.
 */
export function resolveAssetUrl(relativePath) {
  if (!relativePath) return '';
  if (relativePath.startsWith('blob:')) {
    return relativePath;
  }

  let fullUrl = relativePath;
  if (!relativePath.startsWith('http://') && !relativePath.startsWith('https://')) {
    const cleanPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
    fullUrl = `${BASE_URL}/${cleanPath}`;
  }

  // If this points to an image endpoint and user is logged in, attach token query param for <img> rendering
  const token = typeof window !== 'undefined' ? localStorage.getItem('designverse_token') : null;
  if (token && (fullUrl.includes('/upload/images') || fullUrl.includes('/images/')) && !fullUrl.includes('token=')) {
    const separator = fullUrl.includes('?') ? '&' : '?';
    fullUrl = `${fullUrl}${separator}token=${encodeURIComponent(token)}`;
  }

  return fullUrl;
}

export default api;
