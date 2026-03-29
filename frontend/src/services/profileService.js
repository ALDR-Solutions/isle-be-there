import { httpClient } from '@/services/http/client'

export const profileService = {
  async get(options = {}) {
    const response = await httpClient.get('/api/profile', { signal: options.signal })
    return response.data
  },
  async update(payload) {
    const response = await httpClient.put('/api/profile', payload)
    return response.data?.profile ?? response.data
  },
  async setInterestsHandled() {
    const response = await httpClient.patch('/api/profile/interests-handled')
    return response.data
  },
}
