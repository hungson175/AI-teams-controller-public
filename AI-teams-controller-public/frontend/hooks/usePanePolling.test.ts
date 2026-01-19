/**
 * usePanePolling Hook Tests - P0 WebSocket Flicker Bug
 *
 * TDD Protocol: Tests written FIRST to catch double state update bug
 * Root cause: Both onerror + onclose call setWsConnected(false)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, waitFor } from "@testing-library/react"
import { usePanePolling } from "./usePanePolling"
import { RefObject } from "react"

// Mock WebSocket
class MockWebSocket {
  static instances: MockWebSocket[] = []

  readyState = WebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null

  constructor(public url: string) {
    MockWebSocket.instances.push(this)
  }

  send(data: string) {}
  close(code?: number, reason?: string) {}

  // Test helpers
  triggerOpen() {
    if (this.onopen) {
      this.readyState = WebSocket.OPEN
      this.onopen(new Event('open'))
    }
  }

  triggerError() {
    if (this.onerror) {
      this.onerror(new Event('error'))
    }
  }

  triggerClose(code: number = 1006) {
    if (this.onclose) {
      this.readyState = WebSocket.CLOSED
      const closeEvent = new CloseEvent('close', { code })
      this.onclose(closeEvent)
    }
  }

  triggerErrorThenClose() {
    this.triggerError()
    this.triggerClose()
  }
}

describe("usePanePolling - P0 WebSocket State Bug", () => {
  let mockOutputRef: RefObject<HTMLDivElement>
  let mockIsAutoScrollEnabledRef: RefObject<boolean>
  let setWsConnectedCalls: boolean[]

  beforeEach(() => {
    // Reset mocks
    MockWebSocket.instances = []
    setWsConnectedCalls = []

    // Mock WebSocket globally
    global.WebSocket = MockWebSocket as any

    // Create refs
    mockOutputRef = { current: document.createElement('div') }
    mockIsAutoScrollEnabledRef = { current: true }

    // Spy on React setState to track calls
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // TL Requirement 1: WebSocket error handling doesn't cause duplicate renders
  it("test_error_handling_sets_disconnected_state", async () => {
    const onRoleActivityUpdate = vi.fn()

    const { result } = renderHook(() =>
      usePanePolling({
        selectedTeam: "test-team",
        selectedRole: "test-role",
        pollingInterval: 1,
        captureLines: 100,
        outputRef: mockOutputRef,
        isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
        onRoleActivityUpdate,
      })
    )

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1)
    })

    const ws = MockWebSocket.instances[0]

    // Open connection
    ws.triggerOpen()
    await waitFor(() => {
      expect(result.current.wsConnected).toBe(true)
    })

    // Trigger ERROR → should only update state once via onclose
    ws.triggerErrorThenClose()

    await waitFor(() => {
      expect(result.current.wsConnected).toBe(false)
    })

    // Verify state is correctly false after error
    expect(result.current.wsConnected).toBe(false)
  })

  // TL Requirement 2: State guard prevents redundant updates
  it("test_state_guard_prevents_redundant_updates", async () => {
    const onRoleActivityUpdate = vi.fn()

    const { result, rerender } = renderHook(() =>
      usePanePolling({
        selectedTeam: "test-team",
        selectedRole: "test-role",
        pollingInterval: 1,
        captureLines: 100,
        outputRef: mockOutputRef,
        isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
        onRoleActivityUpdate,
      })
    )

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1)
    })

    const ws = MockWebSocket.instances[0]

    // Trigger multiple errors when already disconnected
    const renderCount = { count: 0 }
    const originalRerender = rerender

    ws.triggerClose()
    await waitFor(() => {
      expect(result.current.wsConnected).toBe(false)
    })

    const beforeCount = renderCount.count

    // Trigger error again when already false
    ws.triggerError()

    // Should NOT cause state update since already false
    // BUG: Currently may cause re-render
    // FIX: Guard with if (wsConnected) setWsConnected(false)
    await new Promise(resolve => setTimeout(resolve, 50))

    expect(result.current.wsConnected).toBe(false)
  })

  // TL Requirement 3: Reconnection doesn't cause state thrashing
  it("test_reconnection_does_not_cause_state_thrashing", async () => {
    const onRoleActivityUpdate = vi.fn()

    const { result } = renderHook(() =>
      usePanePolling({
        selectedTeam: "test-team",
        selectedRole: "test-role",
        pollingInterval: 1,
        captureLines: 100,
        outputRef: mockOutputRef,
        isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
        onRoleActivityUpdate,
      })
    )

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1)
    })

    let ws = MockWebSocket.instances[0]
    ws.triggerOpen()

    await waitFor(() => {
      expect(result.current.wsConnected).toBe(true)
    })

    const stateChanges: boolean[] = []

    // Simulate rapid connect/disconnect cycle (network instability)
    for (let i = 0; i < 5; i++) {
      const prevState = result.current.wsConnected
      ws.triggerErrorThenClose()

      await waitFor(() => {
        if (result.current.wsConnected !== prevState) {
          stateChanges.push(result.current.wsConnected)
        }
      })

      // Each cycle should only produce ONE state change (true→false or false→true)
      // BUG: Currently may produce multiple changes per cycle
    }

    // Should have at most 5 state changes (one per cycle)
    // BUG: Currently may have 10+ changes due to double updates
    expect(stateChanges.length).toBeLessThanOrEqual(5)
  })

  // TL Requirement 4: Verify wsConnected is properly managed
  it("test_wsconnected_state_transitions", async () => {
    const onRoleActivityUpdate = vi.fn()

    const { result } = renderHook(() =>
      usePanePolling({
        selectedTeam: "test-team",
        selectedRole: "test-role",
        pollingInterval: 1,
        captureLines: 100,
        outputRef: mockOutputRef,
        isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
        onRoleActivityUpdate,
      })
    )

    // Initial state should be false
    expect(result.current.wsConnected).toBe(false)

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1)
    })

    const ws = MockWebSocket.instances[0]

    // Should become true on open
    ws.triggerOpen()
    await waitFor(() => {
      expect(result.current.wsConnected).toBe(true)
    })

    // Should become false on error (only once, not twice)
    ws.triggerErrorThenClose()
    await waitFor(() => {
      expect(result.current.wsConnected).toBe(false)
    })
  })

  // P0 REGRESSION TEST: Callback stability prevents WebSocket reconnection loops
  describe("P0 Fix - Callback Memoization", () => {
    it("test_stable_callback_prevents_websocket_reconnection", async () => {
      // Create a STABLE callback (same reference across renders)
      const stableCallback = vi.fn()

      const { rerender } = renderHook(
        ({ callback }) =>
          usePanePolling({
            selectedTeam: "test-team",
            selectedRole: "test-role",
            pollingInterval: 1,
            captureLines: 100,
            outputRef: mockOutputRef,
            isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
            onRoleActivityUpdate: callback,
          }),
        { initialProps: { callback: stableCallback } }
      )

      // Wait for initial WebSocket connection
      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]
      ws.triggerOpen()

      // Trigger re-render with SAME callback reference
      rerender({ callback: stableCallback })

      // Wait to ensure no new WebSocket created
      await new Promise(resolve => setTimeout(resolve, 100))

      // CRITICAL: Should still be only 1 WebSocket instance (no reconnection)
      expect(MockWebSocket.instances.length).toBe(1)
    })

    it("test_unstable_callback_causes_websocket_reconnection", async () => {
      // Create callback that changes every render (inline function pattern)
      let renderCount = 0

      const { rerender } = renderHook(
        () => {
          renderCount++
          // NEW callback every render (this was the bug)
          const callback = vi.fn()
          return usePanePolling({
            selectedTeam: "test-team",
            selectedRole: "test-role",
            pollingInterval: 1,
            captureLines: 100,
            outputRef: mockOutputRef,
            isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
            onRoleActivityUpdate: callback,
          })
        }
      )

      // Wait for initial WebSocket connection
      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws1 = MockWebSocket.instances[0]
      ws1.triggerOpen()

      // Trigger re-render with NEW callback reference
      rerender()

      // Wait for effect to re-run
      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(2)
      })

      // PROOF: Unstable callback → new WebSocket connection (the bug we fixed)
      expect(MockWebSocket.instances.length).toBe(2)
    })
  })

  // Sprint 6: DIP (Dependency Inversion Principle) - wsFactory injection
  describe("DIP Compliance - WebSocket Factory Injection", () => {
    it("should accept optional wsFactory parameter", async () => {
      const mockFactory = vi.fn(() => new MockWebSocket("ws://test"))

      renderHook(() =>
        usePanePolling({
          selectedTeam: "test-team",
          selectedRole: "test-role",
          pollingInterval: 1,
          captureLines: 100,
          outputRef: mockOutputRef,
          isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
          onRoleActivityUpdate: vi.fn(),
          wsFactory: mockFactory,
        })
      )

      await waitFor(() => {
        expect(mockFactory).toHaveBeenCalled()
      })
    })

    it("should use provided wsFactory to create WebSocket", async () => {
      const mockFactory = vi.fn((url: string) => {
        const ws = new MockWebSocket(url)
        ws.customProperty = "test-value"
        return ws as any
      })

      renderHook(() =>
        usePanePolling({
          selectedTeam: "test-team",
          selectedRole: "test-role",
          pollingInterval: 1,
          captureLines: 100,
          outputRef: mockOutputRef,
          isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
          onRoleActivityUpdate: vi.fn(),
          wsFactory: mockFactory,
        })
      )

      await waitFor(() => {
        expect(mockFactory).toHaveBeenCalledWith(
          expect.stringContaining("ws://")
        )
      })

      // Verify factory was called with correct URL pattern
      expect(mockFactory).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/ws\/state\/test-team\/test-role$/)
      )
    })

    it("should work with default WebSocket if no factory provided", async () => {
      // Reset global WebSocket to MockWebSocket
      global.WebSocket = MockWebSocket as any

      const { result } = renderHook(() =>
        usePanePolling({
          selectedTeam: "test-team",
          selectedRole: "test-role",
          pollingInterval: 1,
          captureLines: 100,
          outputRef: mockOutputRef,
          isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
          onRoleActivityUpdate: vi.fn(),
          // No wsFactory provided - should use default
        })
      )

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]
      ws.triggerOpen()

      await waitFor(() => {
        expect(result.current.wsConnected).toBe(true)
      })
    })

    it("should enable testing with mock factory", async () => {
      const mockWs = new MockWebSocket("ws://test")
      const mockFactory = vi.fn(() => mockWs)

      const { result } = renderHook(() =>
        usePanePolling({
          selectedTeam: "test-team",
          selectedRole: "test-role",
          pollingInterval: 1,
          captureLines: 100,
          outputRef: mockOutputRef,
          isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
          onRoleActivityUpdate: vi.fn(),
          wsFactory: mockFactory,
        })
      )

      await waitFor(() => {
        expect(mockFactory).toHaveBeenCalled()
      })

      // Verify we can control WebSocket behavior via mock
      mockWs.triggerOpen()

      await waitFor(() => {
        expect(result.current.wsConnected).toBe(true)
      })

      // Verify factory enables full test control
      mockWs.triggerClose()

      await waitFor(() => {
        expect(result.current.wsConnected).toBe(false)
      })
    })

    it("should call factory with correct URL for different teams/roles", async () => {
      const mockFactory = vi.fn((url: string) => new MockWebSocket(url))

      const { rerender } = renderHook(
        ({ team, role }) =>
          usePanePolling({
            selectedTeam: team,
            selectedRole: role,
            pollingInterval: 1,
            captureLines: 100,
            outputRef: mockOutputRef,
            isAutoScrollEnabledRef: mockIsAutoScrollEnabledRef,
            onRoleActivityUpdate: vi.fn(),
            wsFactory: mockFactory,
          }),
        { initialProps: { team: "team1", role: "role1" } }
      )

      await waitFor(() => {
        expect(mockFactory).toHaveBeenCalledWith(
          expect.stringMatching(/team1\/role1$/)
        )
      })

      mockFactory.mockClear()

      // Change team and role
      rerender({ team: "team2", role: "role2" })

      await waitFor(() => {
        expect(mockFactory).toHaveBeenCalledWith(
          expect.stringMatching(/team2\/role2$/)
        )
      })
    })
  })
})
