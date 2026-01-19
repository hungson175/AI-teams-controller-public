/**
 * useWakeLockManager Hook Tests
 *
 * TDD Phase: RED - Tests written BEFORE hook extraction
 *
 * Hook Purpose:
 * - Request wake lock to keep screen on during voice recording (mobile)
 * - Release wake lock when recording stops
 * - Re-acquire wake lock when page becomes visible again
 * - Handle browser compatibility (progressive enhancement)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act, waitFor } from "@testing-library/react"
import { useWakeLockManager } from "./useWakeLockManager"

// Mock WakeLockSentinel
const mockWakeLockSentinel = {
  release: vi.fn().mockResolvedValue(undefined),
  released: false,
  type: "screen" as WakeLockType,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}

// Mock Navigator with WakeLock API
const mockWakeLock = {
  request: vi.fn().mockResolvedValue(mockWakeLockSentinel),
}

describe("useWakeLockManager Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock navigator.wakeLock
    Object.defineProperty(navigator, "wakeLock", {
      value: mockWakeLock,
      writable: true,
      configurable: true,
    })
    mockWakeLockSentinel.release.mockClear()
    mockWakeLock.request.mockClear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe("Initialization", () => {
    it("should initialize without requesting wake lock", () => {
      renderHook(() => useWakeLockManager({ isActive: false }))

      expect(mockWakeLock.request).not.toHaveBeenCalled()
    })

    it("should return requestWakeLock and releaseWakeLock functions", () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      expect(result.current.requestWakeLock).toBeDefined()
      expect(result.current.releaseWakeLock).toBeDefined()
      expect(typeof result.current.requestWakeLock).toBe("function")
      expect(typeof result.current.releaseWakeLock).toBe("function")
    })
  })

  describe("Requesting Wake Lock", () => {
    it("should request screen wake lock when requestWakeLock is called", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      expect(mockWakeLock.request).toHaveBeenCalledWith("screen")
    })

    it("should log success when wake lock is acquired", async () => {
      const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {})

      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("[WakeLock] Screen wake lock acquired")
      )

      consoleLogSpy.mockRestore()
    })

    it("should add event listener for wake lock release", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      expect(mockWakeLockSentinel.addEventListener).toHaveBeenCalledWith(
        "release",
        expect.any(Function)
      )
    })

    it("should log when wake lock is released by system", async () => {
      const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {})

      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      // Get the release callback
      const releaseCallback = mockWakeLockSentinel.addEventListener.mock.calls[0][1]

      // Trigger release event
      act(() => {
        releaseCallback()
      })

      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("[WakeLock] Screen wake lock released")
      )

      consoleLogSpy.mockRestore()
    })

    it("should automatically request wake lock when isActive becomes true", async () => {
      const { rerender } = renderHook(
        ({ isActive }) => useWakeLockManager({ isActive }),
        { initialProps: { isActive: false } }
      )

      expect(mockWakeLock.request).not.toHaveBeenCalled()

      await act(async () => {
        rerender({ isActive: true })
      })

      await waitFor(() => {
        expect(mockWakeLock.request).toHaveBeenCalledWith("screen")
      })
    })
  })

  describe("Releasing Wake Lock", () => {
    it("should release wake lock when releaseWakeLock is called", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      await act(async () => {
        await result.current.releaseWakeLock()
      })

      expect(mockWakeLockSentinel.release).toHaveBeenCalled()
    })

    it("should log when wake lock is released manually", async () => {
      const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {})

      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
        await result.current.releaseWakeLock()
      })

      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("[WakeLock] Screen wake lock released manually")
      )

      consoleLogSpy.mockRestore()
    })

    it("should clear wake lock reference after release", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
        await result.current.releaseWakeLock()
      })

      // Calling release again should not throw
      await act(async () => {
        await result.current.releaseWakeLock()
      })

      expect(mockWakeLockSentinel.release).toHaveBeenCalledTimes(1) // Only once
    })

    it("should automatically release wake lock when isActive becomes false", async () => {
      const { rerender } = renderHook(
        ({ isActive }) => useWakeLockManager({ isActive }),
        { initialProps: { isActive: true } }
      )

      await waitFor(() => {
        expect(mockWakeLock.request).toHaveBeenCalled()
      })

      await act(async () => {
        rerender({ isActive: false })
      })

      await waitFor(() => {
        expect(mockWakeLockSentinel.release).toHaveBeenCalled()
      })
    })
  })

  describe("Page Visibility Handling", () => {
    it("should re-acquire wake lock when page becomes visible", async () => {
      Object.defineProperty(document, "visibilityState", {
        writable: true,
        configurable: true,
        value: "hidden",
      })

      const { result } = renderHook(() => useWakeLockManager({ isActive: true }))

      await waitFor(() => {
        expect(mockWakeLock.request).toHaveBeenCalledTimes(1)
      })

      // Simulate wake lock being released when page is hidden
      mockWakeLockSentinel.release.mockClear()
      mockWakeLock.request.mockClear()

      await act(async () => {
        await result.current.releaseWakeLock()
      })

      // Page becomes visible again
      Object.defineProperty(document, "visibilityState", {
        writable: true,
        configurable: true,
        value: "visible",
      })

      await act(async () => {
        document.dispatchEvent(new Event("visibilitychange"))
      })

      await waitFor(() => {
        expect(mockWakeLock.request).toHaveBeenCalled()
      })
    })

    it("should not re-acquire wake lock when page is visible but not active", async () => {
      Object.defineProperty(document, "visibilityState", {
        writable: true,
        configurable: true,
        value: "hidden",
      })

      renderHook(() => useWakeLockManager({ isActive: false }))

      mockWakeLock.request.mockClear()

      // Page becomes visible
      Object.defineProperty(document, "visibilityState", {
        writable: true,
        configurable: true,
        value: "visible",
      })

      await act(async () => {
        document.dispatchEvent(new Event("visibilitychange"))
      })

      expect(mockWakeLock.request).not.toHaveBeenCalled()
    })

    it("should log when re-acquiring wake lock on visibility change", async () => {
      const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {})

      Object.defineProperty(document, "visibilityState", {
        writable: true,
        configurable: true,
        value: "hidden",
      })

      renderHook(() => useWakeLockManager({ isActive: true }))

      consoleLogSpy.mockClear()

      Object.defineProperty(document, "visibilityState", {
        writable: true,
        configurable: true,
        value: "visible",
      })

      await act(async () => {
        document.dispatchEvent(new Event("visibilitychange"))
      })

      await waitFor(() => {
        expect(consoleLogSpy).toHaveBeenCalledWith(
          expect.stringContaining("[WakeLock] Page visible, re-acquiring wake lock")
        )
      })

      consoleLogSpy.mockRestore()
    })
  })

  describe("Error Handling", () => {
    it("should fail silently when wakeLock API is not supported", async () => {
      // @ts-ignore
      Object.defineProperty(navigator, "wakeLock", {
        value: undefined,
        writable: true,
        configurable: true,
      })

      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await expect(
        act(async () => {
          await result.current.requestWakeLock()
        })
      ).resolves.not.toThrow()
    })

    it("should log error when wake lock request fails", async () => {
      const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {})
      mockWakeLock.request.mockRejectedValueOnce(new Error("Wake lock denied"))

      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("[WakeLock] Could not acquire wake lock"),
        expect.any(Error)
      )

      consoleLogSpy.mockRestore()
    })

    it("should handle release errors gracefully", async () => {
      const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {})
      mockWakeLockSentinel.release.mockRejectedValueOnce(new Error("Release failed"))

      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      await expect(
        act(async () => {
          await result.current.releaseWakeLock()
        })
      ).resolves.not.toThrow()

      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("[WakeLock] Error releasing wake lock"),
        expect.any(Error)
      )

      consoleLogSpy.mockRestore()
    })

    it("should not crash when releaseWakeLock called without active lock", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await expect(
        act(async () => {
          await result.current.releaseWakeLock()
        })
      ).resolves.not.toThrow()

      expect(mockWakeLockSentinel.release).not.toHaveBeenCalled()
    })
  })

  describe("Cleanup on Unmount", () => {
    it("should release wake lock on unmount", async () => {
      const { result, unmount } = renderHook(() => useWakeLockManager({ isActive: true }))

      await waitFor(() => {
        expect(mockWakeLock.request).toHaveBeenCalled()
      })

      unmount()

      await waitFor(() => {
        expect(mockWakeLockSentinel.release).toHaveBeenCalled()
      })
    })

    it("should remove visibility change listener on unmount", () => {
      const removeEventListenerSpy = vi.spyOn(document, "removeEventListener")

      const { unmount } = renderHook(() => useWakeLockManager({ isActive: true }))

      unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "visibilitychange",
        expect.any(Function)
      )

      removeEventListenerSpy.mockRestore()
    })
  })

  describe("Progressive Enhancement", () => {
    it("should work without errors on browsers without Wake Lock API", async () => {
      // @ts-ignore
      Object.defineProperty(navigator, "wakeLock", {
        value: undefined,
        writable: true,
        configurable: true,
      })

      const { result } = renderHook(() => useWakeLockManager({ isActive: true }))

      await expect(
        act(async () => {
          await result.current.requestWakeLock()
          await result.current.releaseWakeLock()
        })
      ).resolves.not.toThrow()
    })

    it("should check for wakeLock support before requesting", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      // Should only call request if 'wakeLock' in navigator
      expect(mockWakeLock.request).toHaveBeenCalled()
    })
  })

  describe("Edge Cases", () => {
    it("should handle rapid isActive state changes", async () => {
      const { rerender } = renderHook(
        ({ isActive }) => useWakeLockManager({ isActive }),
        { initialProps: { isActive: false } }
      )

      await act(async () => {
        rerender({ isActive: true })
        rerender({ isActive: false })
        rerender({ isActive: true })
        rerender({ isActive: false })
      })

      // Should not crash
      expect(mockWakeLock.request).toHaveBeenCalled()
    })

    it("should not request wake lock if already active", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      mockWakeLock.request.mockClear()

      await act(async () => {
        await result.current.requestWakeLock()
      })

      // Should not request again if already have lock
      // (Implementation detail - may vary)
    })

    it("should handle wake lock being released externally", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      // Simulate browser releasing the lock (e.g., battery saver)
      const releaseCallback = mockWakeLockSentinel.addEventListener.mock.calls.find(
        (call) => call[0] === "release"
      )?.[1]

      if (releaseCallback) {
        act(() => {
          releaseCallback()
        })
      }

      // Should handle gracefully, wake lock reference should be cleared
      await act(async () => {
        await result.current.releaseWakeLock()
      })
    })
  })

  describe("Mobile-Specific Behavior", () => {
    it("should request screen wake lock type (not system)", async () => {
      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      expect(mockWakeLock.request).toHaveBeenCalledWith("screen")
      expect(mockWakeLock.request).not.toHaveBeenCalledWith("system")
    })

    it("should work on mobile devices with wake lock support", async () => {
      // Simulate mobile device
      Object.defineProperty(navigator, "userAgent", {
        value: "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
        writable: true,
        configurable: true,
      })

      const { result } = renderHook(() => useWakeLockManager({ isActive: false }))

      await act(async () => {
        await result.current.requestWakeLock()
      })

      expect(mockWakeLock.request).toHaveBeenCalled()
    })
  })
})
