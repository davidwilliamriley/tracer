/**
 * useNodeDetail.js — custom hook for fetching node full detail.
 *
 * React concept — custom hooks:
 *   A hook is a function whose name starts with "use" that can call
 *   other React hooks. Custom hooks let you extract and reuse stateful
 *   logic between components. This hook encapsulates the fetch-on-id-change
 *   pattern so NodePanel doesn't need to know about the API layer.
 *
 *   Rules: hooks must only be called inside React components or other hooks.
 *
 * useEffect:
 *   Runs a side effect after render. The dependency array [nodeId] means
 *   it re-runs whenever nodeId changes — i.e. whenever the user clicks
 *   a different node.
 */
import { useState, useEffect } from 'react'
import { getNodeFull } from '../api/graph'

export function useNodeDetail(nodeId) {
  const [node, setNode] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!nodeId) {
      setNode(null)
      return
    }

    let cancelled = false  // prevent stale state if nodeId changes quickly

    const fetchNode = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const data = await getNodeFull(nodeId)
        if (!cancelled) setNode(data)
      } catch (err) {
        if (!cancelled) setError(err.response?.data?.message || 'Failed to load node')
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    fetchNode()

    return () => { cancelled = true }  // cleanup on unmount or id change
  }, [nodeId])

  const refresh = async () => {
    if (!nodeId) return
    setIsLoading(true)
    try {
      const data = await getNodeFull(nodeId)
      setNode(data)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to refresh')
    } finally {
      setIsLoading(false)
    }
  }

  return { node, isLoading, error, refresh }
}
