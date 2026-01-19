"use client"

import { useEffect } from "react"
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder"
import { useVoiceFeedback } from "@/contexts/VoiceFeedbackContext"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Mic, MicOff, Loader2, Check, AlertCircle, Volume2, X } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { cn } from "@/lib/utils"

interface VoiceCommandProps {
  teamId: string | null
  roleId: string | null
  className?: string
  compact?: boolean  // Mobile mode - just show button
  onTranscriptChange?: (transcript: string, status: string) => void  // Expose transcript to parent
}

/**
 * Voice Command UI Component
 *
 * Displays:
 * - Microphone button to start/stop recording
 * - Status indicator (idle, connecting, listening, processing, sent, speaking, error)
 * - Real-time transcript display
 * - Corrected command display
 * - Voice feedback summary and playback indicator
 */
export function VoiceCommand({ teamId, roleId, className, compact = false, onTranscriptChange }: VoiceCommandProps) {
  const { state, isRecording, startRecording, stopRecording, clearTranscript, canRecord, canClear } = useVoiceRecorder()
  const { setHandsFreeMode } = useVoiceFeedback()
  const { toast } = useToast()

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

  const handleToggleRecording = async () => {
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

  const handleClear = () => {
    clearTranscript()
    toast({
      description: "Recording cleared",
      duration: 1500,
    })
  }

  const getStatusText = () => {
    switch (state.status) {
      case "idle":
        return "Hands-free mode OFF"
      case "connecting":
        return "Connecting..."
      case "listening":
        return state.isSpeaking ? "Listening..." : "Hands-free ON - speak anytime"
      case "processing":
        return "Sending command..."
      case "correcting":
        return "Correcting..."
      case "sent":
        return "Command sent! Still listening..."
      case "speaking":
        return "Speaking..."
      case "error":
        return state.error || "Error"
      default:
        return ""
    }
  }

  const getStatusColor = () => {
    switch (state.status) {
      case "listening":
        return state.isSpeaking ? "text-green-500" : "text-blue-500"
      case "connecting":
      case "processing":
      case "correcting":
        return "text-yellow-500"
      case "sent":
        return "text-green-500"
      case "speaking":
        return "text-purple-500"
      case "error":
        return "text-red-500"
      default:
        return "text-muted-foreground"
    }
  }

  const isDisabled = !teamId || !roleId || (!canRecord && !isRecording)

  // Compact mode - just the button (for mobile)
  if (compact) {
    return (
      <Button
        variant={isRecording ? "destructive" : state.status === "speaking" ? "secondary" : "outline"}
        size="icon"
        className={cn(
          "h-14 w-14 sm:h-12 sm:w-12 rounded-full transition-all shrink-0",
          isRecording && "animate-pulse",
          state.status === "speaking" && "animate-pulse",
          className
        )}
        onClick={handleToggleRecording}
        disabled={isDisabled}
        title={getStatusText()}
        aria-label={isRecording ? "Stop hands-free mode" : "Start hands-free mode"}
        aria-pressed={isRecording}
      >
        {state.status === "connecting" ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : state.status === "sent" ? (
          <Check className="h-5 w-5" />
        ) : state.status === "speaking" ? (
          <Volume2 className="h-5 w-5" />
        ) : state.status === "error" ? (
          <AlertCircle className="h-5 w-5" />
        ) : isRecording ? (
          <MicOff className="h-5 w-5" />
        ) : (
          <Mic className="h-5 w-5" />
        )}
      </Button>
    )
  }

  // Full mode with card
  return (
    <Card className={cn("border-border", className)}>
      <CardContent className="p-3 sm:p-4">
        <div className="flex items-center gap-3 sm:gap-4">
          {/* Microphone Button */}
          <Button
            variant={isRecording ? "destructive" : state.status === "speaking" ? "secondary" : "default"}
            size="icon"
            className={cn(
              "h-14 w-14 sm:h-12 sm:w-12 rounded-full transition-all shrink-0",
              isRecording && "animate-pulse",
              state.status === "speaking" && "animate-pulse"
            )}
            onClick={handleToggleRecording}
            disabled={isDisabled}
            aria-label={isRecording ? "Stop hands-free mode" : "Start hands-free mode"}
            aria-pressed={isRecording}
          >
            {state.status === "connecting" ? (
              <Loader2 className="h-5 w-5 sm:h-6 sm:w-6 animate-spin" />
            ) : state.status === "sent" ? (
              <Check className="h-5 w-5 sm:h-6 sm:w-6" />
            ) : state.status === "speaking" ? (
              <Volume2 className="h-5 w-5 sm:h-6 sm:w-6" />
            ) : state.status === "error" ? (
              <AlertCircle className="h-5 w-5 sm:h-6 sm:w-6" />
            ) : isRecording ? (
              <MicOff className="h-5 w-5 sm:h-6 sm:w-6" />
            ) : (
              <Mic className="h-5 w-5 sm:h-6 sm:w-6" />
            )}
          </Button>

          {/* Status and Transcript */}
          <div className="flex-1 min-w-0">
            {/* Status Text */}
            <p className={cn("text-xs sm:text-sm font-medium", getStatusColor())}>
              {getStatusText()}
            </p>

            {/* Transcript Display */}
            {state.transcript && (
              <p className="text-xs sm:text-sm text-foreground/80 mt-1 truncate">
                {state.transcript}
              </p>
            )}

            {/* Corrected Command Display */}
            {state.correctedCommand && (
              <p className="text-xs sm:text-sm text-green-500 mt-1 truncate">
                {state.correctedCommand}
              </p>
            )}

            {/* Voice Feedback Summary */}
            {state.feedbackSummary && state.status === "speaking" && (
              <p className="text-xs sm:text-sm text-purple-500 mt-1 truncate">
                {state.feedbackSummary}
              </p>
            )}

            {/* Hands-free hint - hidden on mobile */}
            {isRecording && state.status === "listening" && !state.isSpeaking && (
              <p className="hidden sm:block text-xs text-muted-foreground mt-1">
                Pause 5s after speaking to auto-send • Click mic to stop
              </p>
            )}
          </div>

          {/* Clear Button - Right side of transcript */}
          {canClear && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-destructive shrink-0"
              onClick={handleClear}
              title="Clear recording"
              aria-label="Clear recording"
            >
              <X className="h-4 w-4" />
            </Button>
          )}

          {/* VAD / Playback Indicator */}
          {(isRecording || state.status === "speaking") && (
            <div
              className={cn(
                "h-2 w-2 sm:h-3 sm:w-3 rounded-full transition-colors shrink-0",
                state.status === "speaking" ? "bg-purple-500 animate-pulse" :
                state.isSpeaking ? "bg-green-500" : "bg-muted"
              )}
              title={
                state.status === "speaking" ? "Playing feedback" :
                state.isSpeaking ? "Speaking detected" : "Waiting for speech"
              }
            />
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default VoiceCommand
