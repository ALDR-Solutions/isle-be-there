import { httpClient } from '@/services/http/client'

export const businessesService = {
  async getAll(params = {}, options = {}) {
    const response = await httpClient.get('/api/businesses', { params, signal: options.signal })
    return response.data
  },
  async getById(id, options = {}) {
    const response = await httpClient.get(`/api/businesses/${id}`, { signal: options.signal })
    return response.data
  },
  async getMe(options = {}) {
    const response = await httpClient.get('/api/businesses/me', { signal: options.signal })
    return response.data
  },
  async update(id, payload) {
    const response = await httpClient.put(`/api/businesses/${id}`, payload)
    return response.data
  },
  async getListings(params = {}, options = {}) {
    const response = await httpClient.get('/api/businesses/listings', { params, signal: options.signal })
    return response.data
  },
  async getTypes(options = {}) {
    const response = await httpClient.get('/api/businesses/types', { signal: options.signal })
    return response.data
  },
}
