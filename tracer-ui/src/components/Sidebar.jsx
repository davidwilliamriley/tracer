import { NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { useAuthStore } from '../store/authStore'

const GRAPH_LINKS = [
  { to: '/', label: 'Graph canvas', icon: '⬡', end: true },
]

const ADMIN_LINKS = [
  { to: '/admin/node-types',           label: 'Node types',    icon: '◈' },
  { to: '/admin/edge-types',           label: 'Edge types',    icon: '→' },
  { to: '/admin/property-definitions', label: 'Properties',    icon: '≡' },
  { to: '/admin/schema-editor',        label: 'Schema',        icon: '⚙' },
  { to: '/admin/nodes',                label: 'Nodes',         icon: '○' },
  { to: '/admin/edges',                label: 'Edges',         icon: '—' },
]

const linkClass = ({ isActive }) =>
  `flex items-center gap-2.5 px-2 py-1.5 rounded-lg text-sm transition-colors mb-0.5 ${
    isActive
      ? 'bg-gray-900 text-white'
      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
  }`

export default function Sidebar() {
  const { user, logoutAction } = useAuthStore()
  const location = useLocation()
  const isAdmin = location.pathname.startsWith('/admin')
  const [tab, setTab] = useState(isAdmin ? 'admin' : 'graph')

  return (
    <aside className="w-52 bg-white border-r border-gray-200 flex flex-col shrink-0 h-full">
      {/* Logo */}
      <div className="h-12 flex items-center px-4 border-b border-gray-200 shrink-0">
        <span className="text-sm font-semibold text-gray-900">Tracer</span>
      </div>

      {/* Tab switcher */}
      <div className="flex border-b border-gray-200 shrink-0">
        {[['graph', 'Graph'], ['admin', 'Admin']].map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)}
            className={`flex-1 py-2 text-xs font-medium transition-colors ${
              tab === key
                ? 'border-b-2 border-gray-900 text-gray-900'
                : 'text-gray-400 hover:text-gray-600'
            }`}>
            {label}
          </button>
        ))}
      </div>

      {/* Nav links */}
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {(tab === 'graph' ? GRAPH_LINKS : ADMIN_LINKS).map((link) => (
          <NavLink key={link.to} to={link.to} end={link.end} className={linkClass}>
            <span className="text-base leading-none w-4 text-center shrink-0">{link.icon}</span>
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="px-4 py-3 border-t border-gray-200 shrink-0">
        <div className="text-xs text-gray-500 mb-1">{user?.username}</div>
        <button onClick={logoutAction}
          className="text-xs text-gray-400 hover:text-gray-700 transition-colors">
          Sign out
        </button>
      </div>
    </aside>
  )
}
