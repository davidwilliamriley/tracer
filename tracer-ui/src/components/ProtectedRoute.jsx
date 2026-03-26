/**
 * ProtectedRoute.jsx — redirects unauthenticated users to /login.
 *
 * React concept — component composition:
 *   This component wraps other components. If the user is logged in,
 *   it renders whatever children were passed to it. If not, it redirects
 *   to /login. Wrap any route that requires auth with this component.
 *
 * Usage in App.jsx:
 *   <Route path="/" element={<ProtectedRoute><Canvas /></ProtectedRoute>} />
 */
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}
