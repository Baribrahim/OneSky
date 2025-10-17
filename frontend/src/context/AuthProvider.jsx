import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, setAuthToken, toResult } from "../lib/apiClient";

const AuthContext = createContext(null);

const TOKEN_KEY = "onesky_token";


/**
 * AuthProvider
 * Provides authentication state (user, token, login/logout/register)
 * across the entire frontend via Context.
 *
 *  - Store and restore JWT token from localStorage
 *  - Expose helper functions for login, registration, logout
 *  - Fetch and hold the current user's profile (/api/me)
 *  - Handle token persistence and Axios header setup
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  /**
   * On app mount:
   * 1. Check if token exists in localStorage
   * 2. If yes, attach it to API client and fetch user data
   * 3. Otherwise, mark as not authenticated
   */
  useEffect(() => {
    const saved = window.localStorage.getItem(TOKEN_KEY);
    if (saved) {
      setAuthToken(saved);
      loadUser().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);


  /**
   * Fetches the current user info using /api/me
   * - Returns user data if token is valid
   * - Clears user state if invalid/expired
   */
  const loadUser = useCallback(async () => {
    const { data, error } = await toResult(api.get("/api/me"));
    if (!error && data) {
      setUser(data);
      return data;
    }
    setUser(null);
    return null;
  }, []);

  /**
   * Login flow:
   * 1. POST credentials to backend
   * 2. Store returned token in localStorage
   * 3. Update axios headers for subsequent requests
   * 4. Fetch user profile via loadUser()
   */
  const login = useCallback(async (email, password) => {
    const { data, error } = await toResult(api.post("/login", { email, password }));
    if (error) return { data: null, error };

    const token = data?.token || data;
    window.localStorage.setItem(TOKEN_KEY, token);
    setAuthToken(token);
    const me = await loadUser();
    return { data: { token, user: me }, error: null };
  }, [loadUser]);

  /**
   * Register flow:
   * 1. POST registration payload to backend
   * 2. Store token, update axios header, and fetch user
   * (mirrors login flow)
   */
  const register = useCallback(async (payload) => {
    const { data, error } = await toResult(api.post("/register", payload));
    if (error) return { data: null, error };

    const token = data?.token || data;
    window.localStorage.setItem(TOKEN_KEY, token);
    setAuthToken(token);
    const me = await loadUser();
    return { data: { token, user: me }, error: null };
  }, [loadUser]);

  /**
   * Logout flow:
   * - Remove token from localStorage
   * - Clear axios Authorization header
   * - Reset user state
   */
  const logout = useCallback(() => {
    window.localStorage.removeItem(TOKEN_KEY);
    setAuthToken(null);
    setUser(null);
  }, []);

  /**
   * Prevents re-renders in all consuming components unless auth state changes.
   */
  const value = useMemo(() => ({
    user,
    isAuthenticated: !!user,
    loading,
    login,
    register,
    logout,
    loadUser,
  }), [user, loading, login, register, logout, loadUser]);

  // Provide the value to all children (pages/components)
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Custom hook for accessing the AuthContext.
 */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
