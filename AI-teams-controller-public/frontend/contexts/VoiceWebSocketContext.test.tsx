/**
 * VoiceWebSocketContext Tests (Sprint 6: SRP - Single Responsibility Principle)
 *
 * Extracted from VoiceFeedbackContext as part of SOLID refactoring.
 * Responsibility: WebSocket connection management ONLY
 *
 * TDD Protocol: Tests written FIRST
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, waitFor, act } from "@testing-library/react"
import { VoiceWebSocketProvider, useVoiceWebSocket } from "./VoiceWebSocketContext"
import { ReactNode } from "react"

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
      this.onopen(new Event("open"))
    }
  }

  triggerMessage(data: string) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent("message", { data }))
    }
  }

  triggerClose(code: number = 1000) {
    if (this.onclose) {
      this.readyState = WebSocket.CLOSED
      this.onclose(new CloseEvent("close", { code }))
    }
  }

  triggerError() {
    if (this.onerror) {
      this.onerror(new Event("error"))
    }
  }
}

describe("VoiceWebSocketContext - SRP Compliance", () => {
  let wrapper: ({ children }: { children: ReactNode }) => JSX.Element

  beforeEach(() => {
    MockWebSocket.instances = []
    global.WebSocket = MockWebSocket as any
    vi.useFakeTimers()

    wrapper = ({ children }: { children: ReactNode }) => (
      <VoiceWebSocketProvider>{children}</VoiceWebSocketProvider>
    )
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  describe("SRP: WebSocket Connection Management Only", () => {
    it("should provide WebSocket connection interface", () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      // Should expose ONLY connection-related state and methods
      expect(result.current).toHaveProperty("isConnected")
      expect(result.current).toHaveProperty("connect")
      expect(result.current).toHaveProperty("disconnect")
      expect(result.current).toHaveProperty("sendMessage")

      // Should NOT have audio/notification concerns (SRP violation)
      expect(result.current).not.toHaveProperty("playAudio")
      expect(result.current).not.toHaveProperty("notifications")
      expect(result.current).not.toHaveProperty("voiceFeedbackMode")
    })

    it("should connect to WebSocket on mount", async () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      expect(result.current.isConnected).toBe(false)

      const ws = MockWebSocket.instances[0]
      act(() => {
        ws.triggerOpen()
      })

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })
    })

    it("should disconnect WebSocket on unmount", async () => {
      const { unmount } = renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]
      const closeSpy = vi.spyOn(ws, "close")

      unmount()

      expect(closeSpy).toHaveBeenCalled()
    })
  })

  describe("Connection State Management", () => {
    it("should update isConnected on open", async () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      expect(result.current.isConnected).toBe(false)

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      act(() => {
        MockWebSocket.instances[0].triggerOpen()
      })

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })
    })

    it("should update isConnected on close", async () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]

      act(() => {
        ws.triggerOpen()
      })

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })

      act(() => {
        ws.triggerClose()
      })

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
      })
    })
  })

  describe("Auto-Reconnection", () => {
    it("should auto-reconnect after 5 seconds on abnormal close", async () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]

      act(() => {
        ws.triggerOpen()
      })

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })

      // Abnormal close (code !== 1000)
      act(() => {
        ws.triggerClose(1006)
      })

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
      })

      // Advance timers by 5 seconds
      act(() => {
        vi.advanceTimersByTime(5000)
      })

      // Should create new WebSocket
      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(2)
      })
    })

    it("should NOT auto-reconnect on normal close (code 1000)", async () => {
      renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]

      act(() => {
        ws.triggerOpen()
        ws.triggerClose(1000) // Normal close
      })

      act(() => {
        vi.advanceTimersByTime(10000)
      })

      // Should still be only 1 instance (no reconnection)
      expect(MockWebSocket.instances.length).toBe(1)
    })
  })

  describe("Keepalive Ping/Pong", () => {
    it("should send ping every 30 seconds when connected", async () => {
      renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]
      const sendSpy = vi.spyOn(ws, "send")

      act(() => {
        ws.triggerOpen()
      })

      // Advance 30 seconds
      act(() => {
        vi.advanceTimersByTime(30000)
      })

      expect(sendSpy).toHaveBeenCalledWith("ping")

      // Advance another 30 seconds
      act(() => {
        vi.advanceTimersByTime(30000)
      })

      expect(sendSpy).toHaveBeenCalledTimes(2)
    })

    it("should stop ping interval on disconnect", async () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]
      const sendSpy = vi.spyOn(ws, "send")

      act(() => {
        ws.triggerOpen()
      })

      act(() => {
        result.current.disconnect()
      })

      act(() => {
        vi.advanceTimersByTime(60000)
      })

      // Should NOT send pings after disconnect
      expect(sendSpy).not.toHaveBeenCalledWith("ping")
    })

    it("should handle pong response", async () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]

      act(() => {
        ws.triggerOpen()
        ws.triggerMessage("pong")
      })

      // Should not crash, pong is just acknowledgment
      expect(result.current.isConnected).toBe(true)
    })
  })

  describe("Message Handling", () => {
    it("should expose onMessage callback for receiving messages", async () => {
      const onMessage = vi.fn()

      const customWrapper = ({ children }: { children: ReactNode }) => (
        <VoiceWebSocketProvider onMessage={onMessage}>{children}</VoiceWebSocketProvider>
      )

      renderHook(() => useVoiceWebSocket(), { wrapper: customWrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]

      act(() => {
        ws.triggerOpen()
        ws.triggerMessage(JSON.stringify({ type: "test", data: "hello" }))
      })

      await waitFor(() => {
        expect(onMessage).toHaveBeenCalledWith({ type: "test", data: "hello" })
      })
    })

    it("should ignore pong messages (keepalive)", async () => {
      const onMessage = vi.fn()

      const customWrapper = ({ children }: { children: ReactNode }) => (
        <VoiceWebSocketProvider onMessage={onMessage}>{children}</VoiceWebSocketProvider>
      )

      renderHook(() => useVoiceWebSocket(), { wrapper: customWrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]

      act(() => {
        ws.triggerOpen()
        ws.triggerMessage("pong")
      })

      // Should NOT call onMessage for pong
      expect(onMessage).not.toHaveBeenCalled()
    })

    it("should handle malformed JSON gracefully", async () => {
      const onMessage = vi.fn()
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})

      const customWrapper = ({ children }: { children: ReactNode }) => (
        <VoiceWebSocketProvider onMessage={onMessage}>{children}</VoiceWebSocketProvider>
      )

      renderHook(() => useVoiceWebSocket(), { wrapper: customWrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]

      act(() => {
        ws.triggerOpen()
        ws.triggerMessage("invalid json")
      })

      // Should log error but not crash
      expect(consoleErrorSpy).toHaveBeenCalled()
      expect(onMessage).not.toHaveBeenCalled()

      consoleErrorSpy.mockRestore()
    })
  })

  describe("Send Message", () => {
    it("should send message when connected", async () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]
      const sendSpy = vi.spyOn(ws, "send")

      act(() => {
        ws.triggerOpen()
      })

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })

      act(() => {
        result.current.sendMessage({ type: "test", data: "hello" })
      })

      expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({ type: "test", data: "hello" }))
    })

    it("should NOT send message when disconnected", async () => {
      const { result } = renderHook(() => useVoiceWebSocket(), { wrapper })

      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(1)
      })

      const ws = MockWebSocket.instances[0]
      const sendSpy = vi.spyOn(ws, "send")

      act(() => {
        result.current.sendMessage({ type: "test", data: "hello" })
      })

      // Should NOT send when not connected
      expect(sendSpy).not.toHaveBeenCalled()
    })
  })

  describe("DIP: WebSocket Factory Injection", () => {
    it("should accept optional wsFactory parameter", async () => {
      const mockFactory = vi.fn((url: string) => new MockWebSocket(url))

      const customWrapper = ({ children }: { children: ReactNode }) => (
        <VoiceWebSocketProvider wsFactory={mockFactory}>{children}</VoiceWebSocketProvider>
      )

      renderHook(() => useVoiceWebSocket(), { wrapper: customWrapper })

      await waitFor(() => {
        expect(mockFactory).toHaveBeenCalled()
      })
    })

    it("should use provided wsFactory to create WebSocket", async () => {
      const mockFactory = vi.fn((url: string) => {
        const ws = new MockWebSocket(url)
        return ws as any
      })

      const customWrapper = ({ children }: { children: ReactNode }) => (
        <VoiceWebSocketProvider wsFactory={mockFactory}>{children}</VoiceWebSocketProvider>
      )

      renderHook(() => useVoiceWebSocket(), { wrapper: customWrapper })

      await waitFor(() => {
        expect(mockFactory).toHaveBeenCalledWith(
          expect.stringMatching(/\/api\/voice\/ws\/feedback\/global$/)
        )
      })
    })
  })
})
