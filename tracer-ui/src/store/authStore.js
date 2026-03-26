/**
 * authStore.js — global authentication state using Zustand.
 *
 * React concept — why a store?
 *   React components have their own local state (useState), but some
 *   state needs to be shared across many components — like "is the user
 *   logged in?" You could pass it down as props, but that gets messy.
 *   Zustand is a minimal store that any component can read from or write
 *   to directly, without prop-drilling.
 *
 * Usage in any component:
 *   import { useAuthStore } from '../store/authStore'
 *   const { user, isAuthenticated, loginAction } = useAuthStore()
 */
import { create } from 'zustand'
import { login, logout, getMe, isLoggedIn } from '../api/auth'

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: isLoggedIn(),
  isLoading: false,
  error: null,

  // Called when the user submits the login form
  loginAction: async (username, password) => {
    set({ isLoading: true, error: null })
    try {
      await login(username, password)
      const user = await getMe()
      set({ user, isAuthenticated: true, isLoading: false })
      return true
    } catch (err) {
      const message = err.response?.data?.message || 'Login failed'
      set({ error: message, isLoading: false })
      return false
    }
  },

  // Called when the user clicks logout
  logoutAction: () => {
    logout()
    set({ user: null, isAuthenticated: false })
  },

  // Called on app startup to restore session from localStorage
  initAction: async () => {
    if (!isLoggedIn()) return
    try {
      const user = await getMe()
      set({ user, isAuthenticated: true })
    } catch {
      logout()
      set({ user: null, isAuthenticated: false })
    }
  },
}))
