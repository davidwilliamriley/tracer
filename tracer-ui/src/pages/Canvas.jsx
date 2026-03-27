/**
 * Canvas.jsx — main graph canvas page.
 * Toolbar at top, Cytoscape canvas filling remaining height,
 * NodePanel slides in from the right on node click.
 */
import { useState, useEffect, useCallback } from 'react'
import { getGraph } from '../api/graph'
import GraphCanvas from '../components/GraphCanvas'
import NodePanel from '../components/NodePanel'

const LAYOUTS = [
  { key: 'cose',         label: '⊛ Force' },
  { key: 'dagre',        label: '↕ TB'    },
  { key: 'dagre-lr',     label: '↔ LR'    },
  { key: 'breadthfirst', label: '⊞ BFS'   },
]

function buildElements(apiGraph) {
  const nodes = apiGraph.nodes.map((n) => ({
    group: 'nodes',
    data: {
      id:             n.id,
      label:          n.name,
      identifier:     n.identifier,
      typeIdentifier: n.type_identifier,
      typeName:       n.type_name,
    },
  }))
  const edges = apiGraph.edges.map((e) => ({
    group: 'edges',
    data: {
      id:             e.id,
      source:         e.source,
      target:         e.target,
      typeLabel:      e.type_identifier,
      typeIdentifier: e.type_identifier,
    },
  }))
  return [...nodes, ...edges]
}

export default function Canvas() {
  const [elements, setElements]     = useState([])
  const [isLoading, setIsLoading]   = useState(true)
  const [error, setError]           = useState(null)
  const [layout, setLayout]         = useState('cose')
  const [selectedNodeId, setSelected] = useState(null)
  const [counts, setCounts]         = useState({ nodes: 0, edges: 0 })

  const fetchGraph = useCallback(async () => {
    setIsLoading(true); setError(null)
    try {
      const data = await getGraph()
      setCounts({ nodes: data.node_count, edges: data.edge_count })
      setElements(buildElements(data))
    } catch (e) {
      setError(e.response?.data?.message || 'Failed to load graph')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { fetchGraph() }, [])

  const handleNodeClick = useCallback((nodeData) => {
    setSelected(nodeData?.id || null)
  }, [])

  return (
    <div className="flex flex-col h-full overflow-hidden">

      {/* ── Top toolbar ── */}
      <div className="h-12 bg-white border-b border-gray-200 flex items-center gap-3 px-4 shrink-0 z-10">
        <span className="text-xs text-gray-400 mr-auto">
          {isLoading ? 'Loading…' : `${counts.nodes} nodes · ${counts.edges} edges`}
        </span>

        {/* Layout picker */}
        <div className="flex rounded-lg border border-gray-200 overflow-hidden text-xs">
          {LAYOUTS.map((l, i) => (
            <button key={l.key} onClick={() => setLayout(l.key)}
              className={`px-2.5 py-1.5 transition-colors ${i > 0 ? 'border-l border-gray-200' : ''} ${
                layout === l.key
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}>
              {l.label}
            </button>
          ))}
        </div>

        <button onClick={fetchGraph} disabled={isLoading}
          className="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600
                     hover:bg-gray-50 disabled:opacity-50 transition-colors">
          Refresh
        </button>
      </div>

      {/* ── Canvas + panel ── */}
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 relative overflow-hidden">

          {/* Error */}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center z-10">
              <div className="bg-white border border-red-200 rounded-xl p-6 text-center shadow-sm max-w-sm">
                <p className="text-sm text-red-600 mb-3">{error}</p>
                <button onClick={fetchGraph} className="text-sm text-blue-600 hover:underline">
                  Try again
                </button>
              </div>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !error && elements.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center z-10">
              <div className="text-center">
                <p className="text-sm text-gray-500 mb-1">No nodes yet</p>
                <p className="text-xs text-gray-400">
                  Run seed_data.py or add nodes via the Admin tab
                </p>
              </div>
            </div>
          )}

          {/* Canvas */}
          {elements.length > 0 && (
            <GraphCanvas
              elements={elements}
              layout={layout}
              onNodeClick={handleNodeClick}
              selectedId={selectedNodeId}
            />
          )}
        </div>

        {/* Slide-in detail panel */}
        {selectedNodeId && (
          <NodePanel
            nodeId={selectedNodeId}
            onClose={() => setSelected(null)}
          />
        )}
      </div>
    </div>
  )
}
