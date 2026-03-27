/**
 * SubTabs.jsx — horizontal sub-tab bar used inside admin pages.
 */
export default function SubTabs({ tabs, active, onChange }) {
  return (
    <div className="flex gap-1 px-6 py-2 border-b border-gray-100 bg-white shrink-0">
      {tabs.map(({ key, label }) => (
        <button key={key} onClick={() => onChange(key)}
          className={`px-3 py-1.5 text-xs rounded-md border transition-colors ${
            active === key
              ? 'bg-gray-900 text-white border-gray-900'
              : 'text-gray-500 border-gray-200 hover:border-gray-300'
          }`}>
          {label}
        </button>
      ))}
    </div>
  )
}
