/**
 * SchemaEditor.jsx — assign property definitions to node/edge types.
 *
 * This is the centrepiece of the admin UI. The user:
 *   1. Selects a NodeType or EdgeType from the left panel
 *   2. Sees the currently assigned properties on the right
 *   3. Can add new assignments from unassigned definitions
 *   4. Can toggle is_required, set a default value, and adjust sort_order
 *   5. Can remove assignments
 *
 * This screen is what makes the dynamic form editor in the canvas work —
 * every field that appears when editing a node comes from here.
 */
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
    <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-100 last:border-0 hover:bg-gray-50">
      {/* Sort order */}
      <input type="number" value={sortOrder} min={0} step={1}
        onChange={(e) => setSortOrder(Number(e.target.value))}
        onBlur={() => save({ sort_order: sortOrder })}
        className="w-14 px-2 py-1 text-xs border border-gray-200 rounded text-center focus:outline-none focus:ring-1 focus:ring-blue-500"
        title="Sort order"
      />

      {/* Property name */}
      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium text-gray-900 truncate">
          {assignment.node_property_definition?.node_property_definition_name
          ?? assignment.edge_property_definition?.edge_property_definition_name
          ?? assignment.node_property_definition_id_fk?.slice(0, 8)
          ?? '—'}
        </div>
        <div className="text-[10px] text-gray-400">
          {assignment.node_property_definition?.node_property_definition_type
          ?? assignment.edge_property_definition?.edge_property_definition_type
          ?? ''}
        </div>
      </div>

      {/* Required toggle */}
      <label className="flex items-center gap-1 cursor-pointer shrink-0">
        <input type="checkbox" checked={isRequired}
          onChange={(e) => { setIsRequired(e.target.checked); save({ is_required: e.target.checked }) }}
          className="w-3 h-3 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <span className="text-[10px] text-gray-500">Required</span>
      </label>

      {/* Default value */}
      <input type="text" value={defaultValue} placeholder="default…"
        onChange={(e) => setDefault(e.target.value)}
        onBlur={() => save({ default_value: defaultValue || null })}
        className="w-24 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
        title="Default value for this type (overrides definition default)"
      />

      {/* Remove */}
      <button onClick={onRemove} className="text-gray-300 hover:text-red-400 transition-colors text-sm shrink-0" title="Remove assignment">
        ✕
      </button>

      {isSaving && <span className="text-[10px] text-blue-400 shrink-0">saving…</span>}
    </div>
  )
}

