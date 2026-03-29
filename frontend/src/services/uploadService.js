import { httpClient } from '@/services/http/client'

export const uploadService = {
  async uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await httpClient.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    return response.data
  },
}
