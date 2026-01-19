/**
 * useIsDesktop Hook Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act } from "@testing-library/react"
import { useIsDesktop } from "./use-desktop"

describe("useIsDesktop", () => {
  let originalInnerWidth: number
  let matchMediaListeners: Map<string, () => void>
  let mockMatchMedia: ReturnType<typeof vi.fn>

  beforeEach(() => {
    originalInnerWidth = window.innerWidth
    matchMediaListeners = new Map()

    mockMatchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: window.innerWidth >= 1024,
      media: query,
      addEventListener: (_event: string, callback: () => void) => {
        matchMediaListeners.set(query, callback)
      },
      removeEventListener: (_event: string, _callback: () => void) => {
        matchMediaListeners.delete(query)
      },
    }))

    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: mockMatchMedia,
    })
  })

  afterEach(() => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: originalInnerWidth,
    })
    vi.restoreAllMocks()
  })

  it("should return true when viewport is desktop-sized (1024px+)", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 1024,
    })

    const { result } = renderHook(() => useIsDesktop())
    expect(result.current).toBe(true)
  })

  it("should return true for large desktop (1920px)", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 1920,
    })

    const { result } = renderHook(() => useIsDesktop())
    expect(result.current).toBe(true)
  })

  it("should return false when viewport is mobile-sized (<1024px)", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 768,
    })

    const { result } = renderHook(() => useIsDesktop())
    expect(result.current).toBe(false)
  })

  it("should return false for small mobile (375px)", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 375,
    })

    const { result } = renderHook(() => useIsDesktop())
    expect(result.current).toBe(false)
  })

  it("should return false at breakpoint boundary (1023px)", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 1023,
    })

    const { result } = renderHook(() => useIsDesktop())
    expect(result.current).toBe(false)
  })

  it("should update when viewport changes from mobile to desktop", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 768,
    })

    const { result } = renderHook(() => useIsDesktop())
    expect(result.current).toBe(false)

    // Simulate resize to desktop
    act(() => {
      Object.defineProperty(window, "innerWidth", {
        writable: true,
        value: 1024,
      })
      // Trigger the matchMedia change listener
      const listener = matchMediaListeners.get("(min-width: 1024px)")
      if (listener) listener()
    })

    expect(result.current).toBe(true)
  })

  it("should update when viewport changes from desktop to mobile", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 1200,
    })

    const { result } = renderHook(() => useIsDesktop())
    expect(result.current).toBe(true)

    // Simulate resize to mobile
    act(() => {
      Object.defineProperty(window, "innerWidth", {
        writable: true,
        value: 800,
      })
      const listener = matchMediaListeners.get("(min-width: 1024px)")
      if (listener) listener()
    })

    expect(result.current).toBe(false)
  })

  it("should cleanup event listener on unmount", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 1024,
    })

    const { unmount } = renderHook(() => useIsDesktop())
    expect(matchMediaListeners.size).toBe(1)

    unmount()
    expect(matchMediaListeners.size).toBe(0)
  })
})
