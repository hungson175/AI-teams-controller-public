/**
 * useContentSearch Hook (Simple File Search Sprint 1 - Story 2)
 *
 * Searches file contents across project files with debouncing
 */

import { useState, useEffect, useRef } from 'react'
import { getAuthHeaders } from '@/lib/auth-utils'

export interface SearchResult {
  path: string
  match_count: number
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
  query: string
}

export interface UseContentSearchReturn {
  results: SearchResult[]
  isLoading: boolean
  error: string | null
}

/**
 * Hook for searching file contents with 300ms debounce
 *
 * @param teamId - Team ID for API endpoint
 * @param query - Search query string
 * @returns Search results, loading state, and error state
 */
export function useContentSearch(
  teamId: string,
  query: string
): UseContentSearchReturn {
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    // Clear results if query is empty
    if (!query || query.trim() === '') {
      setResults([])
      setError(null)
      setIsLoading(false)
      return
    }

    // Debounce: wait 300ms before searching
    const timeoutId = setTimeout(async () => {
      // Cancel previous request if exists
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }

      // Create new abort controller for this request
      abortControllerRef.current = new AbortController()

      setIsLoading(true)
      setError(null)

      try {
        const response = await fetch(
          `/api/files/${teamId}/search?q=${encodeURIComponent(query)}`,
          {
            headers: getAuthHeaders(),
            signal: abortControllerRef.current.signal
          }
        )

        if (!response.ok) {
          throw new Error(`Search failed: ${response.status} ${response.statusText}`)
        }

        const data: SearchResponse = await response.json()
        setResults(data.results)
        setError(null)
      } catch (err) {
        // Don't set error if request was aborted (user is typing)
        if (err instanceof Error && err.name !== 'AbortError') {
          setError(err.message)
          setResults([])
        }
      } finally {
        setIsLoading(false)
      }
    }, 300)

    // Cleanup: cancel timeout and abort request on unmount or query change
    return () => {
      clearTimeout(timeoutId)
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [teamId, query])

  return {
    results,
    isLoading,
    error
  }
}
