import { useState, useEffect } from 'react'
import {
  getNodeTypes, getEdgeTypes,
  getNodePropertyDefinitions, getEdgePropertyDefinitions,
  getAssignmentsByNodeType, getAssignmentsByEdgeType,
  createNodeTypeAssignment, createEdgeTypeAssignment,
  updateNodeTypeAssignment, updateEdgeTypeAssignment,
  deleteNodeTypeAssignment, deleteEdgeTypeAssignment,
} from '../../api/admin'
import ConfirmDialog from '../../components/admin/ConfirmDialog'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

function AssignmentRow({ assignment, onUpdate, onRemove }) {
  const [isRequired, setIsRequired]   = useState(assignment.is_required)
  const [defaultValue, setDefault]    = useState(assignment.default_value ?? '')
  const [sortOrder, setSortOrder]     = useState(assignment.sort_order)
  const [isSaving, setIsSaving]       = useState(false)

  const save = async (patch) => {
    setIsSaving(true)
    try { await onUpdate(assignment.id, patch) }
    finally { setIsSaving(false) }
  }

  return (
    <div className="flex items-center gap-3 px-4 py-3 border-b border-border last:border-0 hover:bg-accent/50">
      <input type="number" value={sortOrder} min={0} step={1}
        onChange={(e) => setSortOrder(Number(e.target.value))}
        onBlur={() => save({ sort_order: sortOrder })}
        className="w-14 px-2 py-1 text-xs border border-input rounded text-center focus:outline-none focus:ring-1 focus:ring-ring bg-background"
        title="Sort order"
      />

      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium text-foreground truncate">
          {assignment.node_property_definition?.node_property_definition_name
          ?? assignment.edge_property_definition?.edge_property_definition_name
          ?? assignment.node_property_definition_id_fk?.slice(0, 8)
          ?? '—'}
        </div>
        <div className="text-[10px] text-muted-foreground">
          {assignment.node_property_definition?.node_property_definition_type
          ?? assignment.edge_property_definition?.edge_property_definition_type
          ?? ''}
        </div>
      </div>

      <label className="flex items-center gap-1 cursor-pointer shrink-0">
        <input type="checkbox" checked={isRequired}
          onChange={(e) => { setIsRequired(e.target.checked); save({ is_required: e.target.checked }) }}
          className="w-3 h-3 rounded border-input text-primary focus:ring-ring"
        />
        <span className="text-[10px] text-muted-foreground">Required</span>
      </label>

      <input type="text" value={defaultValue} placeholder="default…"
        onChange={(e) => setDefault(e.target.value)}
        onBlur={() => save({ default_value: defaultValue || null })}
        className="w-24 px-2 py-1 text-xs border border-input rounded focus:outline-none focus:ring-1 focus:ring-ring bg-background"
        title="Default value for this type (overrides definition default)"
      />

      <button onClick={onRemove} className="text-muted-foreground hover:text-destructive transition-colors text-sm shrink-0" title="Remove assignment">
        ✕
      </button>

      {isSaving && <span className="text-[10px] text-primary shrink-0">saving…</span>}
    </div>
  )
}

