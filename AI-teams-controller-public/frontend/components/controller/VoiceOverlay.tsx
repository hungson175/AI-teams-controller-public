"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, Radio } from "lucide-react"
import { VoiceInputToggle } from "@/components/voice/VoiceInputToggle"
import { VoiceOutputToggle } from "@/components/voice/VoiceOutputToggle"
import { cn } from "@/lib/utils"
import type { VoiceState } from "@/lib/voice-types"

/**
 * Props for VoiceOverlay component
 */
export interface VoiceOverlayProps {
  /** Number of unread voice feedback notifications */
  unreadCount: number
  /** Whether the voice feedback WebSocket is connected */
  isFeedbackConnected: boolean
  /** Currently selected team ID (can be null) */
  selectedTeam: string | null
  /** Currently selected role ID (can be null) */
  selectedRole: string | null
  /** Callback when notification panel toggle is requested */
  onTogglePanel: () => void
  /** Callback when voice transcript changes */
  onTranscriptChange: (transcript: string, status: string) => void
  /** Voice recorder state (REQUIRED - lifted from useVoiceRecorder in TmuxController) */
  voiceState: VoiceState
  /** Whether recording is active (REQUIRED) */
  isRecording: boolean
  /** Start recording function (REQUIRED) */
  startRecording: (teamId: string, roleId: string) => Promise<void>
  /** Stop recording function (REQUIRED) */
  stopRecording: () => void
  /** Whether recording can start (REQUIRED) */
  canRecord: boolean
}

/**
 * VoiceOverlay Component
 *
 * Header overlay containing voice control elements:
 * - Voice feedback notification button with unread badge
 * - Connection status indicator (green=connected, yellow=disconnected)
 * - Voice input toggle for speech-to-text
 * - Voice output toggle for text-to-speech
 */
export function VoiceOverlay({
  unreadCount,
  isFeedbackConnected,
  selectedTeam,
  selectedRole,
  onTogglePanel,
  onTranscriptChange,
  voiceState,
  isRecording,
  startRecording,
  stopRecording,
  canRecord,
}: VoiceOverlayProps) {
  return (
    <div className="flex items-center gap-1 sm:gap-2">
      {/* Recording Target Indicator - shows where voice commands go */}
      {isRecording && selectedTeam && selectedRole && (
        <div
          data-testid="recording-target-indicator"
          aria-label={`Recording to ${selectedTeam} / ${selectedRole}`}
          className="flex items-center gap-1.5 px-2 py-1 bg-red-500/10 border border-red-500/30 rounded-md animate-pulse"
        >
          <Radio className="h-3 w-3 text-red-500" />
          <span className="text-xs font-medium text-red-600 dark:text-red-400 max-w-[120px] truncate">
            {selectedTeam}
          </span>
          <span className="text-xs text-muted-foreground">/</span>
          <span className="text-xs font-bold text-red-600 dark:text-red-400">
            {selectedRole}
          </span>
        </div>
      )}

      {/* Voice Feedback Notification Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={onTogglePanel}
        className="relative h-8 w-8 sm:h-9 sm:w-9"
        aria-label={`Voice notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
      >
        <MessageSquare className="h-4 w-4" />

        {/* Unread Count Badge */}
        {unreadCount > 0 && (
          <Badge
            variant="destructive"
            className="absolute -top-1 -right-1 h-4 min-w-4 px-1 flex items-center justify-center text-[10px] font-bold"
          >
            {unreadCount > 99 ? "99+" : unreadCount}
          </Badge>
        )}

        {/* Connection Status Indicator */}
        <span
          className={cn(
            "absolute bottom-0 right-0 h-2 w-2 rounded-full border border-background",
            isFeedbackConnected ? "bg-green-500" : "bg-yellow-500 animate-pulse"
          )}
        />
      </Button>

      {/* Voice Input Toggle */}
      <VoiceInputToggle
        teamId={selectedTeam}
        roleId={selectedRole}
        onTranscriptChange={onTranscriptChange}
        voiceState={voiceState}
        isRecording={isRecording}
        startRecording={startRecording}
        stopRecording={stopRecording}
        canRecord={canRecord}
      />

      {/* Voice Output Toggle */}
      <VoiceOutputToggle />
    </div>
  )
}
