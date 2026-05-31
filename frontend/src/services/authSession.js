const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

function getStorage() {
  return typeof window !== "undefined" ? window.localStorage : null;
}

export function readStoredTokens() {
  const storage = getStorage();
  if (!storage) {
    return { accessToken: null, refreshToken: null };
  }

  return {
    accessToken: storage.getItem(ACCESS_TOKEN_KEY),
    refreshToken: storage.getItem(REFRESH_TOKEN_KEY),
  };
}

export function writeStoredTokens({
  accessToken = null,
  refreshToken = null,
} = {}) {
  const storage = getStorage();
  if (!storage) {
    return;
  }

  if (accessToken) {
    storage.setItem(ACCESS_TOKEN_KEY, accessToken);
  } else {
    storage.removeItem(ACCESS_TOKEN_KEY);
  }

  if (refreshToken) {
    storage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  } else {
    storage.removeItem(REFRESH_TOKEN_KEY);
  }
}
