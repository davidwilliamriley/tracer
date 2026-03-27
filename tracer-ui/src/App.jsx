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
import NodeList from './pages/admin/NodeList'
import EdgeList from './pages/admin/EdgeList'

export default function App() {
  const { initAction } = useAuthStore()
  useEffect(() => { initAction() }, [])

  return (
    <BrowserRouter>
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
    </BrowserRouter>
  )
}