export default function SchemaEditor() {
  const [entityType, setEntityType] = useState('node')  // 'node' | 'edge'
  const [types, setTypes]           = useState([])
  const [selectedType, setSelectedType] = useState(null)
  const [assignments, setAssignments]   = useState([])
  const [allDefs, setAllDefs]           = useState([])
  const [isLoading, setIsLoading]       = useState(false)
  const [removeTarget, setRemoveTarget] = useState(null)
  const [removeLoading, setRemoveLoading] = useState(false)
  const [addDefId, setAddDefId]         = useState('')
  const [isAdding, setIsAdding]         = useState(false)

  // Load type list when entity type changes
  useEffect(() => {
    setSelectedType(null)
    setAssignments([])
    const fn = entityType === 'node' ? getNodeTypes : getEdgeTypes
    fn().then(setTypes).catch(() => setTypes([]))
  }, [entityType])

  // Load assignments and definitions when a type is selected
  useEffect(() => {
    if (!selectedType) return
    setIsLoading(true)
    const assignFn = entityType === 'node' ? getAssignmentsByNodeType : getAssignmentsByEdgeType
    const defFn    = entityType === 'node' ? getNodePropertyDefinitions : getEdgePropertyDefinitions
    Promise.all([assignFn(selectedType.id), defFn()])
      .then(([a, d]) => { setAssignments(a); setAllDefs(d) })
      .finally(() => setIsLoading(false))
  }, [selectedType, entityType])

  // Definitions not yet assigned to this type
  const assignedDefIds = new Set(
    assignments.map((a) =>
      a.node_property_definition_id_fk ?? a.edge_property_definition_id_fk
    )
  )
  const availableDefs = allDefs.filter((d) => !assignedDefIds.has(d.id))

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
      <div className="bg-white border-b border-gray-200 px-6 py-4 shrink-0">
        <h1 className="text-base font-semibold text-gray-900">Schema editor</h1>
        <p className="text-xs text-gray-400 mt-0.5">
          Assign property definitions to types — this controls which fields appear when editing nodes and edges
        </p>
        <div className="flex gap-1 mt-4">
          {[['node', 'Node types'], ['edge', 'Edge types']].map(([key, label]) => (
            <button key={key} onClick={() => setEntityType(key)}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${entityType === key ? 'bg-gray-900 text-white border-gray-900' : 'text-gray-600 border-gray-200 hover:border-gray-300'}`}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Body — two columns */}
      <div className="flex-1 flex overflow-hidden">

        {/* Left — type list */}
        <div className="w-56 border-r border-gray-200 overflow-y-auto shrink-0 bg-white">
          {types.length === 0 ? (
            <div className="p-4 text-xs text-gray-400">No types defined yet</div>
          ) : (
            types.map((t) => (
              <button key={t.id} onClick={() => setSelectedType(t)}
                className={`w-full text-left px-4 py-3 border-b border-gray-100 transition-colors ${
                  selectedType?.id === t.id ? 'bg-blue-50 border-l-2 border-l-blue-500' : 'hover:bg-gray-50'
                }`}>
                <div className="text-xs font-medium text-gray-900">{t[nameKey]}</div>
                <div className="text-[10px] text-gray-400">{t[identifierKey]}</div>
              </button>
            ))
          )}
        </div>

        {/* Right — assignments */}
        <div className="flex-1 flex flex-col overflow-hidden bg-white">
          {!selectedType ? (
            <div className="flex-1 flex items-center justify-center text-sm text-gray-400">
              Select a type to edit its schema
            </div>
          ) : (
            <>
              {/* Assignment list header */}
              <div className="px-4 py-3 border-b border-gray-100 shrink-0">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-gray-700">
                    {selectedType[nameKey]} — assigned properties
                  </span>
                  <span className="text-[10px] text-gray-400">{assignments.length} assigned</span>
                </div>
                {/* Column labels */}
                <div className="flex items-center gap-3 text-[10px] text-gray-400 font-medium">
                  <span className="w-14 text-center">Order</span>
                  <span className="flex-1">Property</span>
                  <span className="w-16 text-center">Required</span>
                  <span className="w-24 text-center">Default</span>
                  <span className="w-4" />
                </div>
              </div>

              {/* Assignments */}
              <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                  <div className="flex items-center justify-center h-32 text-sm text-gray-400">Loading…</div>
                ) : assignments.length === 0 ? (
                  <div className="flex items-center justify-center h-32 text-xs text-gray-400">
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
              <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 shrink-0">
                <div className="text-[10px] font-medium text-gray-500 mb-2">Add property</div>
                <div className="flex gap-2">
                  <select value={addDefId} onChange={(e) => setAddDefId(e.target.value)}
                    className="flex-1 px-3 py-1.5 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                    <option value="">Select a property definition…</option>
                    {availableDefs.map((d) => {
                      const nameKey = entityType === 'node' ? 'node_property_definition_name' : 'edge_property_definition_name'
                      const typeKey = entityType === 'node' ? 'node_property_definition_type' : 'edge_property_definition_type'
                      return (
                        <option key={d.id} value={d.id}>
                          {d[nameKey]} ({d[typeKey]})
                        </option>
                      )
                    })}
                  </select>
                  <button onClick={handleAdd} disabled={!addDefId || isAdding}
                    className="px-4 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors shrink-0">
                    {isAdding ? 'Adding…' : 'Add'}
                  </button>
                </div>
                {availableDefs.length === 0 && !isLoading && (
                  <p className="text-[10px] text-gray-400 mt-2">
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
