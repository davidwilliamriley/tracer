/**
 * AppShell.jsx — shared layout for all authenticated pages.
 *
 * Renders the sidebar on the left and the current page's content
 * on the right. The Outlet component from React Router renders
 * whichever child route is currently active.
 *
 * React Router concept — nested routes:
 *   When you have a layout that wraps multiple pages, you define the
 *   layout as a parent route and the pages as children. The parent
 *   renders <Outlet /> where the children should appear.
 */
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function AppShell() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
