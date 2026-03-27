/**
 * GraphCanvas.jsx — Cytoscape.js canvas.
 * Rectangular nodes with identifier + name, colour-coded by type.
 * Connections-first panel and top toolbar handled by Canvas.jsx / NodePanel.jsx.
 */
import { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import cytoscapeDagre from 'cytoscape-dagre'
import { getLayoutOptions, colourForType } from '../utils/layout'

cytoscape.use(cytoscapeDagre)

function buildStylesheet() {
  return [
    {
      selector: 'node',
      style: {
        'shape': 'roundrectangle',
        'width': 180,
        'height': 52,
        'background-color': (ele) => colourForType(ele.data('typeIdentifier')).bg,
        'border-color':     (ele) => colourForType(ele.data('typeIdentifier')).border,
        'border-width': 1.5,
        'label': (ele) => `${ele.data('identifier')}\n${ele.data('label')}`,
        'text-valign': 'center',
        'text-halign': 'center',
        'text-wrap': 'wrap',
        'text-max-width': 168,
        'font-size': 10,
        'font-family': 'system-ui, sans-serif',
        'color': (ele) => colourForType(ele.data('typeIdentifier')).text,
        'line-height': 1.4,
        'padding': 6,
      },
    },
    {
      selector: 'node:selected',
      style: {
        'border-width': 3,
        'border-color': '#2563EB',
      },
    },
    {
      selector: 'node.highlighted',
      style: {
        'border-width': 2.5,
        'border-color': '#2563EB',
        'z-index': 10,
      },
    },
    {
      selector: 'node.dimmed',
      style: { 'opacity': 0.2 },
    },
    {
      selector: 'edge',
      style: {
        'width': 1.5,
        'line-color': '#CBD5E1',
        'target-arrow-color': '#CBD5E1',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(typeLabel)',
        'font-size': 8,
        'font-family': 'system-ui, sans-serif',
        'color': '#9CA3AF',
        'text-background-color': '#FFFFFF',
        'text-background-opacity': 0.85,
        'text-background-padding': 2,
        'text-rotation': 'autorotate',
        'source-distance-from-node': 4,
        'target-distance-from-node': 4,
      },
    },
    {
      selector: 'edge.dimmed',
      style: { 'opacity': 0.1 },
    },
    {
      selector: 'edge.highlighted',
      style: {
        'line-color': '#3B82F6',
        'target-arrow-color': '#3B82F6',
        'width': 2.5,
      },
    },
  ]
}

export default function GraphCanvas({ elements, layout, onNodeClick, selectedId }) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current) return

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements || [],
      style: buildStylesheet(),
      layout: getLayoutOptions(layout || 'cose'),
      wheelSensitivity: 0.3,
      minZoom: 0.05,
      maxZoom: 4,
      boxSelectionEnabled: false,
    })

    cy.on('tap', 'node', (evt) => {
      onNodeClick?.(evt.target.data())
    })

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass('highlighted dimmed')
        onNodeClick?.(null)
      }
    })

    cy.on('mouseover', 'node', (evt) => {
      const neighbourhood = evt.target.closedNeighborhood()
      cy.elements().not(neighbourhood).addClass('dimmed')
      neighbourhood.addClass('highlighted')
    })

    cy.on('mouseout', 'node', () => {
      cy.elements().removeClass('highlighted dimmed')
    })

    cyRef.current = cy
    return () => { cy.destroy(); cyRef.current = null }
  }, [])

  useEffect(() => {
    const cy = cyRef.current
    if (!cy || !elements) return
    cy.elements().remove()
    cy.add(elements)
    const l = cy.layout(getLayoutOptions(layout || 'cose'))
    l.on('layoutstop', () => cy.fit(undefined, 60))
    l.run()
  }, [elements])

  useEffect(() => {
    const cy = cyRef.current
    if (!cy) return
    const l = cy.layout(getLayoutOptions(layout || 'cose'))
    l.on('layoutstop', () => cy.fit(undefined, 60))
    l.run()
  }, [layout])

  useEffect(() => {
    const cy = cyRef.current
    if (!cy) return
    cy.elements().removeClass('highlighted dimmed')
    if (selectedId) {
      const node = cy.getElementById(selectedId)
      if (node.length) {
        const neighbourhood = node.closedNeighborhood()
        cy.elements().not(neighbourhood).addClass('dimmed')
        neighbourhood.addClass('highlighted')
        node.select()
      }
    } else {
      cy.elements().unselect()
    }
  }, [selectedId])

  return <div ref={containerRef} className="cy-container" />
}
