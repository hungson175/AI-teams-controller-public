/**
 * useAudioFeedback - Audio Feedback Hook
 *
 * Extracted from TmuxController.tsx as part of Sprint 3 FE-4 refactoring.
 *
 * Manages:
 * - Audio beep playback for UI feedback
 * - High beep (880Hz) = ON/Active state
 * - Low beep (440Hz) = OFF/Inactive state
 */

import { useCallback } from 'react'

export function useAudioFeedback() {
  const playBeep = useCallback((isActive: boolean) => {
    try {
      const ctx = new AudioContext()
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.frequency.value = isActive ? 880 : 440  // High = ON, Low = OFF
      gain.gain.value = 0.3
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.start()
      setTimeout(() => { osc.stop(); ctx.close() }, 150)
    } catch (e) {
      console.error("[useAudioFeedback] Error:", e)
    }
  }, [])

  return { playBeep }
}
