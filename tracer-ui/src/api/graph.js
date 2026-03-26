/**
 * graph.js — functions that call the graph-related API endpoints.
 *
 * Each function maps to one API endpoint. They all return the
 * response data directly so calling code gets clean objects back.
 */
import client from './client'

// ---------------------------------------------------------------------------
// Graph topology — the full graph for the canvas
// ---------------------------------------------------------------------------

export async function getGraph() {
  const { data } = await client.get('/graph')
  return data  // { nodes, edges, node_count, edge_count }
}

// ---------------------------------------------------------------------------
// Node endpoints
// ---------------------------------------------------------------------------

export async function getNodeFull(nodeId) {
  const { data } = await client.get(`/nodes/${nodeId}/full`)
  return data  // NodeFull with type metadata and all property values
}

export async function getNeighbours(nodeId) {
  const { data } = await client.get(`/nodes/${nodeId}/neighbours`)
  return data
}

export async function getShortestPath(sourceId, targetId) {
  const { data } = await client.get(`/nodes/${sourceId}/paths`, {
    params: { target: targetId },
  })
  return data
}

export async function getSubgraph(nodeId, maxDepth = 5) {
  const { data } = await client.get(`/nodes/${nodeId}/subgraph`, {
    params: { max_depth: maxDepth },
  })
  return data
}

export async function getNodes(params = {}) {
  const { data } = await client.get('/nodes/', { params })
  return data  // Page<NodeResponse>
}

export async function updateNodeProperties(nodeId, properties, modifiedBy) {
  const { data } = await client.post(`/nodes/${nodeId}/properties`, {
    properties,
    modified_by: modifiedBy,
  })
  return data  // NodeFull
}

// ---------------------------------------------------------------------------
// Node type endpoints
// ---------------------------------------------------------------------------

export async function getNodeTypes(params = {}) {
  const { data } = await client.get('/node-types/', { params })
  return data
}

export async function getNodeTypeFormSchema(nodeTypeId) {
  const { data } = await client.get(`/node-types/${nodeTypeId}/form-schema`)
  return data  // FormSchema with ordered fields
}

// ---------------------------------------------------------------------------
// Edge endpoints
// ---------------------------------------------------------------------------

export async function getEdgeFull(edgeId) {
  const { data } = await client.get(`/edges/${edgeId}/full`)
  return data
}

export async function getEdges(params = {}) {
  const { data } = await client.get('/edges/', { params })
  return data
}

export async function getEdgeTypes(params = {}) {
  const { data } = await client.get('/edge-types/', { params })
  return data
}
