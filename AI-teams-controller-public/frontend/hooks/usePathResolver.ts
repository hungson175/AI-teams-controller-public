/**
 * usePathResolver Hook (Sprint 14 - Work Item #2, Phase 2 - Story 3)
 *
 * Resolves file paths using suffix matching algorithm with:
 * - Scoring algorithm (Story 2)
 * - Debouncing (150ms) for performance (Story 3)
 * - TTL-based caching (5 min) for performance (Story 3)
 *
 * Depends on: useFileListCache (WI#1)
 */

import { useMemo, useState, useEffect, useRef } from "react"
import { useFileListCache } from "./useFileListCache"

// Resolution cache with TTL (Story 3 - Performance Optimization)
const resolutionCache = new Map<string, { result: string[], timestamp: number }>()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

/**
 * Clear all cached resolution results for a specific team
 * Called when team changes to prevent stale cache hits
 */
export function clearResolutionCacheForTeam(teamId: string): void {
  const keysToDelete: string[] = []
  for (const key of resolutionCache.keys()) {
    if (key.startsWith(`${teamId}:`)) {
      keysToDelete.push(key)
    }
  }
  keysToDelete.forEach(key => resolutionCache.delete(key))
  console.log(`[usePathResolver] DEBUG: Cleared ${keysToDelete.length} cache entries for team=${teamId}`)
}

/**
 * Get cached resolution result if not expired
 */
function getCachedResolution(key: string): string[] | null {
  const cached = resolutionCache.get(key)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.result
  }
  // Clear expired entry
  if (cached) resolutionCache.delete(key)
  return null
}

/**
 * Set cached resolution result with current timestamp
 */
function setCachedResolution(key: string, result: string[]): void {
  resolutionCache.set(key, { result, timestamp: Date.now() })
}

/**
 * Debounce hook - delays value updates by specified ms
 */
function useDebouncedValue<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

export interface PathMatch {
  path: string
  score: number
}

/**
 * Score a path match based on multiple factors
 *
 * Scoring Algorithm (from TL_SPEC.md - Story 2):
 * 1. Exact filename match (+100)
 * 2. Path segment overlap (+20 per matching segment)
 * 3. Shorter paths preferred (-10 penalty per extra segment)
 *
 * @param match - File path from file list
 * @param parsedPath - Path from terminal output
 * @returns Score (higher = better match)
 */
function scorePath(match: string, parsedPath: string): number {
  let score = 0

  // 1. Exact filename match (+100)
  const matchFilename = match.split("/").pop() || ""
  const parsedFilename = parsedPath.split("/").pop() || ""
  if (matchFilename === parsedFilename) {
    score += 100
  }

  // 2. Path segment overlap (+20 per segment)
  const matchSegments = match.toLowerCase().split("/")
  const parsedSegments = parsedPath.toLowerCase().split("/")
  const overlap = parsedSegments.filter((s) =>
    matchSegments.includes(s)
  ).length
  score += overlap * 20

  // 3. Shorter paths preferred (+10 penalty per extra segment)
  score -= (matchSegments.length - parsedSegments.length) * 10

  return score
}

/**
 * Resolve file path with scoring algorithm
 *
 * Returns matches sorted by score (highest first) with score metadata
 *
 * @param parsedPath - Path from terminal output
 * @param fileList - List of all file paths in project
 * @returns Array of PathMatch sorted by score descending
 */
