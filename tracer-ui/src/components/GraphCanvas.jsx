/**
 * GraphCanvas.jsx — the main React Flow canvas.
 *
 * React concepts introduced here:
 *   - useCallback: memoises functions so React doesn't recreate them
 *     on every render — important for React Flow event handlers
 *   - useMemo: memoises computed values — we use it to build the
 *     nodeTypes object once rather than on every render
 *   - Props: data passed down from the parent (Canvas page)
 *
 * React Flow concepts:
 *   - nodes and edges are arrays of objects with specific shapes
 *   - onNodeClick fires when the user clicks a node
 *   - nodeTypes maps a type string to a custom component
 *   - Controls adds zoom buttons, MiniMap adds the overview
 *   - Background adds the dot grid
 */
import { useCallback, useMemo } from 'react'
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
} from '@xyflow/react'
import TypedNode from './nodes/TypedNode'

// Register custom node types — this object must be defined outside the
// component or memoised, otherwise React Flow re-registers on every render
const nodeTypes = { typedNode: TypedNode }

export default function GraphCanvas({ nodes: initialNodes, edges: initialEdges, onNodeClick }) {
  // useNodesState and useEdgesState are React Flow hooks that manage
  // nodes and edges with built-in change handlers for drag, select, etc.
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  const handleNodeClick = useCallback((event, node) => {
    onNodeClick?.(node)
  }, [onNodeClick])

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={handleNodeClick}
      nodeTypes={nodeTypes}
      fitView                          // auto-zoom to fit all nodes on load
      fitViewOptions={{ padding: 0.1 }}
      minZoom={0.1}
      maxZoom={2}
      defaultEdgeOptions={{
        style: { stroke: '#94a3b8', strokeWidth: 1.5 },
        animated: false,
      }}
    >
      <Controls className="!shadow-none !border !border-gray-200 !rounded-lg" />
      <MiniMap
        nodeColor={(node) => {
          const type = node.data?.typeIdentifier?.toUpperCase()
          const colours = {
            HAZARD: '#fca5a5',
            SAFETY_REQUIREMENT: '#93c5fd',
            REQUIREMENT: '#93c5fd',
            CONTROL: '#86efac',
            EVIDENCE: '#c4b5fd',
          }
          return colours[type] || '#d1d5db'
        }}
        className="!border !border-gray-200 !rounded-lg !shadow-none"
      />
      <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#e2e8f0" />
    </ReactFlow>
  )
}
