/**
 * useAudioManager Hook Tests
 *
 * TDD Phase: RED - Tests written BEFORE hook extraction
 *
 * Hook Purpose:
 * - Play acknowledgment beep using Web Audio API
 * - Generate 880Hz sine wave tone (A5 note)
 * - Handle audio context creation/cleanup
 * - Graceful fallback on errors
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act } from "@testing-library/react"
import { useAudioManager } from "./useAudioManager"

// Mock Web Audio API
const mockOscillator = {
  type: "sine" as OscillatorType,
  frequency: {
    setValueAtTime: vi.fn(),
  },
  connect: vi.fn(),
  start: vi.fn(),
  stop: vi.fn(),
  onended: null as ((this: AudioScheduledSourceNode, ev: Event) => any) | null,
}

const mockGainNode = {
  gain: {
    setValueAtTime: vi.fn(),
    linearRampToValueAtTime: vi.fn(),
  },
  connect: vi.fn(),
}

const mockAudioContext = {
  createOscillator: vi.fn(() => mockOscillator),
  createGain: vi.fn(() => mockGainNode),
  close: vi.fn(),
  currentTime: 0,
  destination: {} as AudioDestinationNode,
}

describe("useAudioManager Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // @ts-ignore
    global.AudioContext = vi.fn(() => mockAudioContext)
    mockAudioContext.currentTime = 0
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe("Initialization", () => {
    it("should initialize without creating AudioContext", () => {
      renderHook(() => useAudioManager())

      // AudioContext should not be created until playBeep is called
      expect(global.AudioContext).not.toHaveBeenCalled()
    })

    it("should return playBeep function", () => {
      const { result } = renderHook(() => useAudioManager())

      expect(result.current.playBeep).toBeDefined()
      expect(typeof result.current.playBeep).toBe("function")
    })
  })

  describe("Playing Acknowledgment Beep", () => {
    it("should create AudioContext when playBeep is called", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(global.AudioContext).toHaveBeenCalledTimes(1)
    })

    it("should create oscillator and gain node", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockAudioContext.createOscillator).toHaveBeenCalled()
      expect(mockAudioContext.createGain).toHaveBeenCalled()
    })

    it("should set oscillator frequency to 880Hz (A5 note)", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockOscillator.frequency.setValueAtTime).toHaveBeenCalledWith(880, 0)
    })

    it("should configure oscillator as sine wave", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockOscillator.type).toBe("sine")
    })

    it("should apply fade in/out envelope to prevent clicks", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      // Fade in: 0 -> 0.3 over 0.02s
      expect(mockGainNode.gain.setValueAtTime).toHaveBeenCalledWith(0, 0)
      expect(mockGainNode.gain.linearRampToValueAtTime).toHaveBeenCalledWith(0.3, 0.02)
      // Fade out: 0.3 -> 0 over 0.15s
      expect(mockGainNode.gain.linearRampToValueAtTime).toHaveBeenCalledWith(0, 0.15)
    })

    it("should connect oscillator to gain node", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockOscillator.connect).toHaveBeenCalledWith(mockGainNode)
    })

    it("should connect gain node to audio context destination", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockGainNode.connect).toHaveBeenCalledWith(mockAudioContext.destination)
    })

    it("should start oscillator immediately", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockOscillator.start).toHaveBeenCalledWith(0)
    })

    it("should stop oscillator after 150ms", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockOscillator.stop).toHaveBeenCalledWith(0.15)
    })

    it("should close AudioContext when oscillator ends", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      // Trigger onended callback
      if (mockOscillator.onended) {
        act(() => {
          mockOscillator.onended!(new Event("ended"))
        })
      }

      expect(mockAudioContext.close).toHaveBeenCalled()
    })
  })

  describe("Error Handling", () => {
    it("should not throw when AudioContext is not supported", () => {
      // @ts-ignore
      global.AudioContext = undefined

      const { result } = renderHook(() => useAudioManager())

      expect(() => {
        act(() => {
          result.current.playBeep()
        })
      }).not.toThrow()
    })

    it("should handle oscillator creation failure gracefully", () => {
      mockAudioContext.createOscillator = vi.fn(() => {
        throw new Error("Oscillator creation failed")
      })

      const { result } = renderHook(() => useAudioManager())

      expect(() => {
        act(() => {
          result.current.playBeep()
        })
      }).not.toThrow()
    })

    it("should handle audio context close failure gracefully", () => {
      mockAudioContext.close = vi.fn(() => {
        throw new Error("Close failed")
      })

      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      // Trigger onended
      if (mockOscillator.onended) {
        expect(() => {
          act(() => {
            mockOscillator.onended!(new Event("ended"))
          })
        }).not.toThrow()
      }
    })

    it("should log error but continue execution on beep failure", () => {
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
      mockAudioContext.createOscillator = vi.fn(() => {
        throw new Error("Test error")
      })

      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Beep error"),
        expect.any(Error)
      )

      consoleErrorSpy.mockRestore()
    })
  })

  describe("Multiple Calls", () => {
    it("should create new AudioContext on each playBeep call", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
        result.current.playBeep()
        result.current.playBeep()
      })

      expect(global.AudioContext).toHaveBeenCalledTimes(3)
    })

    it("should handle rapid successive calls", () => {
      const { result } = renderHook(() => useAudioManager())

      expect(() => {
        act(() => {
          for (let i = 0; i < 10; i++) {
            result.current.playBeep()
          }
        })
      }).not.toThrow()
    })
  })

  describe("Cleanup", () => {
    it("should close AudioContext via onended callback", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockOscillator.onended).not.toBeNull()

      act(() => {
        mockOscillator.onended!(new Event("ended"))
      })

      expect(mockAudioContext.close).toHaveBeenCalled()
    })

    it("should not leak audio contexts", () => {
      const { result, unmount } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      // Simulate oscillator ending
      act(() => {
        if (mockOscillator.onended) {
          mockOscillator.onended(new Event("ended"))
        }
      })

      unmount()

      // AudioContext should be closed
      expect(mockAudioContext.close).toHaveBeenCalled()
    })
  })

  describe("Audio Parameters", () => {
    it("should use correct audio parameters for pleasant chime", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      // 880Hz = A5 note (pleasant tone)
      expect(mockOscillator.frequency.setValueAtTime).toHaveBeenCalledWith(880, expect.any(Number))

      // Volume: 0 -> 0.3 (not too loud)
      expect(mockGainNode.gain.linearRampToValueAtTime).toHaveBeenCalledWith(0.3, expect.any(Number))

      // Duration: 150ms (not too long)
      expect(mockOscillator.stop).toHaveBeenCalledWith(0.15)
    })

    it("should use sine wave for smooth tone", () => {
      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(mockOscillator.type).toBe("sine")
    })
  })

  describe("Browser Compatibility", () => {
    it("should work when webkitAudioContext is available", () => {
      // @ts-ignore
      global.AudioContext = undefined
      // @ts-ignore
      global.webkitAudioContext = vi.fn(() => mockAudioContext)

      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      // Should fall back to webkitAudioContext
      expect(global.webkitAudioContext).toHaveBeenCalled()
    })

    it("should fail silently when no AudioContext available", () => {
      // @ts-ignore
      global.AudioContext = undefined
      // @ts-ignore
      global.webkitAudioContext = undefined

      const { result } = renderHook(() => useAudioManager())

      expect(() => {
        act(() => {
          result.current.playBeep()
        })
      }).not.toThrow()
    })
  })

  describe("Logging", () => {
    it("should log when beep is played", () => {
      const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {})

      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("Acknowledgment beep played")
      )

      consoleLogSpy.mockRestore()
    })

    it("should log errors when beep fails", () => {
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
      mockAudioContext.createGain = vi.fn(() => {
        throw new Error("Gain node error")
      })

      const { result } = renderHook(() => useAudioManager())

      act(() => {
        result.current.playBeep()
      })

      expect(consoleErrorSpy).toHaveBeenCalled()

      consoleErrorSpy.mockRestore()
    })
  })
})