export function resolveFilePathWithScoring(
  parsedPath: string,
  fileList: string[]
): PathMatch[] {
  if (!parsedPath || !fileList.length) return []

  // Normalize parsed path
  let normalized = parsedPath
  if (normalized.startsWith("./")) {
    normalized = normalized.slice(2)
  } else if (normalized.startsWith("../")) {
    normalized = normalized.replace(/^(\.\.\/)+/, "")
  }
  normalized = normalized.replace(/^\//, "")

  const normalizedLower = normalized.toLowerCase()

  // Find suffix matches
  const matches = fileList.filter((filePath) => {
    const lower = filePath.toLowerCase()
    return lower === normalizedLower || lower.endsWith("/" + normalizedLower)
  })

  // Score and sort matches
  const scoredMatches = matches.map((path) => ({
    path,
    score: scorePath(path, normalized),
  }))

  // Sort by score descending (highest score first)
  return scoredMatches.sort((a, b) => b.score - a.score)
}

export interface PathResolution {
  /** Resolution status */
  status: "loading" | "resolved" | "multiple" | "not_found"
  /** List of matching file paths (sorted by length) */
  matches: string[]
  /** First match if status === 'resolved' */
  resolvedPath?: string
}

/**
 * Resolve file path using suffix matching
 *
 * Algorithm:
 * 1. Normalize: remove ./ or ../ prefix, leading slash
 * 2. Find matches: paths ending with normalized path
 * 3. Rank: shorter paths first (more likely correct)
 *
 * @param parsedPath - Path from terminal output
 * @param fileList - List of all file paths in project
 * @returns Sorted array of matching paths
 */
function resolveFilePath(parsedPath: string, fileList: string[]): string[] {
  if (!parsedPath || !fileList.length) return []

  // Normalize: remove ./ or ../ prefix
  let normalized = parsedPath
  if (normalized.startsWith("./")) {
    normalized = normalized.slice(2)
  } else if (normalized.startsWith("../")) {
    // Can't resolve parent references without context
    // Just remove all ../ prefixes
    normalized = normalized.replace(/^(\.\.\/)+/, "")
  }

  // Remove leading slash for consistent matching
  normalized = normalized.replace(/^\//, "")

  // Case-insensitive matching
  const normalizedLower = normalized.toLowerCase()

  // Find matches: exact suffix match
  const matches = fileList.filter((filePath) => {
    const lower = filePath.toLowerCase()
    return (
      lower === normalizedLower || lower.endsWith("/" + normalizedLower)
    )
  })

  // Rank by path length (shorter = more specific match)
  return matches.sort((a, b) => a.length - b.length)
}

/**
 * Hook for resolving terminal file paths to actual file paths
 *
 * Uses shared file list cache and suffix matching algorithm
 * to resolve relative/absolute/subdirectory paths.
 *
 * Performance optimizations (Story 3):
 * - Debouncing (150ms) to prevent excessive re-resolution
 * - TTL-based caching (5 min) to avoid re-computing same paths
 *
 * @param teamId - Team ID for file list cache
 * @param parsedPath - Path extracted from terminal output
 * @returns PathResolution with status and matches
 */
export function usePathResolver(
  teamId: string,
  parsedPath: string
): PathResolution {
  const { files, isLoading } = useFileListCache(teamId)

  // Story 3: Debounce parsedPath (150ms) to prevent rapid re-resolution
  const debouncedPath = useDebouncedValue(parsedPath, 150)

  // Resolve paths using memoization + caching
  const resolution = useMemo(() => {
    // DEBUG: Log resolution attempt
    console.log(`[usePathResolver] DEBUG: teamId=${teamId}, path=${debouncedPath}, isLoading=${isLoading}, filesCount=${files.length}`)

    // While loading file list OR files not yet loaded
    // CRITICAL: Don't resolve while files array is empty - this prevents caching "not found" before files load
    if (isLoading || files.length === 0) {
      console.log(`[usePathResolver] DEBUG: Files not ready (isLoading=${isLoading}, filesCount=${files.length}), returning loading status`)
      return {
        status: "loading" as const,
        matches: [],
        resolvedPath: undefined,
      }
    }

    // Empty path
    if (!debouncedPath) {
      return {
        status: "not_found" as const,
        matches: [],
        resolvedPath: undefined,
      }
    }

    // Story 3: Check cache first
    const cacheKey = `${teamId}:${debouncedPath}`
    const cachedMatches = getCachedResolution(cacheKey)

    let matches: string[]
    if (cachedMatches !== null) {
      // Cache hit - use cached result
      matches = cachedMatches
      console.log(`[usePathResolver] DEBUG: Cache HIT for ${cacheKey}, matches=${matches.length}`)
    } else {
      // Cache miss - resolve using algorithm
      matches = resolveFilePath(debouncedPath, files)
      console.log(`[usePathResolver] DEBUG: Cache MISS for ${cacheKey}, found ${matches.length} matches`)
      if (matches.length > 0) {
        console.log(`[usePathResolver] DEBUG: First 3 matches:`, matches.slice(0, 3))
      } else {
        // Log sample files to debug
        console.log(`[usePathResolver] DEBUG: No matches. Sample files:`, files.slice(0, 5))
      }

      // Only cache results when files are loaded (prevents caching "not found" before files load)
      setCachedResolution(cacheKey, matches)
    }

    // Determine status based on number of matches
    if (matches.length === 0) {
      console.log(`[usePathResolver] DEBUG: NOT_FOUND for path=${debouncedPath}`)
      return {
        status: "not_found" as const,
        matches: [],
        resolvedPath: undefined,
      }
    } else if (matches.length === 1) {
      return {
        status: "resolved" as const,
        matches,
        resolvedPath: matches[0],
      }
    } else {
      return {
        status: "multiple" as const,
        matches,
        resolvedPath: undefined,
      }
    }
  }, [files, isLoading, debouncedPath, teamId])

  return resolution
}
