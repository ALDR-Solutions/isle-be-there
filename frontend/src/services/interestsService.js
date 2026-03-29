import { httpClient } from '@/services/http/client'

export const interestsService = {
  async getAll(options = {}) {
    const response = await httpClient.get('/api/interests', { signal: options.signal })
    return response.data
  },
  async updateUserInterests(interestIds) {
    const response = await httpClient.put('/api/interests/user', { interest_ids: interestIds })
    return response.data
  },
}
