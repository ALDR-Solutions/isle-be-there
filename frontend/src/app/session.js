const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

function readStorage(key) {
  if (typeof window === 'undefined') {
    return null
  }

  return window.localStorage.getItem(key)
}

function writeStorage(key, value) {
  if (typeof window === 'undefined') {
    return
  }

  if (!value) {
    window.localStorage.removeItem(key)
    return
  }

  window.localStorage.setItem(key, value)
}

export function getAccessToken() {
  return readStorage(ACCESS_TOKEN_KEY)
}

export function getRefreshToken() {
  return readStorage(REFRESH_TOKEN_KEY)
}

export function setSessionTokens({ accessToken, refreshToken }) {
  writeStorage(ACCESS_TOKEN_KEY, accessToken)
  writeStorage(REFRESH_TOKEN_KEY, refreshToken)
}

export function clearSessionTokens() {
  writeStorage(ACCESS_TOKEN_KEY, null)
  writeStorage(REFRESH_TOKEN_KEY, null)
}

export function hasSession() {
  return Boolean(getAccessToken())
}
