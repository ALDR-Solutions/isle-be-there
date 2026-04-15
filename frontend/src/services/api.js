import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

let getAccessToken = () => null;
let getRefreshToken = () => null;
let setTokens = () => { };
let handleUnauthorized = async () => { };

export function registerAuthSessionHandlers(handlers = {}) {
  if (handlers.getAccessToken) getAccessToken = handlers.getAccessToken;
  if (handlers.getRefreshToken) getRefreshToken = handlers.getRefreshToken;
  if (handlers.setTokens) setTokens = handlers.setTokens;
}

export function registerUnauthorizedHandler(handler) {
  handleUnauthorized = handler || (async () => { });
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
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

      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          setTokens({ accessToken: access_token, refreshToken: refresh_token });

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          await handleUnauthorized({ reason: 'refresh_failed' });
          return Promise.reject(refreshError);
        }
      }

      await handleUnauthorized({ reason: 'missing_refresh_token' });
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
  search: (query) => api.get('/api/listings/search', {
    params: query?.trim() ? { q: query.trim() } : {},
  }),
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
  create: (data) => api.post('/api/reviews/submit', data),
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
  updateAvatar: (avatarUrl) => api.put('/api/profile', { avatar_url: avatarUrl }),
  setInterestsHandled: () => api.patch('/api/profile/interests-handled'),

};

// Interests API
export const interestsAPI = {
  getAll: () => api.get('/api/interests'),
  getByBusinessType: (businessTypeId) => api.get(`/api/interests/business-type/${businessTypeId}`),
  getUserInterests: () => api.get('/api/interests/user'),
  updateUserInterests: (interestIds) => api.put('/api/interests/user', { interest_ids: interestIds }),
  getCategories: async () => {
    const response = await api.get('/api/interests');
    const categories = [...new Set((response.data || []).map((interest) => interest.category).filter(Boolean))];
    return { ...response, data: categories };
  },
};

// Businesses API
export const businessesAPI = {
  getAll: (params) => api.get('/api/businesses', { params }),
  getById: (id) => api.get(`/api/businesses/${id}`),
  getMe: () => api.get('/api/businesses/me'),
  update: (id, data) => api.put(`/api/businesses/${id}`, data),
  getListings: (params) => api.get('/api/businesses/listings', { params }),
  getTypes: () => api.get('/api/businesses/types'),
};

export const employeesAPI = {
  getAll: () => api.get('/api/employees'),
  create: (data) => api.post('/api/employees', data),
  assignToListing: (employeeId, listingId) => api.post(`/api/employees/${employeeId}/listings/${listingId}`),
  unassignFromListing: (employeeId, listingId) => api.delete(`/api/employees/${employeeId}/listings/${listingId}`),
  getListings: (employeeId) => api.get(`/api/employees/${employeeId}/listings`),
  getEmployeesForListing: (listingId) => api.get(`/api/employees/listings/${listingId}`),
};

export const servicesAPI = {
  getById: (serviceId) => api.get(`/api/services/${serviceId}`),
  getAll: (params) => api.get('/api/services', { params }),
  create: (data) => api.post('/api/services/create', data),
  update: (serviceId, data) => api.put(`/api/services/update/${serviceId}`, data),
  deactivate: (serviceId) => api.patch(`/api/services/${serviceId}`),
  delete: (serviceId) => api.delete(`/api/services/${serviceId}`),
};

export const uploadsAPI = {
  uploadImage: (formData, { folder = 'misc' } = {}) => {
    formData.set('folder', folder);
    return api.post('/api/upload', formData, {
      transformRequest: [(data, headers) => {
        if (headers?.set) {
          headers.set('Content-Type', undefined);
        }
        if (headers && 'Content-Type' in headers) {
          delete headers['Content-Type'];
        }
        return data;
      }],
    });
  },
  deleteImages: (urls) => api.delete('/api/upload', { data: { urls } }),
};

export default api;
