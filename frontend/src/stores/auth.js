import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  authAPI,
  registerAuthSessionHandlers,
} from '../services/api';
import { readStoredTokens, writeStoredTokens } from '../services/authSession';
import { useFavouritesStore } from './favourites';

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(null);
  const refreshToken = ref(null);
  const user = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const bootstrapped = ref(false);
  const authResolving = ref(false);
  const authResolved = ref(false);
  let authResolutionPromise = null;

  const hasToken = computed(() => !!accessToken.value);
  const isAuthPending = computed(
    () => bootstrapped.value && hasToken.value && !authResolved.value,
  );
  const role = computed(() => {
    if (!user.value) return null;
    if (user.value.user_type === 'admin') return 'admin';
    if (user.value.user_type === 'business') return 'business';
    if (user.value.user_type === 'employee') return 'employee';
    return 'user';
  });
  const isAuthenticated = computed(() => hasToken.value && !!user.value);
  const isBusiness = computed(() => user.value?.user_type === 'business');
  const isAdmin = computed(() => user.value?.user_type === 'admin');
  const isEmployee = computed(() => user.value?.user_type === 'employee');
  const shouldPromptForInterests = computed(
    () => isAuthenticated.value && !user.value?.interests_handled
  );

  function syncTokensToStorage() {
    writeStoredTokens({
      accessToken: accessToken.value,
      refreshToken: refreshToken.value,
    });
  }

  function setTokens({ accessToken: nextAccessToken = null, refreshToken: nextRefreshToken = null } = {}) {
    accessToken.value = nextAccessToken;
    refreshToken.value = nextRefreshToken;
    bootstrapped.value = true;
    authResolved.value = !nextAccessToken || !!user.value;
    syncTokensToStorage();
  }

  function clearSessionState() {
    const favouritesStore = useFavouritesStore();
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    bootstrapped.value = true;
    authResolving.value = false;
    authResolved.value = true;
    authResolutionPromise = null;
    syncTokensToStorage();
    favouritesStore.reset();
  }

  function hydrateFromStorage() {
    if (bootstrapped.value) {
      return;
    }

    const storedTokens = readStoredTokens();
    accessToken.value = storedTokens.accessToken;
    refreshToken.value = storedTokens.refreshToken;
    bootstrapped.value = true;
    authResolved.value = !storedTokens.accessToken;
  }

  async function login(email, password) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, refresh_token } = response.data;
      
      setTokens({ accessToken: access_token, refreshToken: refresh_token });
      
      await fetchUser();
      authResolved.value = true;
      return true;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed';
      clearSessionState();
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
      return true;
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
      authResolved.value = true;
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

  async function resendVerificationEmail(email) {
    loading.value = true;
    error.value = null;

    try {
      await authAPI.resendVerification(email);
      return true;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to resend verification email';
      return false;
    } finally {
      loading.value = false;
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

  async function resolveCurrentUser() {
    await fetchUser();
  }

  function startAuthResolution() {
    hydrateFromStorage();

    if (!hasToken.value) {
      authResolving.value = false;
      authResolved.value = true;
      return Promise.resolve(null);
    }

    if (authResolved.value && user.value) {
      return Promise.resolve(user.value);
    }

    if (authResolutionPromise) {
      return authResolutionPromise;
    }

    authResolving.value = true;

    authResolutionPromise = resolveCurrentUser()
      .catch(() => {
        error.value = null;
        return null;
      })
      .finally(() => {
        authResolving.value = false;
        authResolved.value = true;
        authResolutionPromise = null;
      });

    return authResolutionPromise;
  }

  function initialize() {
    hydrateFromStorage();
    return startAuthResolution();
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
    bootstrapped,
    authResolving,
    authResolved,
    hasToken,
    isAuthPending,
    role,
    isAuthenticated,
    isBusiness,
    isAdmin,
    isEmployee,
    shouldPromptForInterests,
    setTokens,
    hydrateFromStorage,
    startAuthResolution,
    resolveCurrentUser,
    setInterestsHandled,
    clearSessionState,
    login,
    register,
    fetchUser,
    logout,
    initialize,
    resendVerificationEmail,
  };
});
