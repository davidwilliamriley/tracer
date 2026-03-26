/**
 * DataTable.jsx — generic table for admin list pages.
 *
 * Props:
 *   columns: [{ key, label, render? }]
 *   rows:    array of data objects
 *   actions: optional render function receiving a row → JSX action buttons
 *   isLoading, error, emptyMessage
 */
export default function DataTable({ columns, rows, actions, isLoading, error, emptyMessage = 'No records found' }) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-400">
        Loading…
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error}
        </div>
      </div>
    )
  }

  if (!rows || rows.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-400">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            {columns.map((col) => (
              <th
                key={col.key}
                className="text-left text-xs font-medium text-gray-500 px-4 py-3"
              >
                {col.label}
              </th>
            ))}
            {actions && (
              <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">
                Actions
              </th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((row, i) => (
            <tr key={row.id ?? i} className="hover:bg-gray-50 transition-colors">
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3 text-gray-700">
                  {col.render ? col.render(row) : (row[col.key] ?? '—')}
                </td>
              ))}
              {actions && (
                <td className="px-4 py-3 text-right">
                  {actions(row)}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
