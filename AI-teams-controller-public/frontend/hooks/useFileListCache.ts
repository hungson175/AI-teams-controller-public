/**
 * useFileListCache Hook (Sprint 14 - Work Item #1)
 *
 * Shared cache for file list across components
 * Reused from FileSearch, shared with path resolution
 *
 * Uses MODULE-LEVEL cache to share data across all hook instances.
 * This prevents each TerminalFileLink from having its own empty state.
 */

import { useState, useEffect, useCallback, useRef } from "react"
import { getAuthHeaders } from "@/lib/auth-utils"

// MODULE-LEVEL SHARED CACHE
// Key: teamId, Value: { files, timestamp, promise }
const fileListCache = new Map<string, {
  files: string[],
  timestamp: number,
  fetchPromise?: Promise<string[]>
}>()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

export interface FileListCache {
  /** List of all file paths in project */
  files: string[]
  /** Loading state */
  isLoading: boolean
  /** Whether cache is stale (needs refresh) */
  isStale: boolean
  /** Manual refetch function */
  refetch: () => Promise<void>
}

/**
 * Hook for fetching and caching file list
 *
 * Fetches file list on mount and caches it in memory.
 * Shared between FileSearch and path resolution.
 *
 * @param teamId - Team ID for API call
 * @returns FileListCache object with files, loading state, and refetch function
 */
/**
 * Fetch files for a team, using shared cache
 * Returns a promise that resolves to the file list
 */
async function fetchFilesForTeam(teamId: string): Promise<string[]> {
  console.log(`[useFileListCache] DEBUG: Fetching files for team=${teamId}`)

  try {
    const response = await fetch(
      `/api/files/${teamId}/list?limit=10000&show_hidden=false`,
      { headers: getAuthHeaders() }
    )

    if (!response.ok) {
      console.error(`[useFileListCache] Failed to fetch file list: ${response.status}`)
      return []
    }

    const data = await response.json()
    const filePaths = (data.files || []).map((f: {path: string}) => f.path)
    console.log(`[useFileListCache] DEBUG: Loaded ${filePaths.length} files for team=${teamId}`)
    console.log(`[useFileListCache] DEBUG: Sample paths:`, filePaths.slice(0, 5))

    return filePaths
  } catch (error) {
    console.error("[useFileListCache] Error fetching file list:", error)
    return []
  }
}

export function useFileListCache(teamId: string): FileListCache {
  const [files, setFiles] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isStale, setIsStale] = useState(false)

  // Use the shared module-level cache
  useEffect(() => {
    if (!teamId) {
      console.log(`[useFileListCache] DEBUG: No teamId, skipping fetch`)
      setFiles([])
      setIsLoading(false)
      return
    }

    console.log(`[useFileListCache] DEBUG: teamId changed to '${teamId}'`)

    // Check shared cache first
    const cached = fileListCache.get(teamId)
    const now = Date.now()

    if (cached && (now - cached.timestamp) < CACHE_TTL) {
      // Cache hit - use cached files
      console.log(`[useFileListCache] DEBUG: Cache HIT for team=${teamId}, files=${cached.files.length}`)
      setFiles(cached.files)
      setIsLoading(false)
      return
    }

    // Cache miss or expired - need to fetch
    console.log(`[useFileListCache] DEBUG: Cache MISS for team=${teamId}`)
    setIsLoading(true)

    // Check if there's already a pending fetch for this team
    if (cached?.fetchPromise) {
      console.log(`[useFileListCache] DEBUG: Reusing pending fetch for team=${teamId}`)
      cached.fetchPromise.then(filePaths => {
        setFiles(filePaths)
        setIsLoading(false)
      })
      return
    }

    // Start new fetch
    const fetchPromise = fetchFilesForTeam(teamId)

    // Store the promise in cache to prevent duplicate fetches
    fileListCache.set(teamId, {
      files: cached?.files || [],
      timestamp: cached?.timestamp || 0,
      fetchPromise,
    })

    fetchPromise.then(filePaths => {
      // Update shared cache with results
      fileListCache.set(teamId, {
        files: filePaths,
        timestamp: Date.now(),
        fetchPromise: undefined,
      })
      setFiles(filePaths)
      setIsLoading(false)
    })
  }, [teamId])

  // Manual refetch function - clears cache and fetches fresh
  const refetch = useCallback(async () => {
    if (!teamId) return

    // Clear cache entry to force fresh fetch
    fileListCache.delete(teamId)

    setIsLoading(true)
    const filePaths = await fetchFilesForTeam(teamId)

    // Update cache
    fileListCache.set(teamId, {
      files: filePaths,
      timestamp: Date.now(),
    })

    setFiles(filePaths)
    setIsLoading(false)
  }, [teamId])

  return {
    files,
    isLoading,
    isStale,
    refetch,
  }
}
