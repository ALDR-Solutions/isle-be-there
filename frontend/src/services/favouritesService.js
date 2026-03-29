import { httpClient } from '@/services/http/client'

export const favouritesService = {
  async getAll(options = {}) {
    const response = await httpClient.get('/api/favourites', { signal: options.signal })
    return response.data
  },
  async add(listingId) {
    const response = await httpClient.post(`/api/favourites/${listingId}`)
    return response.data
  },
  async remove(listingId) {
    const response = await httpClient.delete(`/api/favourites/${listingId}`)
    return response.data
  },
}
