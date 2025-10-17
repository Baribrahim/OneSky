import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, setAuthToken, toResult } from "../lib/apiClient";

const AuthContext = createContext(null);

const TOKEN_KEY = "onesky_token";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = window.localStorage.getItem(TOKEN_KEY);
    if (saved) {
      setAuthToken(saved);
      loadUser().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const loadUser = useCallback(async () => {
    const { data, error } = await toResult(api.get("/api/me"));
    if (!error && data) {
      setUser(data);
      return data;
    }
    setUser(null);
    return null;
  }, []);

  const login = useCallback(async (email, password) => {
    const { data, error } = await toResult(api.post("/login", { email, password }));
    if (error) return { data: null, error };

    const token = data?.token || data;
    window.localStorage.setItem(TOKEN_KEY, token);
    setAuthToken(token);
    const me = await loadUser();
    return { data: { token, user: me }, error: null };
  }, [loadUser]);

  const register = useCallback(async (payload) => {
    const { data, error } = await toResult(api.post("/register", payload));
    if (error) return { data: null, error };

    const token = data?.token || data;
    window.localStorage.setItem(TOKEN_KEY, token);
    setAuthToken(token);
    const me = await loadUser();
    return { data: { token, user: me }, error: null };
  }, [loadUser]);

  const logout = useCallback(() => {
    window.localStorage.removeItem(TOKEN_KEY);
    setAuthToken(null);
    setUser(null);
  }, []);

  const value = useMemo(() => ({
    user,
    isAuthenticated: !!user,
    loading,
    login,
    register,
    logout,
    loadUser,
  }), [user, loading, login, register, logout, loadUser]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
