"use client"

import { useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Mic, MicOff, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import type { VoiceState } from "@/lib/voice-types"

interface VoiceInputToggleProps {
  teamId: string | null
  roleId: string | null
  className?: string
  onTranscriptChange?: (transcript: string, status: string) => void
  /** Voice recorder state (REQUIRED - passed from parent) */
  voiceState: VoiceState
  /** Whether recording is active (REQUIRED - passed from parent) */
  isRecording: boolean
  /** Start recording function (REQUIRED - passed from parent) */
  startRecording: (teamId: string, roleId: string) => Promise<void>
  /** Stop recording function (REQUIRED - passed from parent) */
  stopRecording: () => void
  /** Whether recording can start (REQUIRED - passed from parent) */
  canRecord: boolean
}

/**
 * Voice Input Toggle Button
 *
 * Controls voice command recording (microphone input).
 * Independent of audio output state.
 * Commands go to currently selected team/role.
 *
 * All voice state must be passed from parent (single source of truth).
 * This eliminates the dual-hook instance bug where two Soniox connections were created.
 */
export function VoiceInputToggle({
  teamId,
  roleId,
  className,
  onTranscriptChange,
  voiceState,
  isRecording,
  startRecording,
  stopRecording,
  canRecord,
}: VoiceInputToggleProps) {
  // All state comes from props - no useVoiceRecorder() call here!
  // hands-free mode sync is now centralized in TmuxController

  // Track previous teamId to detect ACTUAL team changes (not just isRecording changes)
  const prevTeamIdRef = useRef<string | null>(teamId)

  // Notify parent of transcript changes
  useEffect(() => {
    if (onTranscriptChange) {
      const displayText = voiceState.correctedCommand || voiceState.transcript || ""
      onTranscriptChange(displayText, voiceState.status)
    }
  }, [voiceState.transcript, voiceState.correctedCommand, voiceState.status, onTranscriptChange])

  // Safety: Auto-stop recording when team CHANGES (prevent commands to wrong team)
  // BUG FIX: Previous implementation fired when isRecording became true, immediately stopping recording.
  // Now we properly track the previous teamId and only stop when it actually changes.
  useEffect(() => {
    const prevTeamId = prevTeamIdRef.current
    prevTeamIdRef.current = teamId

    // Only stop if: recording is active AND team actually changed (not just on mount)
    if (isRecording && prevTeamId !== null && prevTeamId !== teamId) {
      console.log(`[VoiceInputToggle] Team changed from ${prevTeamId} to ${teamId} while recording - stopping`)
      stopRecording()
    }
  }, [teamId, isRecording, stopRecording])

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
    if (voiceState.status === "connecting") return "Connecting..."
    if (isRecording) return "Stop"
    return "Voice Input"
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
      aria-label={isRecording ? "Stop voice recording" : "Start voice recording"}
      aria-pressed={isRecording}
    >
      {voiceState.status === "connecting" ? (
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

export default VoiceInputToggle
