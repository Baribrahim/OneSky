import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
console.log("API_BASE_URL:", API_BASE_URL);

if (!API_BASE_URL) {
  console.warn("VITE_API_BASE_URL is not set. Check your .env.");
}

/**
 * Single axios instance for the whole app.
 * - Attaches Authorization header when a token exists
 * - Normalizes error handling
 */
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

// Token holder
let authToken = null;

export function setAuthToken(token) {
  authToken = token || null;
}

export function getAuthToken() {
  return authToken;
}

/**
 * Request interceptor
 * Automatically attaches the `Authorization: Bearer <token>` header
 * before each API call if a token exists.
 *
 * This ensures all protected routes work once the user logs in.
 */
api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

api.defaults.withCredentials = true;

// Normalization helper that converts a promise into a {data, error} object
export function toResult(promise) {
  return promise
    .then((res) => ({ data: res.data?.data ?? res.data ?? null, error: null }))
    .catch((err) => {
      const message =
        err.response?.data?.error?.message ||
        err.response?.data?.error ||
        err.response?.data ||
        err.message ||
        "Request failed";

      const code = err.response?.status || "REQUEST_ERROR";
      return { data: null, error: { code, message } };
    });
}
