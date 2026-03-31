import { useState, useEffect, useCallback } from 'react'
import { getNodes, getNodeTypes } from '../../api/graph'
import { colourForType } from '../../utils/layout'
import PageHeader from '../../components/admin/PageHeader'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DataTable } from 'primereact/datatable'
import { Column } from 'primereact/column'

export default function NodeList() {
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
    getNodeTypes().then((d) => setTypes(d.items || d)).catch(() => {})
  }, [])

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const params = { skip: page * LIMIT, limit: LIMIT }
      if (typeFilter) params.node_type_identifier = typeFilter
      if (nameFilter) params.name_contains = nameFilter
      const data = await getNodes(params)
      setRows(data.items)
      setTotal(data.total)
    } catch (e) {
      setError(e.response?.data?.message || 'Failed to load')
    } finally {
      setLoading(false)
    }
  }, [page, typeFilter, nameFilter])

  useEffect(() => { load() }, [load])
  useEffect(() => { setPage(0) }, [typeFilter, nameFilter])

  const typeBody = (row) => {
    const c = colourForType(row.node_type?.node_type_identifier)
    return (
      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border"
        style={{ background: c.bg, borderColor: c.border, color: c.text }}>
        {row.node_type?.node_type_identifier || '—'}
      </span>
    )
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <PageHeader title="Nodes" description={`${total} nodes in the graph`} />

      {/* Filters */}
      <div className="flex gap-3 px-6 py-3 border-b border-border bg-card shrink-0">
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-40 text-xs h-8">
            <SelectValue placeholder="All types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All types</SelectItem>
            {types.map((t) => (
              <SelectItem key={t.id} value={t.node_type_identifier}>{t.node_type_name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input
          type="text"
          value={nameFilter}
          onChange={(e) => setNameFilter(e.target.value)}
          placeholder="Search by name…"
          className="text-xs h-8 flex-1"
        />
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto bg-card">
        {isLoading && (
          <div className="flex items-center justify-center h-32 text-sm text-muted-foreground">Loading…</div>
        )}
        {error && (
          <div className="m-6 text-xs text-destructive bg-destructive/10 border border-destructive/30 rounded-lg p-3">{error}</div>
        )}
        {!isLoading && !error && (
          <DataTable value={rows} dataKey="id" size="small" stripedRows emptyMessage="No nodes found">
            <Column header="Type" body={typeBody} />
            <Column field="node_identifier" header="Identifier" bodyClassName="text-xs font-mono text-muted-foreground" />
            <Column field="node_name" header="Name" bodyClassName="text-xs" />
            <Column header="Created" body={(row) => row.created_on?.slice(0, 10)} bodyClassName="text-xs text-muted-foreground" />
          </DataTable>
        )}
      </div>

      {/* Pagination */}
      {total > LIMIT && (
        <div className="flex items-center justify-between px-6 py-3 border-t border-border bg-card shrink-0">
          <span className="text-xs text-muted-foreground">
            {page * LIMIT + 1}–{Math.min((page + 1) * LIMIT, total)} of {total}
          </span>
          <div className="flex gap-2">
            <Button variant="outline" size="xs" onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}>
              ← Prev
            </Button>
            <Button variant="outline" size="xs" onClick={() => setPage(p => p + 1)} disabled={(page + 1) * LIMIT >= total}>
              Next →
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
