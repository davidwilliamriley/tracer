/**
 * auth.js — functions that call the authentication endpoints.
 *
 * Note: login uses axios directly (not the client instance) because
 * the client's interceptor redirects to /login on 401 — which would
 * cause an infinite loop if the login request itself gets a 401.
 */
import axios from 'axios'
import client from './client'

export async function login(username, password) {
  // OAuth2 form data — must be sent as application/x-www-form-urlencoded
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)

  const { data } = await axios.post('/api/auth/token', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })

  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)

  return data
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function getMe() {
  const { data } = await client.get('/auth/me')
  return data
}

export function isLoggedIn() {
  return !!localStorage.getItem('access_token')
}
