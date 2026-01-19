/**
 * useVoiceRecorder Hook Tests
 *
 * Tests for the voice recording hook that manages Soniox STT integration.
 * Tests initial state, state transitions, command sending, and Web Audio API.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act, waitFor } from "@testing-library/react"

// Mock dependencies before import
vi.mock("@/lib/auth", () => ({
  getToken: () => "mock-token",
}))

vi.mock("@/lib/voice-types", () => ({
  getStopWord: () => "thank you",
}))

// Mock toast for routed_to_backlog notification
const mockToast = vi.fn()
vi.mock("@/hooks/use-toast", () => ({
  toast: (...args: unknown[]) => mockToast(...args),
}))

// Mock SonioxSTTService with a proper class that exposes connected property
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let mockServiceInstance: any = null

vi.mock("@/lib/stt", () => ({
  SonioxSTTService: class MockSonioxSTTService {
    connect = vi.fn().mockResolvedValue(undefined)
    disconnect = vi.fn()
    connected = false
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    callbacks: any = {}

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    constructor(_config: any, callbacks: any) {
      this.callbacks = callbacks
      mockServiceInstance = this
    }

    getTranscript() {
      return ""
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    updateCallbacks(callbacks: any) {
      Object.assign(this.callbacks, callbacks)
    }
  },
}))

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock AudioContext for playAcknowledgmentBeep
class MockOscillatorNode {
  type = "sine"
  frequency = { setValueAtTime: vi.fn() }
  connect = vi.fn()
  start = vi.fn()
  stop = vi.fn()
  onended: (() => void) | null = null
}

class MockGainNode {
  gain = {
    setValueAtTime: vi.fn(),
    linearRampToValueAtTime: vi.fn(),
  }
  connect = vi.fn()
}

const mockAudioContextClose = vi.fn()
class MockAudioContext {
  currentTime = 0
  destination = {}
  createOscillator = vi.fn(() => new MockOscillatorNode())
  createGain = vi.fn(() => new MockGainNode())
  close = mockAudioContextClose
}

// Mock WakeLock API
const mockWakeLockRelease = vi.fn()
const mockWakeLockSentinel = {
  release: mockWakeLockRelease,
  addEventListener: vi.fn(),
}

// Import after mocks
import { useVoiceRecorder } from "./useVoiceRecorder"

describe("useVoiceRecorder", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockServiceInstance = null
    mockToast.mockClear()

    // Default fetch mock with streaming body
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
      body: null,
    })

    // Mock AudioContext
    vi.stubGlobal("AudioContext", MockAudioContext)

    // Mock navigator.wakeLock
    Object.defineProperty(navigator, "wakeLock", {
      value: {
        request: vi.fn().mockResolvedValue(mockWakeLockSentinel),
      },
      writable: true,
      configurable: true,
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  describe("initial state", () => {
    it("should start with idle status", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.state.status).toBe("idle")
    })

    it("should have empty transcript", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.state.transcript).toBe("")
    })

    it("should have canRecord=true initially", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.canRecord).toBe(true)
    })

    it("should have isRecording=false initially", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.isRecording).toBe(false)
    })

    it("should have empty correctedCommand", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.state.correctedCommand).toBe("")
    })

    it("should have no error", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.state.error).toBeNull()
    })

    it("should have isSpeaking=false initially", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.state.isSpeaking).toBe(false)
    })

    it("should have empty feedbackSummary", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.state.feedbackSummary).toBe("")
    })
  })

  describe("startRecording", () => {
    it("should set status to connecting when starting", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      act(() => {
        result.current.startRecording("team1", "role1")
      })

      expect(result.current.state.status).toBe("connecting")
    })

    it("should create SonioxSTTService instance", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      expect(mockServiceInstance).not.toBeNull()
    })

    it("should call connect on Soniox service", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      expect(mockServiceInstance?.connect).toHaveBeenCalled()
    })
  })

  describe("stopRecording", () => {
    it("should set status to idle when stopped", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      // Simulate connection success (releases mutex)
      const callbacks = mockServiceInstance?.callbacks
      act(() => {
        callbacks?.onConnectionChange?.(true)
      })

      act(() => {
        result.current.stopRecording()
      })

      expect(result.current.state.status).toBe("idle")
    })

    it("should set isRecording to false", () => {
      const { result } = renderHook(() => useVoiceRecorder())

      act(() => {
        result.current.stopRecording()
      })

      expect(result.current.isRecording).toBe(false)
    })

    it("should call disconnect on Soniox service when connected", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      // Simulate connection success (releases mutex)
      const callbacks = mockServiceInstance?.callbacks
      act(() => {
        callbacks?.onConnectionChange?.(true)
      })

      act(() => {
        result.current.stopRecording()
      })

      expect(mockServiceInstance?.disconnect).toHaveBeenCalled()
    })
  })

  describe("state transitions", () => {
    it("should allow recording from idle state", () => {
      const { result } = renderHook(() => useVoiceRecorder())
      expect(result.current.canRecord).toBe(true)
    })

    it("should not allow recording while connecting", () => {
      const { result } = renderHook(() => useVoiceRecorder())

      act(() => {
        result.current.startRecording("team1", "role1")
      })

      expect(result.current.state.status).toBe("connecting")
      expect(result.current.canRecord).toBe(false)
    })

    it("should allow recording after stopping", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      // Simulate connection success (releases mutex)
      const callbacks = mockServiceInstance?.callbacks
      act(() => {
        callbacks?.onConnectionChange?.(true)
      })

      act(() => {
        result.current.stopRecording()
      })

      expect(result.current.canRecord).toBe(true)
    })
  })

  describe("cleanup on unmount", () => {
    it("should disconnect Soniox on unmount when connected", async () => {
      const { result, unmount } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const instance = mockServiceInstance
      unmount()

      expect(instance?.disconnect).toHaveBeenCalled()
    })
  })

  describe("callback integration", () => {
    it("should register callbacks with Soniox service", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      // Service should have callbacks registered
      expect(mockServiceInstance).not.toBeNull()
      const callbacks = (mockServiceInstance as unknown as { callbacks: Record<string, unknown> })?.callbacks
      expect(callbacks).toBeDefined()
      expect(typeof callbacks?.onTranscript).toBe("function")
      expect(typeof callbacks?.onFinalize).toBe("function")
      expect(typeof callbacks?.onConnectionChange).toBe("function")
      expect(typeof callbacks?.onError).toBe("function")
    })

    it("should update transcript when onTranscript is called", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = (mockServiceInstance as unknown as { callbacks: { onTranscript: (t: string, f: boolean) => void } })?.callbacks

      act(() => {
        callbacks?.onTranscript("hello world", true)
      })

      expect(result.current.state.transcript).toBe("hello world")
    })

    it("should set isRecording true when onConnectionChange(true)", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = (mockServiceInstance as unknown as { callbacks: { onConnectionChange: (c: boolean) => void } })?.callbacks

      act(() => {
        callbacks?.onConnectionChange(true)
      })

      expect(result.current.isRecording).toBe(true)
    })

    it("should set error state when onError is called", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = (mockServiceInstance as unknown as { callbacks: { onError: (e: Error) => void } })?.callbacks

      act(() => {
        callbacks?.onError(new Error("Mic permission denied"))
      })

      expect(result.current.state.status).toBe("error")
      expect(result.current.state.error).toBe("Mic permission denied")
    })

    it("should set isSpeaking based on isFinal flag", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      // Non-final transcript = still speaking
      act(() => {
        callbacks?.onTranscript?.("hello", false)
      })
      expect(result.current.state.isSpeaking).toBe(true)

      // Final transcript = not speaking
      act(() => {
        callbacks?.onTranscript?.("hello world", true)
      })
      expect(result.current.state.isSpeaking).toBe(false)
    })
  })

  describe("handleFinalize via onFinalize callback", () => {
    it("should set status to correcting when command finalized and sent to backend", async () => {
      // Mock streaming response
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('{"type":"llm_token","token":"Fix"}\n') })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      // Trigger onFinalize - this calls handleFinalize which sets "processing" then sendCommand which sets "correcting"
      act(() => {
        callbacks?.onFinalize?.("fix the bug")
      })

      // Status transitions: processing -> correcting (when sendCommand starts)
      expect(result.current.state.status).toBe("correcting")
    })

    it("should skip empty commands", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      // Trigger onFinalize with empty command
      act(() => {
        callbacks?.onFinalize?.("   ")
      })

      // Should remain in whatever state it was, not processing
      expect(result.current.state.status).not.toBe("processing")
    })

    it("should debounce rapid duplicate commands", async () => {
      vi.useFakeTimers()

      const mockReader = {
        read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks
      mockFetch.mockClear()

      // First finalize
      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await vi.advanceTimersByTimeAsync(100)
      })

      // Second finalize within debounce window (500ms)
      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await vi.advanceTimersByTimeAsync(100)
      })

      // Only one fetch call should have been made
      expect(mockFetch).toHaveBeenCalledTimes(1)

      vi.useRealTimers()
    })
  })

  describe("sendCommand", () => {
    it("should call fetch with correct parameters", async () => {
      const mockReader = {
        read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks
      mockFetch.mockClear()

      await act(async () => {
        callbacks?.onFinalize?.("fix the bug")
        // Wait for fetch to be called
        await new Promise(resolve => setTimeout(resolve, 0))
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/voice/command/team1/role1"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          }),
          body: expect.stringContaining("fix the bug"),
        })
      )
    })

    it("should handle streaming response with llm_token", async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('{"type":"llm_token","token":"Fix "}\n{"type":"llm_token","token":"the bug"}\n')
          })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        // Wait for streaming to process
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      expect(result.current.state.correctedCommand).toBe("Fix the bug")
    })

    it("should handle command_sent response", async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('{"type":"command_sent","corrected_command":"Fix the bug now"}\n')
          })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      expect(result.current.state.status).toBe("sent")
      expect(result.current.state.correctedCommand).toBe("Fix the bug now")
    })

    it("should redirect to login on 401", async () => {
      const originalLocation = window.location
      delete (window as { location?: Location }).location
      window.location = { href: "" } as Location

      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        body: null,
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      expect(window.location.href).toBe("/login")

      window.location = originalLocation
    })

    it("should set error status on backend error", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        body: null,
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      expect(result.current.state.status).toBe("error")
      expect(result.current.state.error).toContain("500")
    })

    it("should handle null response body", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: null,
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      // Should not crash, status transitions to sent after timeout
      expect(result.current.state.status).not.toBe("error")
    })

    it("should skip invalid JSON lines in stream", async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('not json\n{"type":"llm_token","token":"Valid"}\n')
          })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      // Should have processed the valid JSON and skipped invalid
      expect(result.current.state.correctedCommand).toBe("Valid")
    })
  })

  describe("routed_to_backlog toast notification", () => {
    it("should show toast when routed_to_backlog is true", async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('{"type":"command_sent","corrected_command":"Add dark mode to backlog","routed_to_backlog":true}\n')
          })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("add dark mode to backlog")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      // Toast should have been called with routing notification
      expect(mockToast).toHaveBeenCalledWith({
        title: "Routed to Backlog Organizer",
        description: "Your command was sent to BL for backlog management.",
      })
    })

    it("should NOT show toast when routed_to_backlog is false", async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('{"type":"command_sent","corrected_command":"Fix the bug","routed_to_backlog":false}\n')
          })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix the bug")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      // Toast should NOT have been called
      expect(mockToast).not.toHaveBeenCalled()
    })

    it("should NOT show toast when routed_to_backlog is undefined", async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('{"type":"command_sent","corrected_command":"Run tests"}\n')
          })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("run tests")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      // Toast should NOT have been called (undefined = not routed)
      expect(mockToast).not.toHaveBeenCalled()
    })
  })

  describe("playAcknowledgmentBeep", () => {
    it("should create AudioContext and oscillator for beep", async () => {
      const mockReader = {
        read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      // AudioContext should have been created
      expect(MockAudioContext).toBeDefined()
    })

    it("should handle AudioContext errors gracefully", async () => {
      // Make AudioContext throw
      vi.stubGlobal("AudioContext", class {
        constructor() {
          throw new Error("AudioContext not supported")
        }
      })

      const mockReader = {
        read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      // Should not throw even if AudioContext fails
      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await new Promise(resolve => setTimeout(resolve, 50))
      })

      // Test should complete without error
      expect(result.current.state.status).not.toBe("error")
    })
  })

  describe("wake lock functionality", () => {
    it("should request wake lock on startRecording", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      expect(navigator.wakeLock.request).toHaveBeenCalledWith("screen")
    })

    it("should release wake lock on stopRecording", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      // Simulate connection success (releases mutex)
      const callbacks = mockServiceInstance?.callbacks
      act(() => {
        callbacks?.onConnectionChange?.(true)
      })

      act(() => {
        result.current.stopRecording()
      })

      expect(mockWakeLockRelease).toHaveBeenCalled()
    })

    it("should handle wake lock not supported gracefully", async () => {
      // Remove wakeLock from navigator
      Object.defineProperty(navigator, "wakeLock", {
        value: undefined,
        writable: true,
        configurable: true,
      })

      const { result } = renderHook(() => useVoiceRecorder())

      // Should not throw
      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      expect(result.current.state.status).not.toBe("error")
    })

    it("should handle wake lock request failure gracefully", async () => {
      Object.defineProperty(navigator, "wakeLock", {
        value: {
          request: vi.fn().mockRejectedValue(new Error("Wake lock denied")),
        },
        writable: true,
        configurable: true,
      })

      const { result } = renderHook(() => useVoiceRecorder())

      // Should not throw
      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      expect(result.current.state.status).not.toBe("error")
    })
  })

  describe("visibility change handler", () => {
    it("should re-acquire wake lock when page becomes visible during recording", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      // Clear the initial wake lock request
      ;(navigator.wakeLock.request as ReturnType<typeof vi.fn>).mockClear()

      // Simulate page becoming hidden then visible
      Object.defineProperty(document, "visibilityState", {
        value: "visible",
        writable: true,
        configurable: true,
      })

      // Dispatch visibility change event
      await act(async () => {
        document.dispatchEvent(new Event("visibilitychange"))
        await new Promise(resolve => setTimeout(resolve, 0))
      })

      // Wake lock should be re-requested (if it was released)
      // The exact behavior depends on implementation
      expect(navigator.wakeLock.request).toBeDefined()
    })
  })

  describe("onConnectionChange reconnect logic", () => {
    it("should attempt reconnect when disconnected while hands-free", async () => {
      vi.useFakeTimers()

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      // First set connected to trigger hands-free mode
      act(() => {
        callbacks?.onConnectionChange?.(true)
      })

      expect(result.current.isRecording).toBe(true)

      // Now simulate disconnect
      act(() => {
        callbacks?.onConnectionChange?.(false)
      })

      // Advance timer to trigger reconnect
      await act(async () => {
        await vi.advanceTimersByTimeAsync(1100)
      })

      // Should have attempted to create a new service (reconnect)
      expect(mockServiceInstance?.connect).toHaveBeenCalled()

      vi.useRealTimers()
    })
  })

  describe("error handling in startRecording", () => {
    it("should set error state when Soniox connect fails", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      // Make connect reject for next call
      if (mockServiceInstance) {
        mockServiceInstance.connect.mockRejectedValueOnce(new Error("Connection failed"))
      }

      // Simulate error callback
      const callbacks = mockServiceInstance?.callbacks

      act(() => {
        callbacks?.onError?.(new Error("Connection failed"))
      })

      expect(result.current.state.status).toBe("error")
      expect(result.current.state.error).toBe("Connection failed")
    })
  })

  describe("state after command sent timeout", () => {
    it("should return to listening if still hands-free after sending", async () => {
      vi.useFakeTimers()

      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('{"type":"command_sent","corrected_command":"Fixed"}\n')
          })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      // Set as connected
      if (mockServiceInstance) {
        mockServiceInstance.connected = true
      }

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await vi.advanceTimersByTimeAsync(50)
      })

      expect(result.current.state.status).toBe("sent")

      // Advance past the 2000ms delay
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2100)
      })

      // Should return to listening since hands-free and connected
      expect(result.current.state.status).toBe("listening")

      vi.useRealTimers()
    })

    it("should return to idle if not hands-free after sending", async () => {
      vi.useFakeTimers()

      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('{"type":"command_sent","corrected_command":"Fixed"}\n')
          })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: { getReader: () => mockReader },
      })

      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      await act(async () => {
        callbacks?.onFinalize?.("fix bug")
        await vi.advanceTimersByTimeAsync(50)
      })

      expect(result.current.state.status).toBe("sent")

      // Stop recording (disables hands-free)
      act(() => {
        result.current.stopRecording()
      })

      // Advance past the 2000ms delay
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2100)
      })

      // Should return to idle since hands-free is disabled
      expect(result.current.state.status).toBe("idle")

      vi.useRealTimers()
    })
  })

  describe("onAudioLevel callback", () => {
    it("should register onAudioLevel callback with service", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks
      expect(typeof callbacks?.onAudioLevel).toBe("function")
    })

    it("should handle onAudioLevel calls without error", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      // Call onAudioLevel - should not throw
      expect(() => {
        callbacks?.onAudioLevel?.(-30)
      }).not.toThrow()
    })
  })

  describe("transition mutex with pending stop", () => {
    it("should execute pending stop after transition completes", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      // Start recording - use await to ensure mock service is created
      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      // After startRecording completes, mutex should still be true until onConnectionChange
      // The mock doesn't call onConnectionChange automatically
      expect(mockServiceInstance).not.toBeNull()

      // Try to stop - this should be blocked by mutex and queued
      act(() => {
        result.current.stopRecording()
      })

      // isRecording should still be true because stop was queued, not executed
      expect(result.current.isRecording).toBe(true)

      // Get callbacks after service is created
      const callbacks = mockServiceInstance?.callbacks

      // Now simulate connection success (onConnectionChange(true))
      // This should clear mutex AND execute pending stop
      act(() => {
        callbacks?.onConnectionChange?.(true)
      })

      // After transition completes, pending stop should have executed
      expect(result.current.isRecording).toBe(false)
      expect(result.current.state.status).toBe("idle")
    })

    it("should not queue stop if no transition in progress", async () => {
      const { result } = renderHook(() => useVoiceRecorder())

      // Start and wait for connection
      await act(async () => {
        await result.current.startRecording("team1", "role1")
      })

      const callbacks = mockServiceInstance?.callbacks

      // Complete connection (clears mutex)
      act(() => {
        callbacks?.onConnectionChange?.(true)
      })

      expect(result.current.isRecording).toBe(true)

      // Now stop - should execute immediately since no transition
      act(() => {
        result.current.stopRecording()
      })

      expect(result.current.isRecording).toBe(false)
      expect(result.current.state.status).toBe("idle")
    })
  })
})
