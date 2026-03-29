import { httpClient } from '@/services/http/client'

export const reviewsService = {
  async getAll(params = {}, options = {}) {
    const response = await httpClient.get('/api/reviews', { params, signal: options.signal })
    return response.data
  },
  async create(payload) {
    const response = await httpClient.post('/api/reviews', payload)
    return response.data
  },
}
