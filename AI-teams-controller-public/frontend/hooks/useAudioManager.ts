"use client"

import { useCallback } from "react"

/**
 * Return type for useAudioManager hook
 */
export interface UseAudioManagerReturn {
  /** Play acknowledgment beep sound */
  playBeep: () => void
}

/**
 * useAudioManager Hook
 *
 * Manages audio feedback using Web Audio API.
 *
 * Features:
 * - Plays acknowledgment beep (880Hz A5 note, sine wave)
 * - 150ms duration with fade in/out envelope to prevent clicks
 * - Progressive enhancement (fails silently if AudioContext unavailable)
 * - Automatic cleanup via onended callback
 */
export function useAudioManager(): UseAudioManagerReturn {
  /**
   * Play acknowledgment beep when command is received
   * Uses Web Audio API to generate a short chime sound
   */
  const playBeep = useCallback(() => {
    try {
      // Create audio context (supports webkit prefix for older browsers)
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
      if (!AudioContextClass) {
        console.log("[AudioManager] AudioContext not supported")
        return
      }

      const audioCtx = new AudioContextClass()
      const oscillator = audioCtx.createOscillator()
      const gainNode = audioCtx.createGain()

      // Pleasant chime: 880Hz (A5) for 150ms
      oscillator.type = "sine"
      oscillator.frequency.setValueAtTime(880, audioCtx.currentTime)

      // Quick fade in/out to avoid clicks
      gainNode.gain.setValueAtTime(0, audioCtx.currentTime)
      gainNode.gain.linearRampToValueAtTime(0.3, audioCtx.currentTime + 0.02)
      gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.15)

      oscillator.connect(gainNode)
      gainNode.connect(audioCtx.destination)

      oscillator.start(audioCtx.currentTime)
      oscillator.stop(audioCtx.currentTime + 0.15)

      // Cleanup
      oscillator.onended = () => audioCtx.close()

      console.log("[AudioManager] Acknowledgment beep played")
    } catch (error) {
      console.error("[AudioManager] Beep error:", error)
      // Non-critical - don't throw
    }
  }, [])

  return {
    playBeep,
  }
}
