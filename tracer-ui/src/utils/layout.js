/**
 * layout.js — applies the Dagre layout algorithm to React Flow nodes and edges.
 *
 * What this does:
 *   Your API returns nodes and edges but no x/y positions — it's a topology,
 *   not a drawing. This function feeds that topology into Dagre, which
 *   computes good x/y positions, then returns the positioned nodes ready
 *   for React Flow to render.
 *
 * Why Dagre?
 *   Dagre produces a layered (hierarchical) layout — nodes at the top
 *   flow down to nodes at the bottom following edge direction. This suits
 *   Tracer well since safety cases, hazards, and requirements form natural
 *   hierarchies. Force-directed layouts are better for peer relationships.
 */
import dagre from 'dagre'

const NODE_WIDTH = 200
const NODE_HEIGHT = 60

/**
 * Apply Dagre layout to React Flow nodes and edges.
 *
 * @param {Array} nodes - React Flow node objects (need id, data)
 * @param {Array} edges - React Flow edge objects (need id, source, target)
 * @param {string} direction - 'TB' (top-bottom) or 'LR' (left-right)
 * @returns {{ nodes: Array, edges: Array }} - nodes with x,y positions added
 */
export function applyDagreLayout(nodes, edges, direction = 'TB') {
  const g = new dagre.graphlib.Graph()

  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({
    rankdir: direction,   // TB = top to bottom, LR = left to right
    ranksep: 80,          // vertical gap between layers
    nodesep: 40,          // horizontal gap between nodes in the same layer
    marginx: 40,
    marginy: 40,
  })

  // Register every node with its dimensions
  nodes.forEach((node) => {
    g.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT })
  })

  // Register every edge
  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target)
  })

  // Run the layout algorithm
  dagre.layout(g)

  // Extract positions back out and apply to the React Flow nodes
  const positionedNodes = nodes.map((node) => {
    const { x, y } = g.node(node.id)
    return {
      ...node,
      position: {
        // Dagre centres positions — React Flow uses top-left corner
        x: x - NODE_WIDTH / 2,
        y: y - NODE_HEIGHT / 2,
      },
    }
  })

  return { nodes: positionedNodes, edges }
}