export default function SchemaEditor() {
  const [entityType, setEntityType] = useState('node')
  const [types, setTypes]           = useState([])
  const [selectedType, setSelectedType] = useState(null)
  const [assignments, setAssignments]   = useState([])
  const [allDefs, setAllDefs]           = useState([])
  const [isLoading, setIsLoading]       = useState(false)
  const [removeTarget, setRemoveTarget] = useState(null)
  const [removeLoading, setRemoveLoading] = useState(false)
  const [addDefId, setAddDefId]         = useState('')
  const [isAdding, setIsAdding]         = useState(false)

  useEffect(() => {
    setSelectedType(null)
    setAssignments([])
    const fn = entityType === 'node' ? getNodeTypes : getEdgeTypes
    fn().then(setTypes).catch(() => setTypes([]))
  }, [entityType])

  useEffect(() => {
    if (!selectedType) return
    setIsLoading(true)
    const assignFn = entityType === 'node' ? getAssignmentsByNodeType : getAssignmentsByEdgeType
    const defFn    = entityType === 'node' ? getNodePropertyDefinitions : getEdgePropertyDefinitions
    Promise.all([assignFn(selectedType.id), defFn()])
      .then(([a, d]) => { setAssignments(a); setAllDefs(d) })
      .finally(() => setIsLoading(false))
  }, [selectedType, entityType])

  const assignedDefIds = new Set(
    assignments.map((a) =>
      String(a.node_property_definition_id_fk ?? a.edge_property_definition_id_fk)
    )
  )
  const availableDefs = allDefs.filter((d) => !assignedDefIds.has(String(d.id)))

  const reloadAssignments = () => {
    if (!selectedType) return
    const fn = entityType === 'node' ? getAssignmentsByNodeType : getAssignmentsByEdgeType
    fn(selectedType.id).then(setAssignments)
  }

  const handleAdd = async () => {
    if (!addDefId || !selectedType) return
    setIsAdding(true)
    try {
      const payload = entityType === 'node'
        ? { node_type_id_fk: selectedType.id, node_property_definition_id_fk: addDefId, is_required: false, sort_order: assignments.length }
        : { edge_type_id_fk: selectedType.id, edge_property_definition_id_fk: addDefId, is_required: false, sort_order: assignments.length }
      const fn = entityType === 'node' ? createNodeTypeAssignment : createEdgeTypeAssignment
      await fn(payload)
      setAddDefId('')
      reloadAssignments()
    } catch (e) {
      alert(e.response?.data?.message || 'Failed to add')
    } finally {
      setIsAdding(false)
    }
  }

  const handleUpdate = async (assignmentId, patch) => {
    const fn = entityType === 'node' ? updateNodeTypeAssignment : updateEdgeTypeAssignment
    await fn(assignmentId, patch)
    reloadAssignments()
  }

  const handleRemove = async () => {
    setRemoveLoading(true)
    try {
      const fn = entityType === 'node' ? deleteNodeTypeAssignment : deleteEdgeTypeAssignment
      await fn(removeTarget.id)
      setRemoveTarget(null)
      reloadAssignments()
    } catch (e) {
      alert(e.response?.data?.message || 'Remove failed')
    } finally {
      setRemoveLoading(false)
    }
  }

  const identifierKey = entityType === 'node' ? 'node_type_identifier' : 'edge_type_identifier'
  const nameKey       = entityType === 'node' ? 'node_type_name' : 'edge_type_name'

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-card border-b border-border px-6 py-4 shrink-0">
        <h1 className="text-base font-semibold text-foreground">Schema editor</h1>
        <p className="text-xs text-muted-foreground mt-0.5">
          Assign property definitions to types — this controls which fields appear when editing nodes and edges
        </p>
        <div className="flex gap-1 mt-4">
          {[['node', 'Node types'], ['edge', 'Edge types']].map(([key, label]) => (
            <Button
              key={key}
              size="xs"
              variant={entityType === key ? 'default' : 'outline'}
              onClick={() => setEntityType(key)}
            >
              {label}
            </Button>
          ))}
        </div>
      </div>

      {/* Body — two columns */}
      <div className="flex-1 flex overflow-hidden">

        {/* Left — type list */}
        <div className="w-56 border-r border-border overflow-y-auto shrink-0 bg-card">
          {types.length === 0 ? (
            <div className="p-4 text-xs text-muted-foreground">No types defined yet</div>
          ) : (
            types.map((t) => (
              <button key={t.id} onClick={() => setSelectedType(t)}
                className={`w-full text-left px-4 py-3 border-b border-border transition-colors ${
                  selectedType?.id === t.id ? 'bg-accent border-l-2 border-l-primary' : 'hover:bg-accent/50'
                }`}>
                <div className="text-xs font-medium text-foreground">{t[nameKey]}</div>
                <div className="text-[10px] text-muted-foreground">{t[identifierKey]}</div>
              </button>
            ))
          )}
        </div>

        {/* Right — assignments */}
        <div className="flex-1 flex flex-col overflow-hidden bg-card">
          {!selectedType ? (
            <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
              Select a type to edit its schema
            </div>
          ) : (
            <>
              <div className="px-4 py-3 border-b border-border shrink-0">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-foreground">
                    {selectedType[nameKey]} — assigned properties
                  </span>
                  <span className="text-[10px] text-muted-foreground">{assignments.length} assigned</span>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-muted-foreground font-medium">
                  <span className="w-14 text-center">Order</span>
                  <span className="flex-1">Property</span>
                  <span className="w-16 text-center">Required</span>
                  <span className="w-24 text-center">Default</span>
                  <span className="w-4" />
                </div>
              </div>

              <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                  <div className="flex items-center justify-center h-32 text-sm text-muted-foreground">Loading…</div>
                ) : assignments.length === 0 ? (
                  <div className="flex items-center justify-center h-32 text-xs text-muted-foreground">
                    No properties assigned — add one below
                  </div>
                ) : (
                  assignments.map((a) => (
                    <AssignmentRow
                      key={a.id}
                      assignment={a}
                      onUpdate={handleUpdate}
                      onRemove={() => setRemoveTarget(a)}
                    />
                  ))
                )}
              </div>

              {/* Add assignment */}
              <div className="px-4 py-3 border-t border-border bg-muted/30 shrink-0">
                <div className="text-[10px] font-medium text-muted-foreground mb-2">Add property</div>
                <div className="flex gap-2">
                  <Select value={addDefId} onValueChange={setAddDefId}>
                    <SelectTrigger className="flex-1 text-xs h-8">
                      <SelectValue placeholder="Select a property definition…" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableDefs.map((d) => {
                        const defNameKey = entityType === 'node' ? 'node_property_definition_name' : 'edge_property_definition_name'
                        const defTypeKey = entityType === 'node' ? 'node_property_definition_type' : 'edge_property_definition_type'
                        return (
                          <SelectItem key={d.id} value={d.id}>
                            {d[defNameKey]} ({d[defTypeKey]})
                          </SelectItem>
                        )
                      })}
                    </SelectContent>
                  </Select>
                  <Button size="sm" onClick={handleAdd} disabled={!addDefId || isAdding}>
                    {isAdding ? 'Adding…' : 'Add'}
                  </Button>
                </div>
                {availableDefs.length === 0 && !isLoading && (
                  <p className="text-[10px] text-muted-foreground mt-2">
                    All available properties are already assigned
                  </p>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {removeTarget && (
        <ConfirmDialog
          title="Remove assignment"
          message="Remove this property from the type? Existing node values are not deleted."
          confirmLabel="Remove"
          onConfirm={handleRemove}
          onCancel={() => setRemoveTarget(null)}
          isLoading={removeLoading}
        />
      )}
    </div>
  )
}
