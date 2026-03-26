/**
 * NodePanel.jsx — slide-in panel showing node detail and edit form.
 *
 * Appears when the user clicks a node on the canvas.
 * Shows: node name, type, all property values, and an edit form.
 * Fetches: GET /nodes/{id}/full and GET /node-types/{id}/form-schema
 *
 * React concept — conditional rendering:
 *   `{condition && <Component />}` only renders the component if
 *   condition is truthy. Used here to show loading/error/content states.
 */
import { useState, useEffect } from 'react'
import { useNodeDetail } from '../hooks/useNodeDetail'
import { getNodeTypeFormSchema } from '../api/graph'
import DynamicForm from './DynamicForm'

function PropertyRow({ label, value, type }) {
  if (value === null || value === undefined) {
    return (
      <div className="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0">
        <span className="text-xs text-gray-500 min-w-[100px] shrink-0">{label}</span>
        <span className="text-xs text-gray-300 italic">—</span>
      </div>
    )
  }

  // Format boolean values nicely
  if (type === 'boolean') {
    return (
      <div className="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0">
        <span className="text-xs text-gray-500 min-w-[100px] shrink-0">{label}</span>
        <span className={`text-xs font-medium ${value === 'true' || value === '1' ? 'text-green-600' : 'text-red-500'}`}>
          {value === 'true' || value === '1' ? 'Yes' : 'No'}
        </span>
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0">
      <span className="text-xs text-gray-500 min-w-[100px] shrink-0">{label}</span>
      <span className="text-xs text-gray-900 break-words">{value}</span>
    </div>
  )
}

export default function NodePanel({ nodeId, onClose }) {
  const { node, isLoading, error, refresh } = useNodeDetail(nodeId)
  const [schema, setSchema] = useState(null)
  const [isEditing, setIsEditing] = useState(false)

  // Fetch the form schema when we have the node's type
  useEffect(() => {
    if (!node?.node_type_id) return
    getNodeTypeFormSchema(node.node_type_id)
      .then(setSchema)
      .catch(() => setSchema(null))
  }, [node?.node_type_id])

  const handleSaved = (updatedNode) => {
    refresh()
    setIsEditing(false)
  }

  return (
    // Overlay backdrop
    <div className="absolute inset-0 z-10 flex justify-end pointer-events-none">

      {/* Panel */}
      <div className="w-80 bg-white border-l border-gray-200 shadow-xl flex flex-col pointer-events-auto h-full">

        {/* Panel header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 shrink-0">
          <span className="text-sm font-medium text-gray-900">Node detail</span>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded"
          >
            ✕
          </button>
        </div>

        {/* Panel content */}
        <div className="flex-1 overflow-y-auto p-4">

          {isLoading && (
            <div className="flex items-center justify-center h-32">
              <div className="text-sm text-gray-400">Loading…</div>
            </div>
          )}

          {error && (
            <div className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
              {error}
            </div>
          )}

          {node && !isLoading && (
            <div className="space-y-5">

              {/* Node identity */}
              <div>
                <div className="text-[10px] font-medium text-gray-400 uppercase tracking-wide mb-2">
                  {node.node_type_identifier}
                </div>
                <h2 className="text-base font-semibold text-gray-900 leading-tight">
                  {node.node_name}
                </h2>
                <div className="text-xs text-gray-400 mt-0.5">{node.node_identifier}</div>
              </div>

              {/* Toggle between view and edit */}
              <div className="flex gap-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className={`flex-1 py-1.5 text-xs rounded-lg border transition-colors ${
                    !isEditing
                      ? 'bg-gray-900 text-white border-gray-900'
                      : 'text-gray-600 border-gray-200 hover:border-gray-300'
                  }`}
                >
                  View
                </button>
                <button
                  onClick={() => setIsEditing(true)}
                  className={`flex-1 py-1.5 text-xs rounded-lg border transition-colors ${
                    isEditing
                      ? 'bg-gray-900 text-white border-gray-900'
                      : 'text-gray-600 border-gray-200 hover:border-gray-300'
                  }`}
                >
                  Edit
                </button>
              </div>

              {/* View mode — property values */}
              {!isEditing && (
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-2">Properties</div>
                  {node.properties.length === 0 ? (
                    <p className="text-xs text-gray-400 italic">No properties defined</p>
                  ) : (
                    <div>
                      {node.properties.map((prop) => (
                        <PropertyRow
                          key={prop.definition_id}
                          label={prop.name}
                          value={prop.value}
                          type={prop.type}
                        />
                      ))}
                    </div>
                  )}

                  {/* Audit info */}
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="text-xs font-medium text-gray-500 mb-2">Audit</div>
                    <PropertyRow label="Created by" value={node.created_by} />
                    <PropertyRow label="Created on" value={node.created_on?.slice(0, 10)} />
                    <PropertyRow label="Modified by" value={node.modified_by} />
                    <PropertyRow label="Modified on" value={node.modified_on?.slice(0, 10)} />
                  </div>
                </div>
              )}

              {/* Edit mode — dynamic form */}
              {isEditing && schema && (
                <DynamicForm
                  schema={schema}
                  existingProperties={node.properties}
                  nodeId={nodeId}
                  onSaved={handleSaved}
                />
              )}

              {isEditing && !schema && (
                <p className="text-xs text-gray-400 italic">No editable properties</p>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  )
}
