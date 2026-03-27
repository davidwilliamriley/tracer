/**
 * NodePanel.jsx — node detail panel.
 * Order: identity → connections → properties → audit
 */
import { useState, useEffect } from 'react'
import { useNodeDetail } from '../hooks/useNodeDetail'
import { getNodeTypeFormSchema, getNeighbours } from '../api/graph'
import DynamicForm from './DynamicForm'
import { colourForType } from '../utils/layout'

function TypeBadge({ typeIdentifier }) {
  const c = colourForType(typeIdentifier)
  return (
    <span className="inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full border"
      style={{ background: c.bg, borderColor: c.border, color: c.text }}>
      {typeIdentifier}
    </span>
  )
}

function PropRow({ label, value, type }) {
  const display =
    value === null || value === undefined || value === ''
      ? <span className="text-gray-300 italic text-xs">—</span>
      : type === 'boolean'
        ? <span className={`text-xs font-medium ${value === 'true' || value === '1' ? 'text-green-600' : 'text-red-400'}`}>
            {value === 'true' || value === '1' ? 'Yes' : 'No'}
          </span>
        : <span className="text-xs text-gray-900 break-words">{value}</span>

  return (
    <div className="flex gap-3 py-2 border-b border-gray-100 last:border-0">
      <span className="text-xs text-gray-400 w-28 shrink-0 pt-0.5">{label}</span>
      {display}
    </div>
  )
}

function ConnectionPill({ neighbour, direction }) {
  const c = colourForType(neighbour.type_identifier)
  const edgeType = direction === 'in'
    ? neighbour.edges?.find(e => e.direction === 'incoming')?.edge_type_identifier
    : neighbour.edges?.find(e => e.direction === 'outgoing')?.edge_type_identifier

  return (
    <div className="flex items-start gap-2 px-2.5 py-2 rounded-lg mb-1.5 border text-xs"
      style={{ background: c.bg, borderColor: c.border }}>
      <span className="shrink-0 font-bold mt-0.5" style={{ color: c.border }}>
        {direction === 'in' ? '←' : '→'}
      </span>
      <div className="min-w-0">
        <div className="font-medium truncate" style={{ color: c.text }}>
          {neighbour.identifier} · {neighbour.name}
        </div>
        {edgeType && (
          <div className="text-[10px] mt-0.5 opacity-60" style={{ color: c.text }}>
            {edgeType}
          </div>
        )}
      </div>
    </div>
  )
}

function SectionLabel({ children }) {
  return (
    <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-4 first:mt-0">
      {children}
    </div>
  )
}

export default function NodePanel({ nodeId, onClose }) {
  const { node, isLoading, error, refresh } = useNodeDetail(nodeId)
  const [schema, setSchema]       = useState(null)
  const [neighbours, setNeighbours] = useState(null)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    if (!node) return
    setIsEditing(false)

    getNodeTypeFormSchema(node.node_type_id)
      .then(setSchema).catch(() => setSchema(null))

    getNeighbours(node.id || nodeId)
      .then(setNeighbours).catch(() => setNeighbours(null))
  }, [node?.id])

  const incoming = neighbours?.neighbours?.filter(n =>
    n.edges?.some(e => e.direction === 'incoming')
  ) || []

  const outgoing = neighbours?.neighbours?.filter(n =>
    n.edges?.some(e => e.direction === 'outgoing')
  ) || []

  return (
    <div className="w-72 bg-white border-l border-gray-200 shadow-xl flex flex-col h-full shrink-0">

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 shrink-0 bg-gray-50">
        <span className="text-xs font-semibold text-gray-600">Node detail</span>
        <button onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors w-6 h-6 flex items-center justify-center rounded hover:bg-gray-200">
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading && (
          <div className="flex items-center justify-center h-32 text-sm text-gray-400">Loading…</div>
        )}
        {error && (
          <div className="m-4 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">{error}</div>
        )}

        {node && !isLoading && (
          <>
            {/* Identity */}
            <div className="px-4 py-3 border-b border-gray-100">
              <TypeBadge typeIdentifier={node.node_type_identifier} />
              <h2 className="text-sm font-semibold text-gray-900 mt-2 leading-snug">
                {node.node_name}
              </h2>
              <div className="text-xs text-gray-400 mt-0.5 font-mono">{node.node_identifier}</div>
            </div>

            {/* View / Edit toggle */}
            <div className="flex gap-1.5 px-4 py-2 border-b border-gray-100 bg-gray-50">
              {['View', 'Edit'].map((mode) => (
                <button key={mode} onClick={() => setIsEditing(mode === 'Edit')}
                  className={`flex-1 py-1 text-xs rounded-md border transition-colors ${
                    (isEditing ? 'Edit' : 'View') === mode
                      ? 'bg-gray-900 text-white border-gray-900'
                      : 'text-gray-500 border-gray-200 hover:border-gray-300'
                  }`}>
                  {mode}
                </button>
              ))}
            </div>

            {/* View mode — connections first, then properties */}
            {!isEditing && (
              <div className="px-4 py-3">

                {/* Connections */}
                {(incoming.length > 0 || outgoing.length > 0) && (
                  <div>
                    <SectionLabel>Connections</SectionLabel>

                    {incoming.length > 0 && (
                      <div className="mb-2">
                        <div className="text-[10px] text-gray-400 mb-1.5">← Incoming</div>
                        {incoming.map((n) => (
                          <ConnectionPill key={n.id} neighbour={n} direction="in" />
                        ))}
                      </div>
                    )}

                    {outgoing.length > 0 && (
                      <div>
                        <div className="text-[10px] text-gray-400 mb-1.5">→ Outgoing</div>
                        {outgoing.map((n) => (
                          <ConnectionPill key={n.id} neighbour={n} direction="out" />
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Properties */}
                {node.properties.length > 0 && (
                  <div>
                    <SectionLabel>Properties</SectionLabel>
                    {node.properties.map((p) => (
                      <PropRow key={p.definition_id} label={p.name} value={p.value} type={p.type} />
                    ))}
                  </div>
                )}

                {/* Audit */}
                <div>
                  <SectionLabel>Audit</SectionLabel>
                  <PropRow label="Created by" value={node.created_by} />
                  <PropRow label="Created on" value={node.created_on?.slice(0, 10)} />
                  <PropRow label="Modified by" value={node.modified_by} />
                </div>
              </div>
            )}

            {/* Edit mode */}
            {isEditing && (
              <div className="px-4 py-3">
                {schema
                  ? <DynamicForm schema={schema} existingProperties={node.properties}
                      nodeId={nodeId} onSaved={() => { refresh(); setIsEditing(false) }} />
                  : <p className="text-xs text-gray-400 italic">No editable properties defined</p>
                }
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
