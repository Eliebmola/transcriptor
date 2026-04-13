import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { fetchJson, fetchWithToken } from "../lib/api";

const TOKEN_KEY = "transcriptor-token";
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || "");
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    if (!token) {
      localStorage.removeItem(TOKEN_KEY);
      setUser(null);
      setAuthReady(true);
      return;
    }

    localStorage.setItem(TOKEN_KEY, token);
    void refreshMe(token);
  }, [token]);

  async function refreshMe(activeToken = token) {
    if (!activeToken) {
      setUser(null);
      setAuthReady(true);
      return null;
    }

    try {
      const payload = await fetchWithToken("/api/auth/me/", activeToken);
      setUser(payload);
      setAuthReady(true);
      return payload;
    } catch (error) {
      setToken("");
      setUser(null);
      setAuthReady(true);
      throw error;
    }
  }

  async function login(username, password) {
    setAuthLoading(true);
    try {
      const payload = await fetchJson("/api/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      setToken(payload.token);
      setUser(payload.user);
      return payload;
    } finally {
      setAuthLoading(false);
    }
  }

  async function register(username, email, password) {
    setAuthLoading(true);
    try {
      const payload = await fetchJson("/api/auth/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
      setToken(payload.token);
      setUser(payload.user);
      return payload;
    } finally {
      setAuthLoading(false);
    }
  }

  function logout() {
    setToken("");
    setUser(null);
    setAuthReady(true);
  }

  const value = useMemo(
    () => ({
      token,
      user,
      authLoading,
      authReady,
      isAuthenticated: Boolean(token),
      login,
      register,
      logout,
      refreshMe,
    }),
    [token, user, authLoading, authReady],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de AuthProvider.");
  }
  return context;
}
