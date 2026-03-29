import axios from 'axios'

export function isRequestCancelled(error) {
  return axios.isCancel(error) || error?.code === 'ERR_CANCELED' || error?.name === 'CanceledError'
}

export function normalizeApiError(error) {
  if (!error) {
    return {
      code: 'UNKNOWN_ERROR',
      message: 'Something went wrong.',
      fieldErrors: null,
      status: null,
      isCancelled: false,
      original: error,
    }
  }

  if (isRequestCancelled(error)) {
    return {
      code: 'REQUEST_CANCELLED',
      message: 'Request was cancelled.',
      fieldErrors: null,
      status: null,
      isCancelled: true,
      original: error,
    }
  }

  const status = error.response?.status ?? null
  const detail = error.response?.data?.detail
  const fieldErrors = error.response?.data?.errors ?? null
  const message = Array.isArray(detail) ? detail.join(', ') : detail || error.message || 'Request failed.'

  return {
    code: error.response?.data?.code || error.code || `HTTP_${status || 'ERROR'}`,
    message,
    fieldErrors,
    status,
    isCancelled: false,
    original: error,
  }
}
