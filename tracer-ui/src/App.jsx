import { useEffect, lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import ProtectedRoute from './components/ProtectedRoute'
import AppShell from './components/AppShell'

const Login               = lazy(() => import('./pages/Login'))
const Canvas              = lazy(() => import('./pages/Canvas'))
const NodeTypes           = lazy(() => import('./pages/admin/NodeTypes'))
const EdgeTypes           = lazy(() => import('./pages/admin/EdgeTypes'))
const PropertyDefinitions = lazy(() => import('./pages/admin/PropertyDefinitions'))
const SchemaEditor        = lazy(() => import('./pages/admin/SchemaEditor'))
const NodeList            = lazy(() => import('./pages/admin/NodeList'))
const EdgeList            = lazy(() => import('./pages/admin/EdgeList'))

export default function App() {
  const { initAction } = useAuthStore()
  useEffect(() => { initAction() }, [])

  return (
    <BrowserRouter>
      <Suspense fallback={<div className="flex items-center justify-center h-screen text-sm text-gray-400">Loading…</div>}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
            <Route path="/"                           element={<Canvas />} />
            <Route path="/admin/node-types"           element={<NodeTypes />} />
            <Route path="/admin/edge-types"           element={<EdgeTypes />} />
            <Route path="/admin/property-definitions" element={<PropertyDefinitions />} />
            <Route path="/admin/schema-editor"        element={<SchemaEditor />} />
            <Route path="/admin/nodes"                element={<NodeList />} />
            <Route path="/admin/edges"                element={<EdgeList />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
