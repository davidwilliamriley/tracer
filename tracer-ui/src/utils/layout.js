/**
 * layout.js — Cytoscape layout configuration helpers.
 */

export function getLayoutOptions(name = 'cose') {
  const base = { animate: true, animationDuration: 500, fit: true, padding: 60 }

  switch (name) {
    case 'cose':
      // Force-directed — best default for multi-cluster graphs like this one.
      // Nodes repel, edges attract — clusters form naturally.
      return {
        ...base,
        name: 'cose',
        idealEdgeLength: 100,
        nodeOverlap: 20,
        refresh: 20,
        randomize: false,
        componentSpacing: 120,   // space between disconnected subgraphs
        nodeRepulsion: 450000,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
      }

    case 'dagre':
      return {
        ...base,
        name: 'dagre',
        rankDir: 'TB',
        ranksep: 70,
        nodesep: 30,
        edgeSep: 10,
        align: 'DL',
      }

    case 'dagre-lr':
      return {
        ...base,
        name: 'dagre',
        rankDir: 'LR',
        ranksep: 90,
        nodesep: 30,
      }

    case 'breadthfirst':
      return {
        ...base,
        name: 'breadthfirst',
        directed: true,
        spacingFactor: 1.75,
        avoidOverlap: true,
      }

    case 'circle':
      return { ...base, name: 'circle', avoidOverlap: true }

    case 'grid':
      return { ...base, name: 'grid', avoidOverlap: true }

    default:
      return { ...base, name: 'cose', nodeRepulsion: 450000, componentSpacing: 120 }
  }
}

/**
 * Node type → colour mapping.
 */
export const TYPE_COLOURS = {
  HAZARD:         { bg: '#FEE2E2', border: '#EF4444', text: '#7F1D1D' },
  SAFETY_REQ:     { bg: '#DBEAFE', border: '#3B82F6', text: '#1E3A8A' },
  REQUIREMENT:    { bg: '#DBEAFE', border: '#3B82F6', text: '#1E3A8A' },
  CONTROL:        { bg: '#D1FAE5', border: '#10B981', text: '#064E3B' },
  EVIDENCE:       { bg: '#EDE9FE', border: '#8B5CF6', text: '#2E1065' },
  GSN_GOAL:       { bg: '#FEF9C3', border: '#EAB308', text: '#713F12' },
  GSN_STRATEGY:   { bg: '#FFEDD5', border: '#F97316', text: '#7C2D12' },
  GSN_SOLUTION:   { bg: '#DCFCE7', border: '#22C55E', text: '#14532D' },
  GSN_CONTEXT:    { bg: '#F1F5F9', border: '#94A3B8', text: '#1E293B' },
  ARCH_ELEMENT:   { bg: '#E0F2FE', border: '#0EA5E9', text: '#0C4A6E' },
  DEFAULT:        { bg: '#F9FAFB', border: '#D1D5DB', text: '#111827' },
}

export function colourForType(typeIdentifier) {
  const key = (typeIdentifier || '').toUpperCase()
  return TYPE_COLOURS[key] || TYPE_COLOURS.DEFAULT
}
