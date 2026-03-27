/**
 * EdgeList.jsx — browse all edges with filtering by type.
 */
import { useState, useEffect, useCallback } from 'react'
import { getEdges, getEdgeTypes } from '../../api/graph'
import PageHeader from '../../components/admin/PageHeader'

export default function EdgeList() {
  const [rows, setRows]           = useState([])
  const [types, setTypes]         = useState([])
  const [total, setTotal]         = useState(0)
  const [isLoading, setLoading]   = useState(true)
  const [error, setError]         = useState(null)
  const [typeFilter, setTypeFilter] = useState('')
  const [nameFilter, setNameFilter] = useState('')
  const [page, setPage]           = useState(0)
  const LIMIT = 25

  useEffect(() => {
    getEdgeTypes().then((d) => setTypes(d.items || d)).catch(() => {})
  }, [])

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const params = { skip: page * LIMIT, limit: LIMIT }
      if (typeFilter) params.edge_type_identifier = typeFilter
      if (nameFilter) params.name_contains = nameFilter
      const data = await getEdges(params)
      setRows(data.items)
      setTotal(data.total)
    } catch (e) {
      setError(e.response?.data?.message || 'Failed to load')
    } finally { setLoading(false) }
  }, [page, typeFilter, nameFilter])

  useEffect(() => { load() }, [load])
  useEffect(() => { setPage(0) }, [typeFilter, nameFilter])

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <PageHeader title="Edges" description={`${total} edges in the graph`} />

      {/* Filters */}
      <div className="flex gap-3 px-6 py-3 border-b border-gray-100 bg-white shrink-0">
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
          className="px-3 py-1.5 text-xs border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All types</option>
          {types.map((t) => (
            <option key={t.id} value={t.edge_type_identifier}>{t.edge_type_name}</option>
          ))}
        </select>
        <input type="text" value={nameFilter} onChange={(e) => setNameFilter(e.target.value)}
          placeholder="Search by name…"
          className="px-3 py-1.5 text-xs border border-gray-200 rounded-lg flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto bg-white">
        {isLoading && (
          <div className="flex items-center justify-center h-32 text-sm text-gray-400">Loading…</div>
        )}
        {error && (
          <div className="m-6 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">{error}</div>
        )}
        {!isLoading && !error && (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                {['Type', 'Identifier', 'Name', 'Created'].map((h) => (
                  <th key={h} className="text-left text-xs font-medium text-gray-500 px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {rows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border border-gray-200 bg-gray-50 text-gray-600">
                      {row.edge_type?.edge_type_identifier || '—'}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-xs font-mono text-gray-600">{row.edge_identifier}</td>
                  <td className="px-4 py-2.5 text-xs text-gray-900">{row.edge_name}</td>
                  <td className="px-4 py-2.5 text-xs text-gray-500">{row.created_on?.slice(0, 10)}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-sm text-gray-400">No edges found</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {total > LIMIT && (
        <div className="flex items-center justify-between px-6 py-3 border-t border-gray-200 bg-white shrink-0">
          <span className="text-xs text-gray-500">
            {page * LIMIT + 1}–{Math.min((page + 1) * LIMIT, total)} of {total}
          </span>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
              className="px-3 py-1 text-xs border border-gray-200 rounded-lg disabled:opacity-40 hover:bg-gray-50">
              ← Prev
            </button>
            <button onClick={() => setPage(p => p + 1)} disabled={(page + 1) * LIMIT >= total}
              className="px-3 py-1 text-xs border border-gray-200 rounded-lg disabled:opacity-40 hover:bg-gray-50">
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
