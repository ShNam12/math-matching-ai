const TOKEN_KEY = "ai_matching_access_token";
const USER_KEY = "ai_matching_current_user";

export function getStoredAuthSession() {
  const accessToken = localStorage.getItem(TOKEN_KEY);
  const storedUser = localStorage.getItem(USER_KEY);

  if (!accessToken || !storedUser) {
    return null;
  }

  try {
    return {
      accessToken,
      user: JSON.parse(storedUser),
    };
  } catch {
    clearStoredAuthSession();
    return null;
  }
}

export function storeAuthSession({ accessToken, user }) {
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearStoredAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

