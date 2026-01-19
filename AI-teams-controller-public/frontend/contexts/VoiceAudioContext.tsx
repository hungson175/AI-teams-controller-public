"use client"

/**
 * VoiceAudioContext - Audio Playback Management (Sprint 6: SRP)
 *
 * Extracted from VoiceFeedbackContext as part of SOLID refactoring.
 *
 * Responsibility: Audio playback management ONLY
 * - Play notification tones (cat meow)
 * - Play voice feedback audio (base64 MP3)
 * - Manage voice feedback mode (off/tone/team_name/voice)
 * - Manage hands-free mode
 * - Audio lifecycle management
 *
 * Does NOT handle:
 * - WebSocket connection (VoiceWebSocketContext responsibility)
 * - Notifications (VoiceFeedbackProvider responsibility)
 */

import {
  createContext,
  useContext,
  useState,
  useRef,
  useCallback,
  useMemo,
  type ReactNode,
} from "react"
import {
  type VoiceFeedbackMode,
  getVoiceFeedbackMode,
  setVoiceFeedbackMode as saveVoiceFeedbackMode,
} from "@/lib/voice-types"

// ============================================
// Types
// ============================================

interface VoiceAudioContextValue {
  /** Current voice feedback mode */
  voiceFeedbackMode: VoiceFeedbackMode
  /** Whether hands-free mode is enabled */
  isHandsFreeMode: boolean
  /** Set voice feedback mode (off/tone/team_name/voice) */
  setVoiceFeedbackMode: (mode: VoiceFeedbackMode) => void
  /** Set hands-free mode */
  setHandsFreeMode: (enabled: boolean) => void
  /** Play notification tone (cat meow) */
  playTone: () => void
  /** Play voice feedback audio from base64 */
  playAudio: (base64Audio: string, notificationId: string) => void
}

// ============================================
// Context
// ============================================

const VoiceAudioContext = createContext<VoiceAudioContextValue | null>(null)

// ============================================
// Provider Component
// ============================================

interface VoiceAudioProviderProps {
  children: ReactNode
  /** Optional callback when audio playback completes */
  onAudioComplete?: (notificationId: string) => void
}

export function VoiceAudioProvider({ children, onAudioComplete }: VoiceAudioProviderProps) {
  // State
  const [voiceFeedbackMode, setVoiceFeedbackModeState] = useState<VoiceFeedbackMode>(() =>
    getVoiceFeedbackMode()
  )
  const [isHandsFreeMode, setIsHandsFreeMode] = useState(false)

  // Refs
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const onAudioCompleteRef = useRef(onAudioComplete)

  // Sync callback ref
  useMemo(() => {
    onAudioCompleteRef.current = onAudioComplete
  }, [onAudioComplete])

  // ============================================
  // Audio Playback
  // ============================================

  const playTone = useCallback(() => {
    try {
      // Play cat meow audio file
      const audio = new Audio("/sounds/meow.mp3")
      audio.volume = 0.5 // 50% volume

      audio.play().catch((error) => {
        console.error("[VoiceAudio] Meow playback error:", error)
      })

      console.log("[VoiceAudio] Playing cat meow notification")
    } catch (error) {
      console.error("[VoiceAudio] Tone playback error:", error)
    }
  }, [])

  const playAudio = useCallback((base64Audio: string, notificationId: string) => {
    console.log(
      `[VoiceAudio] playAudio() CALLED - notificationId: ${notificationId}, audioLength: ${
        base64Audio?.length || 0
      }`
    )

    // Global lock to prevent multiple tabs playing
    if ((window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__) {
      console.log("[VoiceAudio] Another tab is playing, skipping")
      return
    }

    if (!base64Audio || base64Audio.length === 0) {
      console.error("[VoiceAudio] ❌ No audio data provided (empty or null)")
      return
    }

    try {
      // Stop any currently playing audio
      if (audioRef.current) {
        console.log("[VoiceAudio] Stopping currently playing audio")
        audioRef.current.pause()
        audioRef.current = null
      }

      console.log(`[VoiceAudio] Decoding base64 audio (${base64Audio.length} chars)`)
      // Decode base64 to blob
      const binaryString = atob(base64Audio)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      const blob = new Blob([bytes], { type: "audio/mp3" })
      const audioUrl = URL.createObjectURL(blob)
      console.log(`[VoiceAudio] Created blob: ${blob.size} bytes, URL: ${audioUrl}`)

      const audio = new Audio(audioUrl)
      audioRef.current = audio

      // Set global lock
      ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = true

      audio.onended = () => {
        console.log("[VoiceAudio] ✅ Audio playback ENDED")
        URL.revokeObjectURL(audioUrl)
        audioRef.current = null
        ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ =
          false

        // Notify parent of completion
        if (onAudioCompleteRef.current) {
          onAudioCompleteRef.current(notificationId)
        }
      }

      audio.onerror = (e) => {
        console.error("[VoiceAudio] ❌ Audio element ERROR:", e)
        URL.revokeObjectURL(audioUrl)
        audioRef.current = null
        ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ =
          false
      }

      console.log("[VoiceAudio] Calling audio.play()...")
      audio
        .play()
        .then(() => {
          console.log("[VoiceAudio] ✅ audio.play() promise RESOLVED - audio playing")
        })
        .catch((e) => {
          console.error("[VoiceAudio] ❌ audio.play() promise REJECTED:", e.name, e.message)
          ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ =
            false
        })

      console.log("[VoiceAudio] Playing audio for notification:", notificationId)
    } catch (error) {
      console.error("[VoiceAudio] ❌ Audio decode/setup error:", error)
      ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ =
        false
    }
  }, [])

  // ============================================
  // Mode Management
  // ============================================

  const handleSetVoiceFeedbackMode = useCallback((mode: VoiceFeedbackMode) => {
    setVoiceFeedbackModeState(mode)
    saveVoiceFeedbackMode(mode) // Save to localStorage

    // If switching to OFF mode, stop any currently playing audio immediately
    if (mode === "off" && audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
      ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ =
        false
    }

    console.log("[VoiceAudio] Feedback mode:", mode.toUpperCase())
  }, [])

  const handleSetHandsFreeMode = useCallback((enabled: boolean) => {
    setIsHandsFreeMode(enabled)
    console.log("[VoiceAudio] Hands-free mode:", enabled ? "ON" : "OFF")
  }, [])

  // ============================================
  // Context Value
  // ============================================

  const contextValue: VoiceAudioContextValue = useMemo(
    () => ({
      voiceFeedbackMode,
      isHandsFreeMode,
      setVoiceFeedbackMode: handleSetVoiceFeedbackMode,
      setHandsFreeMode: handleSetHandsFreeMode,
      playTone,
      playAudio,
    }),
    [voiceFeedbackMode, isHandsFreeMode, handleSetVoiceFeedbackMode, handleSetHandsFreeMode, playTone, playAudio]
  )

  return <VoiceAudioContext.Provider value={contextValue}>{children}</VoiceAudioContext.Provider>
}

// ============================================
// Hook
// ============================================

export function useVoiceAudio(): VoiceAudioContextValue {
  const context = useContext(VoiceAudioContext)
  if (!context) {
    throw new Error("useVoiceAudio must be used within VoiceAudioProvider")
  }
  return context
}

export default VoiceAudioContext
