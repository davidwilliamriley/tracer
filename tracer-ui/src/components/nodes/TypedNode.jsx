/**
 * TypedNode.jsx — custom React Flow node component.
 *
 * React concept — custom components:
 *   React Flow lets you define your own node appearance by passing a
 *   custom component. It receives a `data` prop containing whatever
 *   you attached to the node when building the graph. Here we use it
 *   to show the node type as a coloured badge and display the name.
 *
 * The Handle components are React Flow's connection points — they render
 * the small dots at the top and bottom of each node where edges connect.
 */
import { Handle, Position } from '@xyflow/react'

// Map NodeType identifiers to colours so different types are visually distinct.
// Add entries here as you define more NodeTypes in Tracer.
const TYPE_COLOURS = {
  HAZARD:              'bg-red-100 text-red-800 border-red-200',
  SAFETY_REQUIREMENT:  'bg-blue-100 text-blue-800 border-blue-200',
  REQUIREMENT:         'bg-blue-100 text-blue-800 border-blue-200',
  CONTROL:             'bg-green-100 text-green-800 border-green-200',
  EVIDENCE:            'bg-purple-100 text-purple-800 border-purple-200',
  ACCIDENT:            'bg-orange-100 text-orange-800 border-orange-200',
  DEFAULT:             'bg-gray-100 text-gray-800 border-gray-200',
}

export default function TypedNode({ data, selected }) {
  const typeKey = data.typeIdentifier?.toUpperCase() || 'DEFAULT'
  const badgeClass = TYPE_COLOURS[typeKey] || TYPE_COLOURS.DEFAULT

  return (
    <div
      className={`
        bg-white border-2 rounded-lg px-3 py-2 min-w-[180px] max-w-[200px]
        shadow-sm transition-shadow
        ${selected
          ? 'border-blue-500 shadow-md shadow-blue-100'
          : 'border-gray-200 hover:border-gray-300 hover:shadow-md'}
      `}
    >
      {/* Incoming edge connection point */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-2 !h-2 !bg-gray-400 !border-white"
      />

      {/* Node type badge */}
      <div className={`inline-block text-[10px] font-medium px-1.5 py-0.5 rounded border mb-1.5 ${badgeClass}`}>
        {data.typeIdentifier || 'Unknown'}
      </div>

      {/* Node name */}
      <div className="text-xs font-medium text-gray-900 leading-tight truncate" title={data.label}>
        {data.label}
      </div>

      {/* Node identifier in muted style */}
      <div className="text-[10px] text-gray-400 mt-0.5 truncate">
        {data.identifier}
      </div>

      {/* Outgoing edge connection point */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-2 !h-2 !bg-gray-400 !border-white"
      />
    </div>
  )
}
