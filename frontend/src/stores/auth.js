/**
 * Authentication store using Pinia.
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authAPI } from '../services/api';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const loading = ref(false);
  const error = ref(null);

  const isAuthenticated = computed(() => !!user.value);
  const isBusiness = computed(() => user.value?.is_business || false);
  const isAdmin = computed(() => user.value?.is_admin || false);

  async function login(email, password) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, refresh_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      await fetchUser();
      return true;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function register(userData) {
    loading.value = true;
    error.value = null;
    
    try {
      await authAPI.register(userData);
      // Auto-login after registration
      return await login(userData.email, userData.password);
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function fetchUser() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      user.value = null;
      return;
    }
    
    try {
      const response = await authAPI.getMe();
      user.value = response.data;
    } catch (err) {
      logout();
    }
  }

  function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    user.value = null;
  }

  function initialize() {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUser();
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    isBusiness,
    isAdmin,
    login,
    register,
    fetchUser,
    logout,
    initialize,
  };
});
