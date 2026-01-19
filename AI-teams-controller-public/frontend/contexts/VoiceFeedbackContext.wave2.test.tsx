/**
 * VoiceFeedbackContext Wave 2 Tests - Dual State Pattern
 *
 * Tests for callback behavior with voiceFeedbackMode and isHandsFreeMode state changes.
 * Written BEFORE refactoring to verify callbacks use latest state.
 *
 * Wave 2: Fix Dual State Pattern
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act } from "@testing-library/react"
import type { ReactNode } from "react"

// Mock toast
const mockToast = vi.fn()
vi.mock("@/hooks/use-toast", () => ({
  toast: (args: unknown) => mockToast(args),
}))

// Mock WebSocket
let mockWsInstance: MockWebSocket | null = null
let capturedMessageHandler: ((event: MessageEvent) => void) | null = null

class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  readyState = MockWebSocket.CONNECTING
  url: string

  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED
  })

  constructor(url: string) {
    this.url = url
    mockWsInstance = this
  }
}

vi.stubGlobal("WebSocket", MockWebSocket)

// Mock Audio
let mockAudioInstance: MockAudio | null = null
let audioPlayCalls: string[] = []

class MockAudio {
  play = vi.fn().mockImplementation(() => {
    audioPlayCalls.push("played")
    return Promise.resolve()
  })
  pause = vi.fn()
  onended: (() => void) | null = null
  onerror: (() => void) | null = null
  src = ""

  constructor(src?: string) {
    this.src = src || ""
    mockAudioInstance = this
  }
}

vi.stubGlobal("Audio", MockAudio)

// Mock URL API
const mockCreateObjectURL = vi.fn().mockReturnValue("blob:test-url")
const mockRevokeObjectURL = vi.fn()
vi.stubGlobal("URL", {
  createObjectURL: mockCreateObjectURL,
  revokeObjectURL: mockRevokeObjectURL,
})

// Mock atob
vi.stubGlobal("atob", (str: string) => str)

// Import after mocks
import {
  VoiceFeedbackProvider,
  useVoiceFeedback,
} from "./VoiceFeedbackContext"

// Helper to create wrapper
function createWrapper() {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <VoiceFeedbackProvider>{children}</VoiceFeedbackProvider>
  }
}

describe("VoiceFeedbackContext - Wave 2: Dual State Pattern", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockWsInstance = null
    capturedMessageHandler = null
    mockAudioInstance = null
    audioPlayCalls = []
    // Clear global voice playing flag
    ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = false
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe("voiceFeedbackMode state management", () => {
    it("should start with default voice feedback mode", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Should have a voiceFeedbackMode (exact value depends on localStorage)
      expect(result.current.voiceFeedbackMode).toBeDefined()
    })

    it("should update voiceFeedbackMode when setVoiceFeedbackMode is called", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        result.current.setVoiceFeedbackMode("off")
      })

      expect(result.current.voiceFeedbackMode).toBe("off")

      act(() => {
        result.current.setVoiceFeedbackMode("tone")
      })

      expect(result.current.voiceFeedbackMode).toBe("tone")

      act(() => {
        result.current.setVoiceFeedbackMode("voice")
      })

      expect(result.current.voiceFeedbackMode).toBe("voice")
    })
  })

  describe("isHandsFreeMode state management", () => {
    it("should start with hands-free mode disabled", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      expect(result.current.isHandsFreeMode).toBe(false)
    })

    it("should update isHandsFreeMode when setHandsFreeMode is called", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        result.current.setHandsFreeMode(true)
      })

      expect(result.current.isHandsFreeMode).toBe(true)

      act(() => {
        result.current.setHandsFreeMode(false)
      })

      expect(result.current.isHandsFreeMode).toBe(false)
    })
  })

  describe("callback behavior with voiceFeedbackMode changes", () => {
    it("should use current voiceFeedbackMode in WebSocket message handler (OFF mode)", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Set mode to OFF
      act(() => {
        result.current.setVoiceFeedbackMode("off")
      })

      // Open WebSocket
      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      // Send voice feedback message
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Should NOT play audio (mode is OFF)
      expect(audioPlayCalls).toHaveLength(0)
    })

    it("should use current voiceFeedbackMode in WebSocket message handler (TONE mode)", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Set mode to TONE
      act(() => {
        result.current.setVoiceFeedbackMode("tone")
      })

      // Open WebSocket
      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      // Send voice feedback message
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Should play tone (meow.mp3)
      expect(audioPlayCalls.length).toBeGreaterThan(0)
    })

    it("should use current voiceFeedbackMode in WebSocket message handler (VOICE mode with hands-free)", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Set mode to VOICE and enable hands-free
      act(() => {
        result.current.setVoiceFeedbackMode("voice")
        result.current.setHandsFreeMode(true)
      })

      // Open WebSocket
      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      // Send voice feedback message
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Should play audio (voice mode + hands-free enabled)
      expect(audioPlayCalls.length).toBeGreaterThan(0)
    })

    it("should NOT play voice audio when hands-free is disabled (VOICE mode)", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Set mode to VOICE but hands-free DISABLED
      act(() => {
        result.current.setVoiceFeedbackMode("voice")
        result.current.setHandsFreeMode(false)
      })

      // Open WebSocket
      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      // Send voice feedback message
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Should NOT play audio (hands-free disabled)
      expect(audioPlayCalls).toHaveLength(0)
    })
  })

  describe("state consistency after mode changes", () => {
    it("should use updated mode immediately after setVoiceFeedbackMode", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Start with VOICE mode
      act(() => {
        result.current.setVoiceFeedbackMode("voice")
        result.current.setHandsFreeMode(true)
      })

      // Open WebSocket
      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      // Change to OFF mode
      act(() => {
        result.current.setVoiceFeedbackMode("off")
      })

      // Send message AFTER mode change
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Should use new mode (OFF) - no audio played
      expect(audioPlayCalls).toHaveLength(0)
    })

    it("should handle rapid mode switching correctly", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Open WebSocket
      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      // Rapid mode changes
      act(() => {
        result.current.setVoiceFeedbackMode("voice")
        result.current.setVoiceFeedbackMode("off")
        result.current.setVoiceFeedbackMode("tone")
      })

      // Final mode should be TONE
      expect(result.current.voiceFeedbackMode).toBe("tone")

      // Send message - should use TONE mode
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Should play tone
      expect(audioPlayCalls.length).toBeGreaterThan(0)
    })

    it("should handle rapid hands-free toggle correctly", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Rapid hands-free toggles
      act(() => {
        result.current.setHandsFreeMode(true)
        result.current.setHandsFreeMode(false)
        result.current.setHandsFreeMode(true)
      })

      // Final state should be TRUE
      expect(result.current.isHandsFreeMode).toBe(true)
    })
  })

  describe("callback re-creation on state change", () => {
    it("should handle messages correctly after voiceFeedbackMode change", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Start with OFF mode
      act(() => {
        result.current.setVoiceFeedbackMode("off")
      })

      // Open WebSocket
      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      // Send first message (should not play)
      const message1 = {
        type: "voice_feedback",
        summary: "First task",
        audio: "audio1",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message1) })
        )
      })

      expect(audioPlayCalls).toHaveLength(0)

      // Change to TONE mode
      act(() => {
        result.current.setVoiceFeedbackMode("tone")
      })

      // Send second message (should play tone)
      const message2 = {
        type: "voice_feedback",
        summary: "Second task",
        audio: "audio2",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message2) })
        )
      })

      // Should play tone for second message
      expect(audioPlayCalls.length).toBeGreaterThan(0)
    })

    it("should handle messages correctly after isHandsFreeMode change", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // VOICE mode, hands-free OFF
      act(() => {
        result.current.setVoiceFeedbackMode("voice")
        result.current.setHandsFreeMode(false)
      })

      // Open WebSocket
      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      // Send first message (should not play - hands-free off)
      const message1 = {
        type: "voice_feedback",
        summary: "First task",
        audio: "audio1",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message1) })
        )
      })

      expect(audioPlayCalls).toHaveLength(0)

      // Enable hands-free
      act(() => {
        result.current.setHandsFreeMode(true)
      })

      // Send second message (should play - hands-free on)
      const message2 = {
        type: "voice_feedback",
        summary: "Second task",
        audio: "audio2",
        timestamp: Date.now(),
      }

      audioPlayCalls = []
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message2) })
        )
      })

      // Should play audio for second message
      expect(audioPlayCalls.length).toBeGreaterThan(0)
    })
  })
})
