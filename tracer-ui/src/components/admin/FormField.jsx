/**
 * FormField.jsx — labelled form field used across all admin forms.
 */
export default function FormField({ label, required, hint, error, children }) {
  return (
    <div className="mb-4">
      <label className="flex items-center gap-1.5 text-xs font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500 text-[10px]">required</span>}
      </label>
      {hint && <p className="text-[11px] text-gray-400 mb-1">{hint}</p>}
      {children}
      {error && <p className="text-[11px] text-red-500 mt-1">{error}</p>}
    </div>
  )
}

/**
 * Styled input and select components to keep admin forms consistent.
 */
export function TextInput({ value, onChange, placeholder, required, disabled }) {
  return (
    <input
      type="text"
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      required={required}
      disabled={disabled}
      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg
                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 disabled:bg-gray-50 disabled:text-gray-400"
    />
  )
}

export function TextArea({ value, onChange, placeholder, rows = 3 }) {
  return (
    <textarea
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      rows={rows}
      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg
                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 resize-none"
    />
  )
}

export function SelectInput({ value, onChange, options, required }) {
  return (
    <select
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      required={required}
      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg
                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 bg-white"
    >
      <option value="">Select…</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  )
}

export function Toggle({ checked, onChange, label }) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <div className="relative">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="sr-only"
        />
        <div className={`w-8 h-4 rounded-full transition-colors ${checked ? 'bg-blue-600' : 'bg-gray-300'}`} />
        <div className={`absolute top-0.5 w-3 h-3 bg-white rounded-full shadow transition-transform ${checked ? 'translate-x-4.5 left-0.5' : 'left-0.5'}`} />
      </div>
      {label && <span className="text-xs text-gray-700">{label}</span>}
    </label>
  )
}
