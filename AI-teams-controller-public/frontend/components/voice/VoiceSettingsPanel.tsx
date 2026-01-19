"use client"

import { useState, useEffect, useCallback } from "react"
import { Slider } from "@/components/ui/slider"
import {
  getSpeechSpeed,
  setSpeechSpeed,
  MIN_SPEECH_SPEED,
  MAX_SPEECH_SPEED,
} from "@/lib/voice-types"

// ============================================
// Types
// ============================================

interface VoiceSettingsPanelProps {
  className?: string
}

// ============================================
// Component
// ============================================

/**
 * Voice Settings Panel - MINIMAL
 *
 * Just slider + number. No text, no labels, no descriptions.
 */
export function VoiceSettingsPanel({ className }: VoiceSettingsPanelProps) {
  const [speechSpeed, setSpeechSpeedState] = useState<number>(1.0)

  useEffect(() => {
    const stored = getSpeechSpeed()
    setSpeechSpeedState(stored ?? 1.0)
  }, [])

  const handleSpeedChange = useCallback((value: number[]) => {
    const newSpeed = value[0]
    setSpeechSpeedState(newSpeed)
    setSpeechSpeed(newSpeed)
    window.dispatchEvent(new CustomEvent("speech-speed-changed", {
      detail: { speed: newSpeed },
    }))
  }, [])

  return (
    <div className={className}>
      <div className="flex items-center gap-3">
        <Slider
          value={[speechSpeed]}
          min={MIN_SPEECH_SPEED}
          max={MAX_SPEECH_SPEED}
          step={0.1}
          onValueChange={handleSpeedChange}
          className="flex-1"
        />
        <span className="text-sm font-medium min-w-[3rem] text-right">
          {speechSpeed.toFixed(1)}x
        </span>
      </div>
    </div>
  )
}

export default VoiceSettingsPanel
