"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Headphones, HeadphoneOff } from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * HeadphoneButton Component
 *
 * Enables hardware headphone button mode for voice control.
 * Uses Media Session API with silent audio workaround.
 *
 * IMPORTANT: This button controls the hardware button MODE/PREFERENCE only.
 * - Clicking the UI button does NOT toggle voice recording
 * - Only physical headphone button presses toggle recording (via Media Session API)
 *
 * Features:
 * - Initialize button to enable hardware headphone button mode
 * - Visual indicator showing current recording state
 * - Press count display (counts physical button presses)
 * - Handles AudioContext suspension on mobile
 *
 * Based on SA's research in experiments/headphone-button-demo/
 */
export interface HeadphoneButtonProps {
  /** External recording state to sync with (bidirectional sync) */
  isRecording?: boolean
  onToggle?: (isActive: boolean) => void
  className?: string
}

export function HeadphoneButton({ isRecording: externalIsRecording, onToggle, className }: HeadphoneButtonProps) {
  const [isInitialized, setIsInitialized] = useState(false)
  const [isActive, setIsActive] = useState(false)
  const [pressCount, setPressCount] = useState(0)
  const [isSupported, setIsSupported] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  // Ref to avoid stale closure in Media Session handlers
  const isActiveRef = useRef(false)
  // Ref to hold latest onToggle callback - prevents stale closure when team changes
  const onToggleRef = useRef(onToggle)

  // Check API support on mount
  useEffect(() => {
    const supported = "mediaSession" in navigator
    setIsSupported(supported)
  }, [])

  // Keep onToggle ref updated - ensures Media Session handlers always use current callback
  useEffect(() => {
    onToggleRef.current = onToggle
  }, [onToggle])

  // Sync internal state with external isRecording (bidirectional sync)
  useEffect(() => {
    if (externalIsRecording !== undefined && isInitialized) {
      if (externalIsRecording !== isActiveRef.current) {
        console.log("[HeadphoneButton] Syncing with external isRecording:", externalIsRecording)
        isActiveRef.current = externalIsRecording
        setIsActive(externalIsRecording)
        // NOTE: Do NOT change playbackState here - mobile Chrome requires it to stay 'paused'
      }
    }
  }, [externalIsRecording, isInitialized])

  // Create silent audio element for Media Session API (Chrome mobile needs 5+ seconds)
  const createSilentAudio = useCallback(() => {
    const audio = new Audio("/audio/silent-5s.wav")
    audio.loop = true
    audio.volume = 0.01 // Nearly silent but not zero (Firefox compatibility)
    return audio
  }, [])

  // Toggle voice state - updates both state and ref
  // Uses onToggleRef to avoid stale closure - always calls latest callback even after team changes
  const toggleVoice = useCallback((source: string) => {
    const newState = !isActiveRef.current
    isActiveRef.current = newState
    setIsActive(newState)
    setPressCount(c => c + 1)
    // Use ref to always call latest onToggle (prevents stale team reference)
    onToggleRef.current?.(newState)
    console.log(`[HeadphoneButton] Voice ${newState ? "ON" : "OFF"} (via ${source})`)
    // NOTE: Do NOT change playbackState here - mobile Chrome requires it to stay 'paused'
  }, [])  // No dependencies - uses refs for latest values

  // Initialize Media Session
  const initMediaSession = useCallback(async () => {
    if (isInitialized || !isSupported) return

    try {
      // Create and store audio element
      const audio = createSilentAudio()
      audioRef.current = audio

      // Set up media session metadata
      navigator.mediaSession.metadata = new MediaMetadata({
        title: "Voice Input",
        artist: "AI Teams Controller",
        album: "Voice Commands",
      })

      // FIX #4: Media Session handlers ONLY control audio - don't call toggleVoice here!
      // Let audio element events handle the toggle logic (see below)
      navigator.mediaSession.setActionHandler("play", () => {
        console.log("[HeadphoneButton] Play action received - resuming audio")
        audioRef.current?.play().catch(e => console.error("Audio play error:", e))
      })

      navigator.mediaSession.setActionHandler("pause", () => {
        console.log("[HeadphoneButton] Pause action received - pausing audio")
        audioRef.current?.pause()
      })

      // Try to register optional handlers
      try {
        navigator.mediaSession.setActionHandler("stop", () => {
          console.log("[HeadphoneButton] Stop action received")
          audioRef.current?.pause()
        })
      } catch {
        // Handler not supported
      }

      // FIX #4: Use audio element events for toggle logic
      // UX Model: Audio PAUSED = Voice ON, Audio PLAYING = Voice OFF
      audio.addEventListener("pause", () => {
        console.log("[HeadphoneButton] Audio paused - starting voice")
        if (!isActiveRef.current) {
          isActiveRef.current = true
          setIsActive(true)
          setPressCount(c => c + 1)
          onToggleRef.current?.(true)
        }
      })

      audio.addEventListener("play", () => {
        console.log("[HeadphoneButton] Audio playing - stopping voice")
        if (isActiveRef.current) {
          isActiveRef.current = false
          setIsActive(false)
          setPressCount(c => c + 1)
          onToggleRef.current?.(false)
        }
      })

      // Start playing silent audio to activate media session
      await audio.play()
      navigator.mediaSession.playbackState = "paused"

      setIsInitialized(true)
      console.log("[HeadphoneButton] Media Session initialized successfully")
    } catch (error) {
      console.error("[HeadphoneButton] Initialization error:", error)
    }
  }, [isInitialized, isSupported, createSilentAudio, toggleVoice])

  // Handle visibility change - resume audio when tab becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && isInitialized && audioRef.current) {
        audioRef.current.play().catch(() => {})
        console.log("[HeadphoneButton] Visibility restored - audio resumed")
      }
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange)
  }, [isInitialized])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, [])

  if (!isSupported) {
    return (
      <div className={cn("flex items-center gap-1 text-xs text-muted-foreground", className)}>
        <HeadphoneOff className="h-3 w-3" />
        <span className="hidden sm:inline">No Media API</span>
      </div>
    )
  }

  return (
    <div className={cn("flex items-center gap-1", className)}>
      {!isInitialized ? (
        <Button
          variant="outline"
          size="sm"
          onClick={initMediaSession}
          className="h-7 text-xs gap-1 px-2"
        >
          <Headphones className="h-3 w-3" />
          <span className="hidden sm:inline">Init</span>
        </Button>
      ) : (
        <div className="flex items-center gap-1">
          <div
            className={cn(
              "w-6 h-6 rounded-full flex items-center justify-center transition-all",
              isActive
                ? "bg-red-500 text-white animate-pulse"
                : "bg-muted text-muted-foreground"
            )}
            title="Hardware headphone button mode enabled - use physical headphone button to toggle voice"
          >
            <Headphones className="h-3 w-3" />
          </div>
          {pressCount > 0 && (
            <span className="text-xs text-muted-foreground font-mono">
              {pressCount}
            </span>
          )}
        </div>
      )}
    </div>
  )
}
