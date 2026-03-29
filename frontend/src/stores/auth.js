import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { clearSessionTokens, hasSession, setSessionTokens } from '@/app/session'
import { authService } from '@/services/authService'
import { normalizeApiError } from '@/services/http/errors'
import { useFavouritesStore } from '@/stores/favourites'
import { getUserRole } from '@/utils/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref('')
  const initialized = ref(false)

  const isAuthenticated = computed(() => Boolean(user.value))
  const isBusiness = computed(() => user.value?.is_business || false)
  const isAdmin = computed(() => user.value?.is_super_admin || false)
  const role = computed(() => getUserRole(user.value))

  async function login(email, password) {
    const favouritesStore = useFavouritesStore()
    loading.value = true
    error.value = ''

    try {
      const { access_token: accessToken, refresh_token: refreshToken } = await authService.login({
        email,
        password,
      })

      setSessionTokens({ accessToken, refreshToken })
      await fetchUser()
      await favouritesStore.fetchAll(true)
      return true
    } catch (err) {
      error.value = normalizeApiError(err).message || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = ''

    try {
      await authService.register(userData)
      return await login(userData.email, userData.password)
    } catch (err) {
      error.value = normalizeApiError(err).message || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!hasSession()) {
      user.value = null
      return null
    }

    try {
      user.value = await authService.getCurrentUser()
      return user.value
    } catch {
      logout()
      return null
    }
  }

  function logout() {
    const favouritesStore = useFavouritesStore()
    clearSessionTokens()
    user.value = null
    error.value = ''
    favouritesStore.reset()
  }

  function handleSessionExpired() {
    logout()
    error.value = 'Your session has expired. Please sign in again.'
  }

  async function initialize() {
    if (initialized.value) {
      return
    }

    if (hasSession()) {
      await fetchUser()
    }

    initialized.value = true
  }

  return {
    user,
    loading,
    error,
    initialized,
    isAuthenticated,
    isBusiness,
    isAdmin,
    role,
    login,
    register,
    fetchUser,
    logout,
    handleSessionExpired,
    initialize,
  }
})
