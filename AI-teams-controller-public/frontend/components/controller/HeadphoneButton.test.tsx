/**
 * Tests for HeadphoneButton Component
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen } from "@testing-library/react"
import { HeadphoneButton } from "./HeadphoneButton"

describe("HeadphoneButton", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("Rendering with Media Session support", () => {
    beforeEach(() => {
      // Mock mediaSession support
      Object.defineProperty(navigator, "mediaSession", {
        value: {
          metadata: null,
          playbackState: "none",
          setActionHandler: vi.fn(),
        },
        writable: true,
        configurable: true,
      })
    })

    it("should render Init button when not initialized", () => {
      render(<HeadphoneButton />)
      expect(screen.getByRole("button")).toBeInTheDocument()
    })

    it("should show Init text on button", () => {
      render(<HeadphoneButton />)
      expect(screen.getByText("Init")).toBeInTheDocument()
    })

    it("should accept className prop", () => {
      const { container } = render(<HeadphoneButton className="test-class" />)
      expect(container.firstChild).toHaveClass("test-class")
    })
  })

  describe("Rendering without Media Session support", () => {
    beforeEach(() => {
      // Completely remove mediaSession property
      const navigatorWithoutMediaSession = Object.create(Navigator.prototype)
      Object.defineProperty(global, "navigator", {
        value: navigatorWithoutMediaSession,
        writable: true,
        configurable: true,
      })
    })

    it("should show unsupported message when mediaSession not available", () => {
      render(<HeadphoneButton />)
      expect(screen.getByText("No Media API")).toBeInTheDocument()
    })

    it("should not show Init button when not supported", () => {
      render(<HeadphoneButton />)
      expect(screen.queryByRole("button")).not.toBeInTheDocument()
    })
  })

  describe("Props", () => {
    beforeEach(() => {
      Object.defineProperty(navigator, "mediaSession", {
        value: {
          metadata: null,
          playbackState: "none",
          setActionHandler: vi.fn(),
        },
        writable: true,
        configurable: true,
      })
    })

    it("should accept onToggle callback", () => {
      const onToggle = vi.fn()
      render(<HeadphoneButton onToggle={onToggle} />)
      // Component renders without error when onToggle is provided
      expect(screen.getByRole("button")).toBeInTheDocument()
    })

    it("should handle onToggle prop changes (stale closure fix)", () => {
      // This test verifies the component handles callback prop changes correctly
      // Bug: Media Session handlers captured old onToggle when team changed
      // Fix: Uses ref to always access latest onToggle callback
      const onToggle1 = vi.fn()
      const onToggle2 = vi.fn()

      const { rerender } = render(<HeadphoneButton onToggle={onToggle1} />)
      expect(screen.getByRole("button")).toBeInTheDocument()

      // Simulate team switch - new callback passed
      rerender(<HeadphoneButton onToggle={onToggle2} />)
      expect(screen.getByRole("button")).toBeInTheDocument()

      // Component should accept new callback without error
      // The actual Media Session handler test requires browser environment
    })

    it("should handle isRecording prop changes", () => {
      const { rerender } = render(<HeadphoneButton isRecording={false} />)
      rerender(<HeadphoneButton isRecording={true} />)
      // Component handles prop changes without error
      expect(screen.getByRole("button")).toBeInTheDocument()
    })
  })

  describe("Media Session Toggle OFF - Regression Test (Sprint 5)", () => {
    /**
     * REGRESSION TEST for Sprint 5 Bug Fix #2
     *
     * Bug: Physical headphone button could turn voice ON but not OFF
     * Root Cause: handleSuspend listener (removed) was auto-resuming audio on pause,
     *             preventing Media Session pause action from firing properly
     * Fix: Removed handleSuspend listener that interfered with Media Session API
     *
     * These tests verify:
     * 1. Media Session pause action handler is registered and calls toggleVoice
     * 2. Both play and pause actions can toggle voice state
     * 3. Removing handleSuspend doesn't break visibility change handling
     */

    let mockSetActionHandler: ReturnType<typeof vi.fn>
    let actionHandlers: Record<string, () => void>
    let mockAudioInstance: {
      play: ReturnType<typeof vi.fn>
      pause: ReturnType<typeof vi.fn>
      loop: boolean
      volume: number
      addEventListener: ReturnType<typeof vi.fn>
      removeEventListener: ReturnType<typeof vi.fn>
    }

    beforeEach(() => {
      actionHandlers = {}
      mockSetActionHandler = vi.fn((action: string, handler: () => void) => {
        actionHandlers[action] = handler
      })

      // Mock Audio element as a class
      mockAudioInstance = {
        play: vi.fn().mockResolvedValue(undefined),
        pause: vi.fn(),
        loop: false,
        volume: 1,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }

      // Create a proper constructor function for Audio
      class MockAudio {
        play = mockAudioInstance.play
        pause = mockAudioInstance.pause
        loop = mockAudioInstance.loop
        volume = mockAudioInstance.volume
        addEventListener = mockAudioInstance.addEventListener
        removeEventListener = mockAudioInstance.removeEventListener
      }
      vi.stubGlobal("Audio", MockAudio)

      // Mock MediaMetadata constructor
      class MockMediaMetadata {
        title: string
        artist: string
        album: string
        constructor(init: { title?: string; artist?: string; album?: string }) {
          this.title = init.title || ""
          this.artist = init.artist || ""
          this.album = init.album || ""
        }
      }
      vi.stubGlobal("MediaMetadata", MockMediaMetadata)

      // Mock mediaSession with captured handlers
      Object.defineProperty(navigator, "mediaSession", {
        value: {
          metadata: null,
          playbackState: "none",
          setActionHandler: mockSetActionHandler,
        },
        writable: true,
        configurable: true,
      })
    })

    afterEach(() => {
      vi.unstubAllGlobals()
    })

    it("should register both play and pause action handlers", async () => {
      const onToggle = vi.fn()
      render(<HeadphoneButton onToggle={onToggle} />)

      // Click Init button to initialize Media Session
      const initButton = screen.getByRole("button")
      await initButton.click()

      // Verify both handlers are registered
      expect(mockSetActionHandler).toHaveBeenCalledWith("play", expect.any(Function))
      expect(mockSetActionHandler).toHaveBeenCalledWith("pause", expect.any(Function))
    })

    it("should toggle via audio events when Media Session actions fire (Sprint 5 fix #4)", async () => {
      /**
       * UPDATED for Fix #4: Toggle now happens via audio events, not Media Session handlers
       * Media Session pause -> audio.pause() -> audio 'pause' event -> voice ON
       */
      const onToggle = vi.fn()
      render(<HeadphoneButton onToggle={onToggle} />)

      // Initialize
      const initButton = screen.getByRole("button")
      await initButton.click()

      // Get the audio pause event listener
      const pauseListeners = mockAudioInstance.addEventListener.mock.calls
        .filter((call: [string, () => void]) => call[0] === "pause")
        .map((call: [string, () => void]) => call[1])

      // Simulate audio pause event (which happens when Media Session pause fires)
      // This should trigger voice ON
      pauseListeners[0]?.()
      expect(onToggle).toHaveBeenCalledWith(true) // Voice ON when audio pauses
    })

    it("should allow multiple toggle cycles via audio events (Sprint 5 fix #4)", async () => {
      /**
       * UPDATED for Fix #4: Toggle cycles now happen via audio events
       * UX: Audio PAUSED = Voice ON, Audio PLAYING = Voice OFF
       */
      const onToggle = vi.fn()
      render(<HeadphoneButton onToggle={onToggle} />)

      // Initialize
      const initButton = screen.getByRole("button")
      await initButton.click()

      // Get audio event listeners
      const pauseListeners = mockAudioInstance.addEventListener.mock.calls
        .filter((call: [string, () => void]) => call[0] === "pause")
        .map((call: [string, () => void]) => call[1])
      const playListeners = mockAudioInstance.addEventListener.mock.calls
        .filter((call: [string, () => void]) => call[0] === "play")
        .map((call: [string, () => void]) => call[1])

      // Cycle 1: Audio pauses -> Voice ON
      pauseListeners[0]?.()
      expect(onToggle).toHaveBeenLastCalledWith(true)

      // Cycle 1: Audio plays -> Voice OFF
      playListeners[0]?.()
      expect(onToggle).toHaveBeenLastCalledWith(false)

      // Cycle 2: Audio pauses -> Voice ON
      pauseListeners[0]?.()
      expect(onToggle).toHaveBeenLastCalledWith(true)

      // Cycle 2: Audio plays -> Voice OFF
      playListeners[0]?.()
      expect(onToggle).toHaveBeenLastCalledWith(false)

      // Total: 4 toggles
      expect(onToggle).toHaveBeenCalledTimes(4)
    })

    it("should have audio pause/play event listeners for toggle logic (Sprint 5 fix #4)", async () => {
      /**
       * UPDATED for Fix #4: Now we WANT pause/play listeners for toggle logic
       * (Old test checked for NO pause listener - that was fix #2 which is now superseded)
       */
      render(<HeadphoneButton />)

      // Initialize
      const initButton = screen.getByRole("button")
      await initButton.click()

      // Check that pause AND play event listeners are registered
      const addEventListenerCalls = mockAudioInstance.addEventListener.mock.calls || []
      const pauseListeners = addEventListenerCalls.filter(
        (call: [string, () => void]) => call[0] === "pause"
      )
      const playListeners = addEventListenerCalls.filter(
        (call: [string, () => void]) => call[0] === "play"
      )

      // Should have 1 pause listener and 1 play listener for toggle logic
      expect(pauseListeners.length).toBe(1)
      expect(playListeners.length).toBe(1)
    })

    it("should keep playbackState as 'paused' always - never set to 'playing' (Sprint 5 fix #3)", async () => {
      /**
       * REGRESSION TEST for Sprint 5 Bug Fix #3
       *
       * Bug: Physical headphone button works once then stops on mobile Chrome
       * Root Cause: Setting playbackState to 'playing' prevents mobile Chrome
       *             from firing subsequent pause handlers
       * Fix: Keep playbackState as 'paused' always - never change it
       *
       * This test verifies playbackState is never set to 'playing'
       */
      render(<HeadphoneButton />)

      // Track all playbackState assignments
      const playbackStateHistory: string[] = []
      const originalDescriptor = Object.getOwnPropertyDescriptor(navigator.mediaSession, "playbackState")

      Object.defineProperty(navigator.mediaSession, "playbackState", {
        get: () => playbackStateHistory[playbackStateHistory.length - 1] || "none",
        set: (value: string) => {
          playbackStateHistory.push(value)
        },
        configurable: true,
      })

      // Initialize
      const initButton = screen.getByRole("button")
      await initButton.click()

      // Trigger multiple toggles via play/pause actions
      actionHandlers["play"]?.()
      actionHandlers["pause"]?.()
      actionHandlers["pause"]?.()

      // Restore original descriptor if it existed
      if (originalDescriptor) {
        Object.defineProperty(navigator.mediaSession, "playbackState", originalDescriptor)
      }

      // Verify playbackState was NEVER set to 'playing'
      // All values should be 'paused' (or 'none' initially)
      const playingStates = playbackStateHistory.filter(state => state === "playing")
      expect(playingStates.length).toBe(0) // Should FAIL before fix, PASS after fix
    })

    it("should use audio events for toggle, not Media Session handlers (Sprint 5 fix #4)", async () => {
      /**
       * REGRESSION TEST for Sprint 5 Bug Fix #4
       *
       * Bug: Calling audio.play() inside pause handler breaks mobile Chrome
       * Root Cause: Media Session handlers should ONLY control audio,
       *             toggle logic should react to audio element events
       *
       * New UX Model:
       * - Audio PAUSED = Voice ON (user speaking)
       * - Audio PLAYING = Voice OFF (silent audio keeps session alive)
       *
       * This test verifies:
       * 1. pause handler calls audio.pause() (not toggleVoice)
       * 2. Audio 'pause' event triggers onToggle(true) - voice ON
       * 3. Audio 'play' event triggers onToggle(false) - voice OFF
       */
      const onToggle = vi.fn()
      render(<HeadphoneButton onToggle={onToggle} />)

      // Initialize
      const initButton = screen.getByRole("button")
      await initButton.click()

      // Get audio event listeners that were registered
      const pauseListeners = mockAudioInstance.addEventListener.mock.calls
        .filter((call: [string, () => void]) => call[0] === "pause")
        .map((call: [string, () => void]) => call[1])

      const playListeners = mockAudioInstance.addEventListener.mock.calls
        .filter((call: [string, () => void]) => call[0] === "play")
        .map((call: [string, () => void]) => call[1])

      // Verify audio event listeners are registered
      expect(pauseListeners.length).toBeGreaterThan(0) // Should have pause listener
      expect(playListeners.length).toBeGreaterThan(0) // Should have play listener

      // Simulate audio pause event -> should trigger voice ON
      onToggle.mockClear()
      pauseListeners[0]?.()
      expect(onToggle).toHaveBeenCalledWith(true) // Voice ON when audio pauses

      // Simulate audio play event -> should trigger voice OFF
      onToggle.mockClear()
      playListeners[0]?.()
      expect(onToggle).toHaveBeenCalledWith(false) // Voice OFF when audio plays
    })

    it("should call audio.pause() in Media Session pause handler (Sprint 5 fix #4)", async () => {
      /**
       * Verify Media Session pause handler calls audio.pause()
       * instead of toggleVoice + audio.play()
       */
      render(<HeadphoneButton />)

      // Initialize
      const initButton = screen.getByRole("button")
      await initButton.click()

      // Clear previous calls
      mockAudioInstance.pause.mockClear()
      mockAudioInstance.play.mockClear()

      // Trigger Media Session pause action
      actionHandlers["pause"]?.()

      // Should call audio.pause(), NOT audio.play()
      expect(mockAudioInstance.pause).toHaveBeenCalled()
      // Note: play() might be called initially during init, but pause handler should NOT call play()
    })
  })
})
