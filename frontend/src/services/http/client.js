import axios from 'axios'
import { clearSessionTokens, getAccessToken, getRefreshToken, setSessionTokens } from '@/app/session'
import { normalizeApiError } from '@/services/http/errors'

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

let refreshRequest = null

function redirectToLogin() {
  if (typeof window === 'undefined') {
    return
  }

  if (window.location.pathname !== '/login') {
    window.location.assign('/login')
  }
}

async function refreshTokens() {
  if (!refreshRequest) {
    const refreshToken = getRefreshToken()

    if (!refreshToken) {
      throw normalizeApiError({ message: 'Missing refresh token.' })
    }

    refreshRequest = axios
      .post(`${API_BASE_URL}/api/auth/refresh`, { refresh_token: refreshToken })
      .then((response) => {
        const { access_token: accessToken, refresh_token: nextRefreshToken } = response.data
        setSessionTokens({ accessToken, refreshToken: nextRefreshToken })
        return accessToken
      })
      .finally(() => {
        refreshRequest = null
      })
  }

  return refreshRequest
}

export const httpClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

httpClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken()

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(normalizeApiError(error))
)

httpClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {}
    const requestUrl = String(originalRequest.url || '')
    const isAuthRoute =
      requestUrl.includes('/api/auth/login') ||
      requestUrl.includes('/api/auth/register') ||
      requestUrl.includes('/api/auth/refresh')

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthRoute) {
      originalRequest._retry = true

      try {
        const accessToken = await refreshTokens()
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${accessToken}`
        return httpClient(originalRequest)
      } catch (refreshError) {
        clearSessionTokens()
        redirectToLogin()
        return Promise.reject(normalizeApiError(refreshError))
      }
    }

    return Promise.reject(normalizeApiError(error))
  }
)
