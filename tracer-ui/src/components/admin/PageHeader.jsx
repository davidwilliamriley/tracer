/**
 * PageHeader.jsx — consistent page header for all admin pages.
 */
export default function PageHeader({ title, description, action }) {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shrink-0">
      <div>
        <h1 className="text-sm font-semibold text-gray-900">{title}</h1>
        {description && <p className="text-xs text-gray-400 mt-0.5">{description}</p>}
      </div>
      {action}
    </div>
  )
}
