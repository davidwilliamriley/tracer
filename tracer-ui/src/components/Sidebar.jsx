/**
 * Sidebar.jsx — left navigation sidebar.
 *
 * Uses React Router's NavLink which automatically adds an active class
 * when the current URL matches the link's path.
 */
import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

const NAV_ITEMS = [
  {
    section: 'Application',
    links: [
      { to: '/', label: 'Graph canvas', icon: '⬡', end: true },
    ],
  },
  {
    section: 'Admin',
    links: [
      { to: '/admin/node-types',            label: 'Node types',            icon: '◈' },
      { to: '/admin/edge-types',            label: 'Edge types',            icon: '→' },
      { to: '/admin/property-definitions',  label: 'Property definitions',  icon: '≡' },
      { to: '/admin/schema-editor',         label: 'Schema editor',         icon: '⚙' },
    ],
  },
]

export default function Sidebar() {
  const { user, logoutAction } = useAuthStore()

  return (
    <aside className="w-52 bg-white border-r border-gray-200 flex flex-col shrink-0 h-full">

      {/* Logo */}
      <div className="h-12 flex items-center px-4 border-b border-gray-200 shrink-0">
        <span className="text-sm font-semibold text-gray-900">Tracer</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {NAV_ITEMS.map((group) => (
          <div key={group.section} className="mb-5">
            <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider px-2 mb-1">
              {group.section}
            </div>
            {group.links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-2 py-1.5 rounded-lg text-sm transition-colors mb-0.5 ${
                    isActive
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                <span className="text-base leading-none w-4 text-center shrink-0">
                  {link.icon}
                </span>
                <span>{link.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* User / logout */}
      <div className="px-4 py-3 border-t border-gray-200 shrink-0">
        <div className="text-xs text-gray-500 mb-1">{user?.username}</div>
        <button
          onClick={logoutAction}
          className="text-xs text-gray-400 hover:text-gray-700 transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>
  )
}
