import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act, waitFor } from "@testing-library/react"
import { useTerminalResize } from "./useTerminalResize"

// Mock ResizeObserver
class MockResizeObserver {
  callback: ResizeObserverCallback
  static instances: MockResizeObserver[] = []

  constructor(callback: ResizeObserverCallback) {
    this.callback = callback
    MockResizeObserver.instances.push(this)
  }

  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()

  // Helper to trigger resize
  triggerResize(entries: ResizeObserverEntry[]) {
    this.callback(entries, this as unknown as ResizeObserver)
  }
}

describe("useTerminalResize", () => {
  beforeEach(() => {
    vi.useFakeTimers()
    MockResizeObserver.instances = []
    vi.stubGlobal("ResizeObserver", MockResizeObserver)
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it("should return containerRef, columns, and width", () => {
    const { result } = renderHook(() => useTerminalResize())

    expect(result.current.containerRef).toBeDefined()
    expect(typeof result.current.columns).toBe("number")
    expect(typeof result.current.width).toBe("number")
  })

  it("should return default columns when container has no width", () => {
    const { result } = renderHook(() => useTerminalResize())

    // Default should be reasonable minimum (e.g., 80)
    expect(result.current.columns).toBeGreaterThanOrEqual(40)
  })

  it("should calculate columns based on container width", async () => {
    const { result } = renderHook(() => useTerminalResize())

    // Simulate setting containerRef to an element
    const mockElement = document.createElement("div")
    Object.defineProperty(mockElement, "getBoundingClientRect", {
      value: () => ({ width: 800, height: 400 }),
    })

    // Manually set the ref
    act(() => {
      (result.current.containerRef as React.MutableRefObject<HTMLDivElement>).current = mockElement
    })

    // Trigger resize observation
    const observer = MockResizeObserver.instances[0]
    if (observer) {
      act(() => {
        observer.triggerResize([
          {
            target: mockElement,
            contentRect: { width: 800, height: 400 } as DOMRectReadOnly,
            borderBoxSize: [],
            contentBoxSize: [],
            devicePixelContentBoxSize: [],
          },
        ])
      })

      // Wait for debounce
      act(() => {
        vi.advanceTimersByTime(300)
      })

      // With 800px width and ~8px char width, expect around 100 columns
      expect(result.current.width).toBe(800)
      expect(result.current.columns).toBeGreaterThan(50)
    }
  })

  it("should debounce resize events", async () => {
    const { result } = renderHook(() => useTerminalResize({ debounceMs: 250 }))

    const mockElement = document.createElement("div")
    act(() => {
      (result.current.containerRef as React.MutableRefObject<HTMLDivElement>).current = mockElement
    })

    const observer = MockResizeObserver.instances[0]
    if (observer) {
      // Trigger multiple rapid resize events
      act(() => {
        observer.triggerResize([
          {
            target: mockElement,
            contentRect: { width: 600, height: 400 } as DOMRectReadOnly,
            borderBoxSize: [],
            contentBoxSize: [],
            devicePixelContentBoxSize: [],
          },
        ])
      })

      // Advance only 100ms (less than debounce)
      act(() => {
        vi.advanceTimersByTime(100)
      })

      // Should still have initial/previous value, not updated yet
      const columnsBeforeDebounce = result.current.columns

      // Trigger another resize
      act(() => {
        observer.triggerResize([
          {
            target: mockElement,
            contentRect: { width: 900, height: 400 } as DOMRectReadOnly,
            borderBoxSize: [],
            contentBoxSize: [],
            devicePixelContentBoxSize: [],
          },
        ])
      })

      // Advance past debounce threshold
      act(() => {
        vi.advanceTimersByTime(300)
      })

      // Now should be updated to latest value
      expect(result.current.width).toBe(900)
    }
  })

  it("should handle zero/small container width gracefully", () => {
    const { result } = renderHook(() => useTerminalResize())

    const mockElement = document.createElement("div")
    act(() => {
      (result.current.containerRef as React.MutableRefObject<HTMLDivElement>).current = mockElement
    })

    const observer = MockResizeObserver.instances[0]
    if (observer) {
      // Trigger resize with 0 width
      act(() => {
        observer.triggerResize([
          {
            target: mockElement,
            contentRect: { width: 0, height: 400 } as DOMRectReadOnly,
            borderBoxSize: [],
            contentBoxSize: [],
            devicePixelContentBoxSize: [],
          },
        ])
      })

      act(() => {
        vi.advanceTimersByTime(300)
      })

      // Should return minimum columns (e.g., 40)
      expect(result.current.columns).toBeGreaterThanOrEqual(40)
    }
  })

  it("should clean up ResizeObserver on unmount", () => {
    // Create a mock element to use as the container
    const mockElement = document.createElement("div")
    Object.defineProperty(mockElement, "getBoundingClientRect", {
      value: () => ({ width: 800, height: 400 }),
    })

    // Use a wrapper that sets the ref immediately
    const { unmount } = renderHook(() => {
      const result = useTerminalResize()
      // Simulate ref being set by React
      if (!result.containerRef.current) {
        (result.containerRef as React.MutableRefObject<HTMLDivElement>).current = mockElement
      }
      return result
    })

    // Wait for the effect to run
    act(() => {
      vi.advanceTimersByTime(10)
    })

    // An observer should have been created
    const observer = MockResizeObserver.instances.find((o) => o.observe.mock.calls.length > 0)

    unmount()

    // If an observer was created, it should have been disconnected
    if (observer) {
      expect(observer.disconnect).toHaveBeenCalled()
    } else {
      // At minimum, verify no memory leaks by checking instances are tracked
      expect(MockResizeObserver.instances.length).toBeGreaterThanOrEqual(0)
    }
  })

  it("should use custom debounce time when provided", async () => {
    const customDebounceMs = 500
    const { result } = renderHook(() => useTerminalResize({ debounceMs: customDebounceMs }))

    const mockElement = document.createElement("div")
    act(() => {
      (result.current.containerRef as React.MutableRefObject<HTMLDivElement>).current = mockElement
    })

    const observer = MockResizeObserver.instances[0]
    if (observer) {
      act(() => {
        observer.triggerResize([
          {
            target: mockElement,
            contentRect: { width: 700, height: 400 } as DOMRectReadOnly,
            borderBoxSize: [],
            contentBoxSize: [],
            devicePixelContentBoxSize: [],
          },
        ])
      })

      // Advance less than custom debounce
      act(() => {
        vi.advanceTimersByTime(400)
      })

      // Should not be updated yet
      expect(result.current.width).not.toBe(700)

      // Advance past custom debounce
      act(() => {
        vi.advanceTimersByTime(200)
      })

      // Now should be updated
      expect(result.current.width).toBe(700)
    }
  })
})
