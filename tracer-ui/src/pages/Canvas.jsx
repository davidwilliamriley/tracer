/**
 * Canvas.jsx — graph canvas page (Phase 4B version).
 *
 * The toolbar and logout moved to the Sidebar in Phase 4B.
 * This page is now just the canvas + node panel.
 */
import { useState, useEffect, useCallback } from 'react'
import { ReactFlowProvider } from '@xyflow/react'
import { getGraph } from '../api/graph'
import { applyDagreLayout } from '../utils/layout'
import GraphCanvas from '../components/GraphCanvas'
import NodePanel from '../components/NodePanel'

function buildFlowGraph(apiGraph) {
  const nodes = apiGraph.nodes.map((n) => ({
    id: n.id,
    type: 'typedNode',
    data: {
      label: n.name,
      identifier: n.identifier,
      typeIdentifier: n.type_identifier,
      typeName: n.type_name,
    },
    position: { x: 0, y: 0 },
  }))

  const edges = apiGraph.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.type_identifier,
    labelStyle: { fontSize: 10, fill: '#94a3b8' },
    labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
  }))

  return { nodes, edges }
}

export default function Canvas() {
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedNodeId, setSelectedNodeId] = useState(null)
  const [layoutDirection, setLayoutDirection] = useState('TB')
  const [nodeCount, setNodeCount] = useState(0)
  const [edgeCount, setEdgeCount] = useState(0)

  const fetchGraph = useCallback(async (direction = layoutDirection) => {
    setIsLoading(true)
    setError(null)
    try {
      const apiGraph = await getGraph()
      setNodeCount(apiGraph.node_count)
      setEdgeCount(apiGraph.edge_count)
      const { nodes: rawNodes, edges: rawEdges } = buildFlowGraph(apiGraph)
      const { nodes: positioned, edges: laid } = applyDagreLayout(rawNodes, rawEdges, direction)
      setNodes(positioned)
      setEdges(laid)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load graph')
    } finally {
      setIsLoading(false)
    }
  }, [layoutDirection])

  useEffect(() => { fetchGraph() }, [])

  const handleNodeClick = useCallback((node) => setSelectedNodeId(node.id), [])
  const handleClosePanel = useCallback(() => setSelectedNodeId(null), [])

  const handleLayoutChange = (dir) => {
    setLayoutDirection(dir)
    fetchGraph(dir)
  }

  return (
    <div className="flex flex-col h-full">

      {/* Canvas toolbar */}
      <div className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-4 shrink-0">
        <span className="text-xs text-gray-400">
          {isLoading ? 'Loading…' : `${nodeCount} nodes · ${edgeCount} edges`}
        </span>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-gray-200 overflow-hidden text-xs">
            {['TB', 'LR'].map((dir) => (
              <button
                key={dir}
                onClick={() => handleLayoutChange(dir)}
                className={`px-2.5 py-1 transition-colors ${
                  layoutDirection === dir
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-600 hover:bg-gray-50 border-l border-gray-200 first:border-0'
                }`}
              >
                {dir === 'TB' ? '↕ TB' : '↔ LR'}
              </button>
            ))}
          </div>
          <button
            onClick={() => fetchGraph()}
            disabled={isLoading}
            className="px-3 py-1 text-xs border border-gray-200 rounded-lg text-gray-600
                       hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative overflow-hidden">
        {error && (
          <div className="absolute inset-0 flex items-center justify-center z-10">
            <div className="bg-white border border-red-200 rounded-xl p-6 max-w-sm text-center shadow-sm">
              <p className="text-sm text-red-600 mb-3">{error}</p>
              <button onClick={() => fetchGraph()} className="text-sm text-blue-600 hover:underline">
                Try again
              </button>
            </div>
          </div>
        )}

        {!isLoading && !error && nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center z-10">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">No nodes yet</p>
              <p className="text-xs text-gray-400">Add NodeTypes and Nodes via the Admin section</p>
            </div>
          </div>
        )}

        <ReactFlowProvider>
          {nodes.length > 0 && (
            <GraphCanvas nodes={nodes} edges={edges} onNodeClick={handleNodeClick} />
          )}
          {selectedNodeId && (
            <NodePanel nodeId={selectedNodeId} onClose={handleClosePanel} />
          )}
        </ReactFlowProvider>
      </div>
    </div>
  )
}
