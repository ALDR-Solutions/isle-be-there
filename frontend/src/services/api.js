/**
 * API service for communicating with the backend.
 */
import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (credentials) => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    return api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  refresh: (refreshToken) => api.post('/api/auth/refresh', { refresh_token: refreshToken }),
  getMe: () => api.get('/api/auth/me'),
  disableAccount: () => api.delete('/api/auth/me'),
};

// Listings API
export const listingsAPI = {
  getAll: (params) => api.get('/api/listings', { params }),
  getById: (id) => api.get(`/api/listings/${id}`),
  create: (data) => api.post('/api/listings', data),
  update: (id, data) => api.put(`/api/listings/${id}`, data),
  delete: (id) => api.delete(`/api/listings/${id}`),
  getPersonalized: (params) => api.get('/api/listings/personalized', { params }),
};

// Bookings API
export const bookingsAPI = {
  getAll: (params) => api.get('/api/bookings', { params }),
  getById: (id) => api.get(`/api/bookings/${id}`),
  create: (data) => api.post('/api/bookings', data),
  update: (id, data) => api.put(`/api/bookings/${id}`, data),
  cancel: (id) => api.delete(`/api/bookings/${id}`),
};

// Reviews API
export const reviewsAPI = {
  getAll: (params) => api.get('/api/reviews', { params }),
  getById: (id) => api.get(`/api/reviews/${id}`),
  create: (data) => api.post('/api/reviews', data),
  update: (id, data) => api.put(`/api/reviews/${id}`, data),
  delete: (id) => api.delete(`/api/reviews/${id}`),
};

// Favourites API
export const favouritesAPI = {
  getAll: () => api.get('/api/favourites'),
  add: (listingId) => api.post(`/api/favourites/${listingId}`),
  remove: (listingId) => api.delete(`/api/favourites/${listingId}`),
};

// Profile API
export const profileAPI = {
  get: () => api.get('/api/profile'),
  update: (data) => api.put('/api/profile', data),
  updateAvatar: (avatarUrl) => api.put('/api/profile/avatar', null, { params: { avatar_url: avatarUrl } }),
  setInterestsHandled: () => api.patch('/api/profile/interests-handled'),

};

// Interests API
export const interestsAPI = {
  getAll: () => api.get('/api/interests'),
  getUserInterests: () => api.get('/api/interests/user'),
  updateUserInterests: (interestIds) => api.put('/api/interests/user', { interest_ids: interestIds }),
  getCategories: () => api.get('/api/interests/categories'),
};

// Businesses API
export const businessesAPI = {
  getAll: (params) => api.get('/api/businesses', { params }),
  getById: (id) => api.get(`/api/businesses/${id}`),
  getMe: () =>  api.get('/api/businesses/me'),
  update: (id, data) => api.put(`/api/businesses/${id}`, data),
  getListings: (params) => api.get('/api/businesses/listings', { params }),
  getTypes: () => api.get('/api/businesses/types'),
};

export default api;
