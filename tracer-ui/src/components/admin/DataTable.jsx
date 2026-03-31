import { DataTable as PrimeDataTable } from 'primereact/datatable'
import { Column } from 'primereact/column'

export default function DataTable({ columns, rows, actions, isLoading, error, emptyMessage = 'No records found' }) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
        Loading…
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="text-sm text-destructive bg-destructive/10 border border-destructive/30 rounded-lg px-4 py-3">
          {error}
        </div>
      </div>
    )
  }

  if (!rows || rows.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <PrimeDataTable
        value={rows}
        size="small"
        stripedRows
        dataKey="id"
        emptyMessage={emptyMessage}
        className="text-sm"
      >
        {columns.map((col) => (
          <Column
            key={col.key}
            field={col.key}
            header={col.label}
            body={(row) => (col.render ? col.render(row) : (row[col.key] ?? '—'))}
          />
        ))}
        {actions && (
          <Column
            header="Actions"
            body={(row) => actions(row)}
            bodyClassName="text-right"
            headerClassName="text-right"
            style={{ width: '1%' }}
          />
        )}
      </PrimeDataTable>
    </div>
  )
}
