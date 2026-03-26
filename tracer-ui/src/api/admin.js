/**
 * admin.js — API functions for the admin screens.
 * Covers NodeTypes, EdgeTypes, PropertyDefinitions, and Assignments.
 */
import client from './client'

// ---------------------------------------------------------------------------
// Node Types
// ---------------------------------------------------------------------------

export async function getNodeTypes(params = {}) {
  const { data } = await client.get('/node-types/', { params: { limit: 200, ...params } })
  return data.items
}

export async function createNodeType(payload) {
  const { data } = await client.post('/node-types/', payload)
  return data
}

export async function updateNodeType(id, payload) {
  const { data } = await client.put(`/node-types/${id}`, payload)
  return data
}

export async function deleteNodeType(id) {
  const { data } = await client.delete(`/node-types/${id}`)
  return data
}

// ---------------------------------------------------------------------------
// Edge Types
// ---------------------------------------------------------------------------

export async function getEdgeTypes(params = {}) {
  const { data } = await client.get('/edge-types/', { params: { limit: 200, ...params } })
  return data.items
}

export async function createEdgeType(payload) {
  const { data } = await client.post('/edge-types/', payload)
  return data
}

export async function updateEdgeType(id, payload) {
  const { data } = await client.put(`/edge-types/${id}`, payload)
  return data
}

export async function deleteEdgeType(id) {
  const { data } = await client.delete(`/edge-types/${id}`)
  return data
}

// ---------------------------------------------------------------------------
// Node Property Definitions
// ---------------------------------------------------------------------------

export async function getNodePropertyDefinitions(params = {}) {
  const { data } = await client.get('/node-property-definitions/', {
    params: { limit: 200, ...params },
  })
  return data.items
}

export async function createNodePropertyDefinition(payload) {
  const { data } = await client.post('/node-property-definitions/', payload)
  return data
}

export async function updateNodePropertyDefinition(id, payload) {
  const { data } = await client.put(`/node-property-definitions/${id}`, payload)
  return data
}

export async function deleteNodePropertyDefinition(id) {
  const { data } = await client.delete(`/node-property-definitions/${id}`)
  return data
}

// ---------------------------------------------------------------------------
// Edge Property Definitions
// ---------------------------------------------------------------------------

export async function getEdgePropertyDefinitions(params = {}) {
  const { data } = await client.get('/edge-property-definitions/', {
    params: { limit: 200, ...params },
  })
  return data.items
}

export async function createEdgePropertyDefinition(payload) {
  const { data } = await client.post('/edge-property-definitions/', payload)
  return data
}

export async function updateEdgePropertyDefinition(id, payload) {
  const { data } = await client.put(`/edge-property-definitions/${id}`, payload)
  return data
}

export async function deleteEdgePropertyDefinition(id) {
  const { data } = await client.delete(`/edge-property-definitions/${id}`)
  return data
}

// ---------------------------------------------------------------------------
// Node Type Property Assignments
// ---------------------------------------------------------------------------

export async function getAssignmentsByNodeType(nodeTypeId) {
  const { data } = await client.get(
    `/node-type-property-assignments/by-node-type/${nodeTypeId}`
  )
  return data  // already a list, ordered by sort_order
}

export async function createNodeTypeAssignment(payload) {
  const { data } = await client.post('/node-type-property-assignments/', payload)
  return data
}

export async function updateNodeTypeAssignment(id, payload) {
  const { data } = await client.put(`/node-type-property-assignments/${id}`, payload)
  return data
}

export async function deleteNodeTypeAssignment(id) {
  const { data } = await client.delete(`/node-type-property-assignments/${id}`)
  return data
}

// ---------------------------------------------------------------------------
// Edge Type Property Assignments
// ---------------------------------------------------------------------------

export async function getAssignmentsByEdgeType(edgeTypeId) {
  const { data } = await client.get(
    `/edge-type-property-assignments/by-edge-type/${edgeTypeId}`
  )
  return data
}

export async function createEdgeTypeAssignment(payload) {
  const { data } = await client.post('/edge-type-property-assignments/', payload)
  return data
}

export async function updateEdgeTypeAssignment(id, payload) {
  const { data } = await client.put(`/edge-type-property-assignments/${id}`, payload)
  return data
}

export async function deleteEdgeTypeAssignment(id) {
  const { data } = await client.delete(`/edge-type-property-assignments/${id}`)
  return data
}
