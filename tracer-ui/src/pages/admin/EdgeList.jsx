import { useState, useEffect, useCallback } from 'react'
import { getEdges, getEdgeTypes } from '../../api/graph'
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

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
      <div className="flex gap-3 px-6 py-3 border-b border-border bg-card shrink-0">
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-40 text-xs h-8">
            <SelectValue placeholder="All types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All types</SelectItem>
            {types.map((t) => (
              <SelectItem key={t.id} value={t.edge_type_identifier}>{t.edge_type_name}</SelectItem>
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
          <Table>
            <TableHeader>
              <TableRow>
                {['Type', 'Identifier', 'Name', 'Created'].map((h) => (
                  <TableHead key={h}>{h}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border border-border bg-secondary text-secondary-foreground">
                      {row.edge_type?.edge_type_identifier || '—'}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs font-mono text-muted-foreground">{row.edge_identifier}</TableCell>
                  <TableCell className="text-xs">{row.edge_name}</TableCell>
                  <TableCell className="text-xs text-muted-foreground">{row.created_on?.slice(0, 10)}</TableCell>
                </TableRow>
              ))}
              {rows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground py-8">No edges found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </div>

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
