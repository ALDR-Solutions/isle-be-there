import { httpClient } from '@/services/http/client'

/**
 * @typedef {{
 *   email: string,
 *   password: string,
 *   username?: string | null,
 *   first_name?: string | null,
 *   last_name?: string | null,
 *   is_business?: boolean
 * }} RegisterPayload
 */

export const authService = {
  async register(payload) {
    const response = await httpClient.post('/api/auth/register', payload)
    return response.data
  },
  async login(credentials) {
    const formData = new URLSearchParams()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)

    const response = await httpClient.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })

    return response.data
  },
  async getCurrentUser() {
    const response = await httpClient.get('/api/auth/me')
    return response.data
  },
  async disableAccount() {
    const response = await httpClient.delete('/api/auth/me')
    return response.data
  },
}
