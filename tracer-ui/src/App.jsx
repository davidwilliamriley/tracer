import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import ProtectedRoute from './components/ProtectedRoute'
import AppShell from './components/AppShell'
import Login from './pages/Login'
import Canvas from './pages/Canvas'
import NodeTypes from './pages/admin/NodeTypes'
import EdgeTypes from './pages/admin/EdgeTypes'
import PropertyDefinitions from './pages/admin/PropertyDefinitions'
import SchemaEditor from './pages/admin/SchemaEditor'

export default function App() {
  const { initAction } = useAuthStore()

  useEffect(() => {
    initAction()
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />

        {/* Protected — all inside the AppShell layout */}
        <Route
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route path="/"                            element={<Canvas />} />
          <Route path="/admin/node-types"            element={<NodeTypes />} />
          <Route path="/admin/edge-types"            element={<EdgeTypes />} />
          <Route path="/admin/property-definitions"  element={<PropertyDefinitions />} />
          <Route path="/admin/schema-editor"         element={<SchemaEditor />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
