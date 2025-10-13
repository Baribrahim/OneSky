import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

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

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

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
