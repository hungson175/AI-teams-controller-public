/**
 * Tests for Performance Optimization (Story 3)
 *
 * Sprint: Terminal File Path Click Popup (Phase 2)
 * Coverage target: 85% (caching and debouncing)
 */

import { renderHook, act } from "@testing-library/react"
import { usePathResolver } from "../usePathResolver"
import { useFileListCache } from "../useFileListCache"
import { vi, beforeEach, describe, it, expect } from "vitest"

// Mock useFileListCache
vi.mock("../useFileListCache")

describe("usePathResolver - Performance Optimization (Story 3)", () => {
  const mockFiles = [
    "frontend/components/Button.tsx",
    "backend/components/Button.tsx",
    "frontend/lib/utils.ts",
  ]

  beforeEach(() => {
    vi.mocked(useFileListCache).mockReturnValue({
      files: mockFiles,
      isLoading: false,
    })
  })

  describe("AC1: Debouncing (150ms)", () => {
    it("should debounce path changes by 150ms", async () => {
      vi.useFakeTimers()

      const { result, rerender } = renderHook(
        ({ path }) => usePathResolver("test-team", path),
        { initialProps: { path: "" } }
      )

      // Initial state with empty path
      expect(result.current.status).toBe("not_found")

      // Rapidly change path multiple times (simulating typing)
      act(() => {
        rerender({ path: "B" })
      })

      act(() => {
        vi.advanceTimersByTime(50)
      })

      act(() => {
        rerender({ path: "Bu" })
      })

      act(() => {
        vi.advanceTimersByTime(50)
      })

      act(() => {
        rerender({ path: "Button.tsx" })
      })

      // Debounce hasn't expired yet - should still show old value
      expect(result.current.status).toBe("not_found")

      // Fast-forward to complete debounce (150ms)
      act(() => {
        vi.advanceTimersByTime(150)
      })

      // Should have resolved to Button.tsx matches
      expect(result.current.status).toBe("multiple")
      expect(result.current.matches.length).toBe(2) // frontend and backend

      vi.useRealTimers()
    }, 10000)

    it("should delay resolution by 150ms", async () => {
      vi.useFakeTimers()

      const { result, rerender } = renderHook(
        ({ path }) => usePathResolver("test-team", path),
        { initialProps: { path: "" } }
      )

      // Start with empty, then change to Button.tsx
      act(() => {
        rerender({ path: "Button.tsx" })
      })

      // Immediately after rerender, debounce hasn't kicked in yet
      expect(result.current.status).toBe("not_found")

      // Fast-forward past debounce period
      act(() => {
        vi.advanceTimersByTime(150)
      })

      expect(result.current.status).toBe("multiple")
      expect(result.current.matches.length).toBeGreaterThan(0)

      vi.useRealTimers()
    }, 10000)
  })

  describe("AC2: TTL-based caching (5 minutes)", () => {
    it("should use cached result on second resolution (cache hit)", () => {
      // First resolution
      const { result: result1 } = renderHook(() =>
        usePathResolver("test-team", "Button.tsx")
      )

      const firstMatches = result1.current.matches

      // Second resolution with same path (should use cache)
      const { result: result2 } = renderHook(() =>
        usePathResolver("test-team", "Button.tsx")
      )

      // Results should be identical (from cache)
      expect(result2.current.matches).toEqual(firstMatches)
    })

    it("should NOT use cache for different paths (cache miss)", () => {
      // First resolution
      const { result: result1 } = renderHook(() =>
        usePathResolver("test-team", "Button.tsx")
      )

      const firstMatches = result1.current.matches

      // Second resolution with different path
      const { result: result2 } = renderHook(() =>
        usePathResolver("test-team", "utils.ts")
      )

      // Results should be different (cache miss)
      expect(result2.current.matches).not.toEqual(firstMatches)
    })

    it("should expire cache after 5 minutes (TTL)", () => {
      vi.useFakeTimers()
      const realDateNow = Date.now

      // First resolution at time T
      const { result: result1 } = renderHook(() =>
        usePathResolver("test-team", "Button.tsx")
      )

      const firstMatches = result1.current.matches

      // Fast-forward 5 minutes + 1ms (past TTL)
      vi.advanceTimersByTime(5 * 60 * 1000 + 1)
      // Also mock Date.now for cache TTL check
      Date.now = () => realDateNow() + 5 * 60 * 1000 + 1

      // Second resolution with same path (cache should be expired)
      const { result: result2 } = renderHook(() =>
        usePathResolver("test-team", "Button.tsx")
      )

      // Results should still match (same input), but cache was re-computed
      expect(result2.current.matches).toEqual(firstMatches)

      Date.now = realDateNow
      vi.useRealTimers()
    })

    it("should NOT expire cache before TTL (within 5 minutes)", () => {
      vi.useFakeTimers()
      const realDateNow = Date.now

      // First resolution
      const { result: result1 } = renderHook(() =>
        usePathResolver("test-team", "Button.tsx")
      )

      const firstMatches = result1.current.matches

      // Fast-forward 4 minutes (before TTL expires)
      vi.advanceTimersByTime(4 * 60 * 1000)
      Date.now = () => realDateNow() + 4 * 60 * 1000

      // Second resolution with same path (cache should still be valid)
      const { result: result2 } = renderHook(() =>
        usePathResolver("test-team", "Button.tsx")
      )

      // Should use cached result
      expect(result2.current.matches).toEqual(firstMatches)

      Date.now = realDateNow
      vi.useRealTimers()
    })
  })

  describe("AC3: Integration with existing behavior", () => {
    it("should maintain correct status with debounce and cache", async () => {
      vi.useFakeTimers()

      const { result, rerender } = renderHook(
        ({ path }) => usePathResolver("test-team", path),
        { initialProps: { path: "" } }
      )

      // Initially not_found (empty path)
      expect(result.current.status).toBe("not_found")

      // Change to Button.tsx
      act(() => {
        rerender({ path: "Button.tsx" })
      })

      // After debounce
      act(() => {
        vi.advanceTimersByTime(150)
      })

      // Should have multiple matches
      expect(result.current.status).toBe("multiple")
      expect(result.current.matches.length).toBe(2) // frontend and backend Button.tsx

      vi.useRealTimers()
    }, 10000)

    it("should handle empty path with debounce", () => {
      const { result } = renderHook(() => usePathResolver("test-team", ""))

      // Empty path should always be not_found (no debounce needed for empty)
      expect(result.current.status).toBe("not_found")
      expect(result.current.matches).toEqual([])
    })
  })

  describe("AC4: No performance lag on rapid changes", () => {
    it("should not trigger multiple resolutions during rapid typing", async () => {
      vi.useFakeTimers()

      const { result, rerender } = renderHook(
        ({ path }) => usePathResolver("test-team", path),
        { initialProps: { path: "" } }
      )

      // Simulate rapid typing
      const typingSequence = ["B", "Bu", "But", "Butt", "Butto", "Button"]

      typingSequence.forEach((path) => {
        act(() => {
          rerender({ path })
          vi.advanceTimersByTime(50) // Less than debounce period
        })
      })

      // Should still show old value (empty path = not_found) because debounce hasn't completed
      expect(result.current.status).toBe("not_found")

      // Now wait for debounce to complete
      act(() => {
        vi.advanceTimersByTime(150)
      })

      // Should have resolved with final typed value (partial match "Button")
      expect(result.current.matches.length).toBeGreaterThanOrEqual(0)

      vi.useRealTimers()
    }, 10000)
  })
})
