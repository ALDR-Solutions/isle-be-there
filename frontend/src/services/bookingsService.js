import { httpClient } from '@/services/http/client'

export const bookingsService = {
  async getAll(params = {}, options = {}) {
    const response = await httpClient.get('/api/bookings', { params, signal: options.signal })
    return response.data
  },
  async cancel(id) {
    const response = await httpClient.delete(`/api/bookings/${id}`)
    return response.data
  },
}
