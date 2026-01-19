/**
 * VoiceFeedbackContext Tests
 *
 * Tests for the global voice feedback notification context.
 * Tests state management, WebSocket integration, deduplication, and audio playback.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"

// Mock toast
const mockToast = vi.fn()
vi.mock("@/hooks/use-toast", () => ({
  toast: (args: unknown) => mockToast(args),
}))

// Mock WebSocket
let mockWsInstance: MockWebSocket | null = null

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

class MockAudio {
  play = vi.fn().mockResolvedValue(undefined)
  pause = vi.fn()
  onended: (() => void) | null = null
  onerror: (() => void) | null = null

  constructor() {
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
  type VoiceNotification,
} from "./VoiceFeedbackContext"

// Helper to create wrapper
function createWrapper() {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <VoiceFeedbackProvider>{children}</VoiceFeedbackProvider>
  }
}

describe("VoiceFeedbackContext", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockWsInstance = null
    mockAudioInstance = null
    // Clear global voice playing flag
    ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = false
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe("initial state", () => {
    it("should start with empty notifications", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })
      expect(result.current.notifications).toEqual([])
    })

    it("should start with unreadCount=0", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })
      expect(result.current.unreadCount).toBe(0)
    })

    it("should start with panel closed", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })
      expect(result.current.isPanelOpen).toBe(false)
    })

    it("should start with hands-free mode disabled", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })
      expect(result.current.isHandsFreeMode).toBe(false)
    })

    it("should auto-connect WebSocket on mount", () => {
      renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })
      // Check instance was created (not spy assertion)
      expect(mockWsInstance).not.toBeNull()
      expect(mockWsInstance?.url).toContain("/api/voice/ws/feedback/global")
    })
  })

  describe("WebSocket connection", () => {
    it("should set isConnected=true when WebSocket opens", async () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })

      expect(result.current.isConnected).toBe(true)
    })

    it("should set isConnected=false when WebSocket closes", async () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        mockWsInstance?.onopen?.(new Event("open"))
      })
      expect(result.current.isConnected).toBe(true)

      act(() => {
        mockWsInstance?.onclose?.(new CloseEvent("close"))
      })
      expect(result.current.isConnected).toBe(false)
    })

    it("should disconnect WebSocket on unmount", () => {
      const { unmount } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      unmount()
      expect(mockWsInstance?.close).toHaveBeenCalled()
    })

    it("should auto-reconnect after close", () => {
      renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      const firstInstance = mockWsInstance
      expect(firstInstance).not.toBeNull()

      // Simulate close
      act(() => {
        mockWsInstance?.onclose?.(new CloseEvent("close"))
      })

      // Clear reference to track new connection
      mockWsInstance = null

      // Fast forward 5 seconds
      act(() => {
        vi.advanceTimersByTime(5000)
      })

      // New instance should be created
      expect(mockWsInstance).not.toBeNull()
      expect(mockWsInstance).not.toBe(firstInstance)
    })

    it("should manually disconnect via disconnectWebSocket", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        result.current.disconnectWebSocket()
      })

      expect(mockWsInstance?.close).toHaveBeenCalled()
      expect(result.current.isConnected).toBe(false)
    })

    it("should manually connect via connectWebSocket", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // First disconnect
      act(() => {
        result.current.disconnectWebSocket()
      })

      const firstInstance = mockWsInstance
      mockWsInstance = null

      // Then connect again
      act(() => {
        result.current.connectWebSocket()
      })

      expect(mockWsInstance).not.toBeNull()
      expect(mockWsInstance).not.toBe(firstInstance)
    })
  })

  describe("notification handling", () => {
    it("should add notification when voice_feedback message received", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        team_id: "team1",
        role_id: "FE",
        timestamp: Date.now(),
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      expect(result.current.notifications).toHaveLength(1)
      expect(result.current.notifications[0].summary).toBe("Task completed")
      expect(result.current.notifications[0].teamId).toBe("team1")
      expect(result.current.notifications[0].roleId).toBe("FE")
    })

    it("should show toast on new notification", () => {
      renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "Voice Feedback",
        })
      )
    })

    it("should update unreadCount when notification added", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      expect(result.current.unreadCount).toBe(1)
    })

    it("should deduplicate identical messages within 30s window", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      // Send same message twice
      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Should only have 1 notification
      expect(result.current.notifications).toHaveLength(1)
    })

    it("should limit notifications to MAX_NOTIFICATIONS (50)", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Add 55 unique notifications
      for (let i = 0; i < 55; i++) {
        const message = {
          type: "voice_feedback",
          summary: `Task ${i}`,
          audio: `audio${i}`,
          timestamp: Date.now() + i,
        }
        act(() => {
          mockWsInstance?.onmessage?.(
            new MessageEvent("message", { data: JSON.stringify(message) })
          )
        })
      }

      expect(result.current.notifications).toHaveLength(50)
    })
  })

  describe("panel actions", () => {
    it("should toggle panel open/close", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      expect(result.current.isPanelOpen).toBe(false)

      act(() => {
        result.current.togglePanel()
      })
      expect(result.current.isPanelOpen).toBe(true)

      act(() => {
        result.current.togglePanel()
      })
      expect(result.current.isPanelOpen).toBe(false)
    })

    it("should open panel via openPanel", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        result.current.openPanel()
      })
      expect(result.current.isPanelOpen).toBe(true)
    })

    it("should close panel via closePanel", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        result.current.openPanel()
      })
      act(() => {
        result.current.closePanel()
      })
      expect(result.current.isPanelOpen).toBe(false)
    })
  })

  describe("notification actions", () => {
    it("should mark single notification as read", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Add notification
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      const notificationId = result.current.notifications[0].id

      act(() => {
        result.current.markAsRead(notificationId)
      })

      expect(result.current.notifications[0].isRead).toBe(true)
      expect(result.current.unreadCount).toBe(0)
    })

    it("should mark all notifications as read", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Add multiple notifications
      for (let i = 0; i < 3; i++) {
        const message = {
          type: "voice_feedback",
          summary: `Task ${i}`,
          audio: `audio${i}`,
          timestamp: Date.now() + i,
        }
        act(() => {
          mockWsInstance?.onmessage?.(
            new MessageEvent("message", { data: JSON.stringify(message) })
          )
        })
      }

      expect(result.current.unreadCount).toBe(3)

      act(() => {
        result.current.markAllAsRead()
      })

      expect(result.current.unreadCount).toBe(0)
      expect(result.current.notifications.every((n) => n.isRead)).toBe(true)
    })

    it("should clear all notifications", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Add notification
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      expect(result.current.notifications).toHaveLength(1)

      act(() => {
        result.current.clearAll()
      })

      expect(result.current.notifications).toHaveLength(0)
    })
  })

  describe("hands-free mode", () => {
    it("should toggle hands-free mode", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      expect(result.current.isHandsFreeMode).toBe(false)

      act(() => {
        result.current.setHandsFreeMode(true)
      })

      expect(result.current.isHandsFreeMode).toBe(true)
    })

    it("should auto-play audio in hands-free mode for recent messages", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Enable hands-free mode
      act(() => {
        result.current.setHandsFreeMode(true)
      })

      // Clear any audio instance from setup
      mockAudioInstance = null

      // Add notification with recent timestamp
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(), // Current time = recent
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Audio instance should have been created and play called
      expect(mockAudioInstance).not.toBeNull()
      expect(mockAudioInstance?.play).toHaveBeenCalled()
    })

    it("should NOT auto-play audio when hands-free mode disabled", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Ensure hands-free mode is OFF
      expect(result.current.isHandsFreeMode).toBe(false)

      // Clear any audio instance
      mockAudioInstance = null

      // Add notification
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Audio should NOT be created
      expect(mockAudioInstance).toBeNull()
    })

    it("should skip stale audio (>60s old) even in hands-free mode", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Enable hands-free mode
      act(() => {
        result.current.setHandsFreeMode(true)
      })

      // Clear any audio instance
      mockAudioInstance = null

      // Add notification with old timestamp (2 minutes ago)
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now() - 120000, // 2 minutes old
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Audio should NOT be played (stale)
      expect(mockAudioInstance).toBeNull()
    })
  })

  describe("playNotification", () => {
    it("should play audio for specific notification", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Add notification (without auto-play since hands-free is off)
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      // Clear any audio instance
      mockAudioInstance = null

      const notificationId = result.current.notifications[0].id

      act(() => {
        result.current.playNotification(notificationId)
      })

      expect(mockAudioInstance).not.toBeNull()
      expect(mockAudioInstance?.play).toHaveBeenCalled()
    })

    it("should mark notification as played after audio ends", () => {
      const { result } = renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      // Add notification
      const message = {
        type: "voice_feedback",
        summary: "Task completed",
        audio: "base64audio",
        timestamp: Date.now(),
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(message) })
        )
      })

      const notificationId = result.current.notifications[0].id

      act(() => {
        result.current.playNotification(notificationId)
      })

      expect(result.current.notifications[0].isPlayed).toBe(false)

      // Simulate audio ended
      act(() => {
        mockAudioInstance?.onended?.()
      })

      expect(result.current.notifications[0].isPlayed).toBe(true)
    })
  })

  describe("useVoiceFeedback hook", () => {
    it("should throw error when used outside provider", () => {
      expect(() => {
        renderHook(() => useVoiceFeedback())
      }).toThrow("useVoiceFeedback must be used within VoiceFeedbackProvider")
    })
  })

  describe("error handling", () => {
    it("should handle WebSocket error event", () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {})

      renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        mockWsInstance?.onerror?.(new Event("error"))
      })

      expect(consoleSpy).toHaveBeenCalledWith(
        "[VoiceFeedback] WebSocket error:",
        expect.any(Event)
      )

      consoleSpy.mockRestore()
    })

    it("should handle error message type", () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {})

      renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      const errorMessage = {
        type: "error",
        message: "Something went wrong",
      }

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: JSON.stringify(errorMessage) })
        )
      })

      expect(consoleSpy).toHaveBeenCalledWith(
        "[VoiceFeedback] WebSocket error:",
        "Something went wrong"
      )

      consoleSpy.mockRestore()
    })

    it("should handle invalid JSON message", () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {})

      renderHook(() => useVoiceFeedback(), {
        wrapper: createWrapper(),
      })

      act(() => {
        mockWsInstance?.onmessage?.(
          new MessageEvent("message", { data: "invalid json" })
        )
      })

      expect(consoleSpy).toHaveBeenCalledWith(
        "[VoiceFeedback] Message parse error:",
        expect.any(Error)
      )

      consoleSpy.mockRestore()
    })
  })
})
