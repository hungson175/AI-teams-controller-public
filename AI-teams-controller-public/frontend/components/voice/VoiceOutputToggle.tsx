"use client"

import { useVoiceFeedback } from "@/contexts/VoiceFeedbackContext"
import { Button } from "@/components/ui/button"
import { Volume2, VolumeX, Bell, User } from "lucide-react"
import { cn } from "@/lib/utils"

interface VoiceOutputToggleProps {
  className?: string
}

/**
 * Voice Output Toggle Button
 *
 * Controls voice feedback audio playback mode (speaker output).
 * Independent of voice recording state.
 * Cycles through 4 modes: Voice → Off → Tone → Team → Voice
 */
export function VoiceOutputToggle({
  className
}: VoiceOutputToggleProps) {
  const { voiceFeedbackMode, setVoiceFeedbackMode } = useVoiceFeedback()

  const handleToggle = () => {
    // Haptic feedback on button press (mobile)
    if ('vibrate' in navigator) {
      navigator.vibrate(50)
    }

    // Cycle through modes: voice → off → tone → team_name → voice
    const nextMode =
      voiceFeedbackMode === "voice" ? "off" :
      voiceFeedbackMode === "off" ? "tone" :
      voiceFeedbackMode === "tone" ? "team_name" :
      "voice"
    setVoiceFeedbackMode(nextMode)
  }

  const getIcon = () => {
    switch (voiceFeedbackMode) {
      case "voice":
        return <Volume2 className="h-4 w-4" />
      case "off":
        return <VolumeX className="h-4 w-4" />
      case "tone":
        return <Bell className="h-4 w-4" />
      case "team_name":
        return <User className="h-4 w-4" />
    }
  }

  const getLabel = () => {
    switch (voiceFeedbackMode) {
      case "voice":
        return "Voice"
      case "off":
        return "Off"
      case "tone":
        return "Tone"
      case "team_name":
        return "Team"
    }
  }

  const getAriaLabel = () => {
    switch (voiceFeedbackMode) {
      case "voice":
        return "Voice feedback mode (click for off)"
      case "off":
        return "Feedback off (click for tone)"
      case "tone":
        return "Tone feedback mode (click for team)"
      case "team_name":
        return "Team name feedback mode (click for voice)"
    }
  }

  return (
    <Button
      variant={voiceFeedbackMode === "off" ? "outline" : "ghost"}
      size="sm"
      className={cn(
        "gap-2 transition-all",
        voiceFeedbackMode === "off" && "text-muted-foreground",
        voiceFeedbackMode === "tone" && "text-blue-500",
        className
      )}
      onClick={handleToggle}
      aria-label={getAriaLabel()}
      title={`Feedback mode: ${getLabel()} (click to cycle)`}
    >
      {getIcon()}
      <span className="hidden sm:inline">
        {getLabel()}
      </span>
    </Button>
  )
}

export default VoiceOutputToggle
