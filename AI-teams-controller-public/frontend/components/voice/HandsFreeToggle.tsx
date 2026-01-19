"use client"

import { useEffect } from "react"
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder"
import { useVoiceFeedback } from "@/contexts/VoiceFeedbackContext"
import { Button } from "@/components/ui/button"
import { Mic, MicOff, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface HandsFreeToggleProps {
  teamId: string | null
  roleId: string | null
  className?: string
  onTranscriptChange?: (transcript: string, status: string) => void
}

/**
 * Hands-Free Toggle Button for Header
 *
 * Global toggle for hands-free voice mode.
 * Commands go to currently selected team/role.
 * Mobile: icon-only. Desktop: icon + text.
 */
export function HandsFreeToggle({
  teamId,
  roleId,
  className,
  onTranscriptChange
}: HandsFreeToggleProps) {
  const { state, isRecording, startRecording, stopRecording, canRecord } = useVoiceRecorder()
  const { setHandsFreeMode } = useVoiceFeedback()

  // Sync hands-free mode with VoiceFeedbackContext for audio playback control
  useEffect(() => {
    setHandsFreeMode(isRecording)
  }, [isRecording, setHandsFreeMode])

  // Notify parent of transcript changes
  useEffect(() => {
    if (onTranscriptChange) {
      const displayText = state.correctedCommand || state.transcript || ""
      onTranscriptChange(displayText, state.status)
    }
  }, [state.transcript, state.correctedCommand, state.status, onTranscriptChange])

  const handleToggle = async () => {
    if (!teamId || !roleId) return

    // Haptic feedback on button press (mobile)
    if ('vibrate' in navigator) {
      navigator.vibrate(50)
    }

    if (isRecording) {
      stopRecording()
    } else {
      await startRecording(teamId, roleId)
    }
  }

  const isDisabled = !teamId || !roleId || (!canRecord && !isRecording)

  const getButtonText = () => {
    if (state.status === "connecting") return "Connecting..."
    if (isRecording) return "Stop"
    return "Hands-Free"
  }

  return (
    <Button
      variant={isRecording ? "destructive" : "ghost"}
      size="sm"
      className={cn(
        "gap-2 transition-all",
        isRecording && "animate-pulse",
        className
      )}
      onClick={handleToggle}
      disabled={isDisabled}
      aria-label={isRecording ? "Stop hands-free mode" : "Start hands-free mode"}
      aria-pressed={isRecording}
    >
      {state.status === "connecting" ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : isRecording ? (
        <MicOff className="h-4 w-4" />
      ) : (
        <Mic className="h-4 w-4" />
      )}
      <span className="hidden sm:inline">
        {getButtonText()}
      </span>
    </Button>
  )
}

export default HandsFreeToggle
