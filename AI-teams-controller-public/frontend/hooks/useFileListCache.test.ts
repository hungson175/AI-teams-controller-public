/**
 * useFileListCache Hook Tests (Sprint 14 - Work Item #1)
 *
 * TDD: Tests written FIRST per Boss requirement
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, waitFor } from "@testing-library/react"
import { useFileListCache } from "./useFileListCache"

// Mock fetch
global.fetch = vi.fn()

describe("useFileListCache", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(global.fetch as any).mockClear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("should fetch file list on mount", async () => {
    const mockFiles = ["src/App.tsx", "src/Button.tsx", "lib/utils.ts"]
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ files: mockFiles }),
    })

    const { result } = renderHook(() => useFileListCache("test-team"))

    // Initial state: loading
    expect(result.current.isLoading).toBe(true)
    expect(result.current.files).toEqual([])

    // Wait for fetch to complete
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Check files loaded
    expect(result.current.files).toEqual(mockFiles)
    expect(result.current.isStale).toBe(false)

    // Verify fetch called with correct endpoint
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/files/test-team/list?limit=10000&show_hidden=false",
      expect.objectContaining({ headers: expect.any(Object) })
    )
  })

  it("should return cached data on subsequent calls with same teamId", async () => {
    const mockFiles = ["src/App.tsx"]
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ files: mockFiles }),
    })

    // First render
    const { result, rerender } = renderHook(() => useFileListCache("test-team"))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.files).toEqual(mockFiles)
    expect(global.fetch).toHaveBeenCalledTimes(1)

    // Rerender - should use cache, not fetch again
    rerender()

    expect(result.current.files).toEqual(mockFiles)
    expect(global.fetch).toHaveBeenCalledTimes(1) // Still only 1 call
  })

  it("should refetch when teamId changes", async () => {
    const mockFiles1 = ["team1/file.ts"]
    const mockFiles2 = ["team2/file.ts"]

    ;(global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ files: mockFiles1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ files: mockFiles2 }),
      })

    const { result, rerender } = renderHook(
      ({ teamId }) => useFileListCache(teamId),
      { initialProps: { teamId: "team1" } }
    )

    await waitFor(() => {
      expect(result.current.files).toEqual(mockFiles1)
    })

    // Change teamId
    rerender({ teamId: "team2" })

    await waitFor(() => {
      expect(result.current.files).toEqual(mockFiles2)
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
  })

  it("should allow manual refetch", async () => {
    const mockFiles1 = ["old.ts"]
    const mockFiles2 = ["new.ts"]

    ;(global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ files: mockFiles1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ files: mockFiles2 }),
      })

    const { result } = renderHook(() => useFileListCache("test-team"))

    await waitFor(() => {
      expect(result.current.files).toEqual(mockFiles1)
    })

    // Manual refetch
    await result.current.refetch()

    await waitFor(() => {
      expect(result.current.files).toEqual(mockFiles2)
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
  })

  it("should handle fetch errors gracefully", async () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {})

    ;(global.fetch as any).mockRejectedValueOnce(new Error("Network error"))

    const { result } = renderHook(() => useFileListCache("test-team"))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Should return empty array on error
    expect(result.current.files).toEqual([])
    expect(result.current.isStale).toBe(false)

    consoleError.mockRestore()
  })

  it("should handle non-ok response gracefully", async () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {})

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    })

    const { result } = renderHook(() => useFileListCache("test-team"))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Should return empty array on error
    expect(result.current.files).toEqual([])

    consoleError.mockRestore()
  })

  it("should mark as stale and refetch on 404 (file not found)", async () => {
    const mockFiles1 = ["file1.ts"]
    const mockFiles2 = ["file1.ts", "file2.ts"]

    ;(global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ files: mockFiles1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ files: mockFiles2 }),
      })

    const { result } = renderHook(() => useFileListCache("test-team"))

    await waitFor(() => {
      expect(result.current.files).toEqual(mockFiles1)
    })

    // Simulate 404 error - mark as stale and refetch
    await result.current.refetch()

    await waitFor(() => {
      expect(result.current.files).toEqual(mockFiles2)
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
  })
})
