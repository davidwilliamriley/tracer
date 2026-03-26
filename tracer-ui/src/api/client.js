/**
 * client.js — base axios instance for all API calls.
 *
 * What this does:
 *   - Sets the base URL to /api (proxied to FastAPI by Vite in dev)
 *   - Attaches the Bearer token to every request automatically
 *   - Intercepts 401 responses, tries to refresh the token silently,
 *     then retries the original request — so the user is never logged
 *     out due to an expired access token mid-session
 *
 * React concept — why a module like this?
 *   In React you want to avoid duplicating logic. Rather than writing
 *   `axios.get('/api/node-types', { headers: { Authorization: ... } })`
 *   everywhere, you configure axios once here and every other file just
 *   calls `client.get('/node-types')`.
 */
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ---------------------------------------------------------------------------
// Request interceptor — attach token to every outgoing request
// ---------------------------------------------------------------------------
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ---------------------------------------------------------------------------
// Response interceptor — handle token expiry transparently
// ---------------------------------------------------------------------------
let isRefreshing = false
let failedQueue = []   // requests that arrived while a refresh was in progress

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Not a 401, or already retried — just reject
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    // Don't try to refresh if the failing request IS the refresh endpoint
    if (originalRequest.url === '/auth/refresh') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // If a refresh is already in progress, queue this request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return client(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      window.location.href = '/login'
      return Promise.reject(error)
    }

    try {
      const { data } = await client.post('/auth/refresh', {
        refresh_token: refreshToken,
      })
      localStorage.setItem('access_token', data.access_token)
      processQueue(null, data.access_token)
      originalRequest.headers.Authorization = `Bearer ${data.access_token}`
      return client(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default client
