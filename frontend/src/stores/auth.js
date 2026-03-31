/**
 * Authentication store using Pinia.
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  authAPI,
  registerAuthSessionHandlers,
} from '../services/api';
import { useFavouritesStore } from './favourites';

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'));
  const refreshToken = ref(localStorage.getItem('refresh_token'));
  const user = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const initialized = ref(false);
  let initializePromise = null;

  const hasToken = computed(() => !!accessToken.value);
  const role = computed(() => {
    if (!user.value) return null;
    if (user.value.is_super_admin) return 'admin';
    if (user.value.is_business) return 'business';
    return 'user';
  });
  const isAuthenticated = computed(() => hasToken.value && !!user.value);
  const isBusiness = computed(() => user.value?.is_business || false);
  const isAdmin = computed(() => user.value?.is_super_admin || false);
  const shouldPromptForInterests = computed(
    () => isAuthenticated.value && !user.value?.interests_handled
  );

  function syncTokensToStorage() {
    if (accessToken.value) {
      localStorage.setItem('access_token', accessToken.value);
    } else {
      localStorage.removeItem('access_token');
    }

    if (refreshToken.value) {
      localStorage.setItem('refresh_token', refreshToken.value);
    } else {
      localStorage.removeItem('refresh_token');
    }
  }

  function setTokens({ accessToken: nextAccessToken = null, refreshToken: nextRefreshToken = null } = {}) {
    accessToken.value = nextAccessToken;
    refreshToken.value = nextRefreshToken;
    syncTokensToStorage();
  }

  function clearSessionState() {
    const favouritesStore = useFavouritesStore();
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    syncTokensToStorage();
    favouritesStore.reset();
  }

  async function login(email, password) {
    const favouritesStore = useFavouritesStore();
    loading.value = true;
    error.value = null;
    
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, refresh_token } = response.data;
      
      setTokens({ accessToken: access_token, refreshToken: refresh_token });
      
      await fetchUser();
      await favouritesStore.fetchAll(true);
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
    if (!hasToken.value) {
      user.value = null;
      return;
    }
    
    try {
      const response = await authAPI.getMe();
      user.value = response.data;
    } catch (err) {
      clearSessionState();
      throw err;
    }
  }

  function logout() {
    clearSessionState();
  }

  function setInterestsHandled(handled = true) {
    if (!user.value) {
      return;
    }

    user.value = {
      ...user.value,
      interests_handled: handled,
    };
  }

  async function initialize() {
    if (initialized.value) {
      return;
    }

    if (initializePromise) {
      return initializePromise;
    }

    const favouritesStore = useFavouritesStore();

    initializePromise = (async () => {
      if (hasToken.value) {
        try {
          await fetchUser();
          await favouritesStore.fetchAll(true);
        } catch (err) {
          error.value = null;
        }
      } else {
        favouritesStore.reset();
      }
    })().finally(() => {
      initialized.value = true;
      initializePromise = null;
    });

    return initializePromise;
  }

  registerAuthSessionHandlers({
    getAccessToken: () => accessToken.value,
    getRefreshToken: () => refreshToken.value,
    setTokens,
  });

  return {
    accessToken,
    refreshToken,
    user,
    loading,
    error,
    initialized,
    hasToken,
    role,
    isAuthenticated,
    isBusiness,
    isAdmin,
    shouldPromptForInterests,
    setTokens,
    setInterestsHandled,
    clearSessionState,
    login,
    register,
    fetchUser,
    logout,
    initialize,
  };
});
