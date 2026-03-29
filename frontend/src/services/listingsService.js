import { httpClient } from '@/services/http/client'

export const listingsService = {
  async getAll(params = {}, options = {}) {
    const response = await httpClient.get('/api/listings', { params, signal: options.signal })
    return response.data
  },
  async getById(id, options = {}) {
    const response = await httpClient.get(`/api/listings/${id}`, { signal: options.signal })
    return response.data
  },
  async create(payload) {
    const response = await httpClient.post('/api/listings', payload)
    return response.data
  },
  async update(id, payload) {
    const response = await httpClient.put(`/api/listings/${id}`, payload)
    return response.data
  },
  async delete(id) {
    const response = await httpClient.delete(`/api/listings/${id}`)
    return response.data
  },
  async getPersonalized(params = {}, options = {}) {
    const response = await httpClient.get('/api/listings/personalized', { params, signal: options.signal })
    return response.data
  },
}
