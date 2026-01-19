/**
 * Voice Integration TypeScript Types
 *
 * Types for Soniox STT, microphone capture, and voice command flow.
 */

// ============================================
// Voice Command Types (Frontend State)
// ============================================

export type VoiceStatus =
  | "idle"           // Not recording
  | "connecting"     // Getting token / connecting WebSocket
  | "listening"      // Recording and streaming audio
  | "processing"     // Stop word detected, sending to backend
  | "correcting"     // Backend LLM correction in progress
  | "sent"           // Command sent to tmux
  | "speaking"       // Playing voice feedback audio
  | "error"          // Error state

export interface VoiceState {
  status: VoiceStatus
  transcript: string           // Accumulated transcript
  correctedCommand: string     // LLM-corrected command
  error: string | null
  isSpeaking: boolean          // VAD detected speech
  feedbackSummary: string      // Voice feedback summary text
  isPlayingFeedback: boolean   // Currently playing feedback audio
}

// ============================================
// Voice Command API Types (Backend Calls)
// ============================================

// Request to POST /api/voice/command/{team_id}/{role_id}
export interface VoiceCommandRequest {
  raw_command: string    // Full transcript including stop word
  transcript: string     // Command text (stop word removed)
  speed?: number         // Speech speed (0.5-2.0) for TTS feedback
}

// Streaming response from voice command endpoint
export interface LLMTokenMessage {
  type: "llm_token"
  token: string
}

export interface CommandSentMessage {
  type: "command_sent"
  corrected_command: string
  routed_to_backlog?: boolean  // True if command was routed to BL (Backlog Organizer)
}

export type VoiceCommandStreamMessage = LLMTokenMessage | CommandSentMessage

// ============================================
// Voice Feedback Types (Stop Hook -> TTS)
// ============================================

export interface VoiceFeedbackMessage {
  type: "voice_feedback"
  summary: string
  audio: string  // base64 MP3
}

export interface VoiceErrorMessage {
  type: "error"
  message: string
}

export type VoiceFeedbackEvent = VoiceFeedbackMessage | VoiceErrorMessage

// ============================================
// Audio Configuration Constants
// ============================================

export const AUDIO_CONFIG = {
  sampleRate: 16000,        // Required by Soniox STT
  channelCount: 1,          // Mono
  format: "pcm16" as const,
  chunkSizeMs: 64,          // ~64ms chunks (1024/16000)
  chunkSizeSamples: 1024,   // Must be power of 2 for createScriptProcessor (256-16384)
} as const

// ============================================
// Noise Filter Configuration
// ============================================

// Noise filter levels with descriptive labels
// Maps to VAD threshold: higher threshold = more noise filtering (requires louder speech)
export type NoiseFilterLevel = "very-low" | "low" | "medium" | "high" | "very-high"

export const NOISE_FILTER_LABELS: Record<NoiseFilterLevel, string> = {
  "very-low": "Very Low",
  "low": "Low",
  "medium": "Medium",
  "high": "High",
  "very-high": "Very High",
}

// VAD threshold values for each noise filter level
// Lower = more sensitive (picks up quieter sounds)
// Higher = less sensitive (requires louder speech, filters more noise)
export const NOISE_FILTER_THRESHOLDS: Record<NoiseFilterLevel, number> = {
  "very-low": 0.5,   // Very sensitive - quiet environments
  "low": 0.65,       // Sensitive - home office
  "medium": 0.75,    // Balanced - default
  "high": 0.85,      // Less sensitive - noisy office
  "very-high": 0.95, // Least sensitive - very noisy environments
}

// Noise filter DB thresholds for SilenceDetector
// Maps noise filter level to dB threshold for silence detection
// Lower dB = more sensitive (detects quieter sounds as speech)
// Higher dB = less sensitive (requires louder speech)
export const NOISE_FILTER_DB_THRESHOLDS: Record<NoiseFilterLevel, number> = {
  "very-low": -50,   // Very sensitive - picks up everything
  "low": -45,        // Sensitive
  "medium": -40,     // Balanced (default)
  "high": -35,       // Less sensitive
  "very-high": -30,  // Least sensitive - only clear speech
}

// Noise filter level descriptions for UI
export const NOISE_FILTER_DESCRIPTIONS: Record<NoiseFilterLevel, string> = {
  "very-low": "Picks up everything - quiet environments only",
  "low": "Sensitive - good for home office",
  "medium": "Balanced - normal environments",
  "high": "Less sensitive - noisy office",
  "very-high": "Only clear speech - very noisy environments",
}

// Get noise filter DB threshold from localStorage setting
export const getNoiseFilterDbThreshold = (): number => {
  const level = getNoiseFilterLevel()
  return NOISE_FILTER_DB_THRESHOLDS[level]
}

export const DEFAULT_NOISE_FILTER: NoiseFilterLevel = "medium"
export const NOISE_FILTER_STORAGE_KEY = "voice-noise-filter"

// Get noise filter level from localStorage
export const getNoiseFilterLevel = (): NoiseFilterLevel => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem(NOISE_FILTER_STORAGE_KEY)
    if (stored && stored in NOISE_FILTER_THRESHOLDS) {
      return stored as NoiseFilterLevel
    }
  }
  return DEFAULT_NOISE_FILTER
}

// Set noise filter level to localStorage
export const setNoiseFilterLevel = (level: NoiseFilterLevel): void => {
  if (typeof window !== "undefined") {
    localStorage.setItem(NOISE_FILTER_STORAGE_KEY, level)
  }
}

// VAD threshold: 0.0-1.0 scale where higher = less sensitive (requires louder speech)
// Reads from localStorage noise filter setting, falls back to env var or default
const getVadThreshold = (): number => {
  if (typeof window !== "undefined") {
    // First check localStorage for noise filter setting
    const noiseFilter = getNoiseFilterLevel()
    return NOISE_FILTER_THRESHOLDS[noiseFilter]
  }
  // Fallback for SSR
  const envThreshold = process.env.NEXT_PUBLIC_VOICE_VAD_THRESHOLD
  if (envThreshold) {
    const parsed = parseFloat(envThreshold)
    if (!isNaN(parsed) && parsed >= 0 && parsed <= 1) {
      return parsed
    }
  }
  return NOISE_FILTER_THRESHOLDS[DEFAULT_NOISE_FILTER]
}

export const VAD_CONFIG = {
  type: "server_vad" as const,
  threshold: getVadThreshold(),
  prefixPaddingMs: 300,
  silenceDurationMs: 800,
} as const

// Get current VAD threshold (for dynamic use)
export const getCurrentVadThreshold = (): number => {
  return NOISE_FILTER_THRESHOLDS[getNoiseFilterLevel()]
}

// ============================================
// Detection Mode Configuration
// ============================================

// Only stopword detection mode is supported
export type DetectionMode = "stopword"

export const DETECTION_MODE_LABELS: Record<DetectionMode, string> = {
  stopword: "Stop Word",
}

export const DEFAULT_DETECTION_MODE: DetectionMode = "stopword"
export const STOP_WORD_STORAGE_KEY = "voice-stop-word"
export const DEFAULT_STOP_WORD = "thank you"

// Get stop word from localStorage
export const getStopWord = (): string => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem(STOP_WORD_STORAGE_KEY)
    if (stored) {
      return stored
    }
  }
  return DEFAULT_STOP_WORD
}

// Set stop word to localStorage
export const setStopWordSetting = (stopWord: string): void => {
  if (typeof window !== "undefined") {
    localStorage.setItem(STOP_WORD_STORAGE_KEY, stopWord)
  }
}

// ============================================
// Voice Feedback Mode Configuration
// ============================================

// Voice feedback playback modes
export type VoiceFeedbackMode = "voice" | "off" | "tone" | "team_name"

export const VOICE_FEEDBACK_MODE_LABELS: Record<VoiceFeedbackMode, string> = {
  voice: "Voice",
  off: "Off",
  tone: "Tone",
  team_name: "Team",
}

export const VOICE_FEEDBACK_MODE_DESCRIPTIONS: Record<VoiceFeedbackMode, string> = {
  voice: "Play full voice feedback (hands-free)",
  off: "No audio (silent)",
  tone: "Short notification tone only",
  team_name: "Speak team name only",
}

export const DEFAULT_VOICE_FEEDBACK_MODE: VoiceFeedbackMode = "voice"
export const VOICE_FEEDBACK_MODE_STORAGE_KEY = "voice-feedback-mode"

// Get voice feedback mode from localStorage
export const getVoiceFeedbackMode = (): VoiceFeedbackMode => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem(VOICE_FEEDBACK_MODE_STORAGE_KEY)
    if (stored && (stored === "voice" || stored === "off" || stored === "tone" || stored === "team_name")) {
      return stored as VoiceFeedbackMode
    }
  }
  return DEFAULT_VOICE_FEEDBACK_MODE
}

// Set voice feedback mode to localStorage
export const setVoiceFeedbackMode = (mode: VoiceFeedbackMode): void => {
  if (typeof window !== "undefined") {
    localStorage.setItem(VOICE_FEEDBACK_MODE_STORAGE_KEY, mode)
  }
}

// ============================================
// Speech Speed Configuration (HD-TTS)
// ============================================

export const MIN_SPEECH_SPEED = 0.5
export const MAX_SPEECH_SPEED = 2.0
export const SPEECH_SPEED_STORAGE_KEY = "speech-speed"

// Get speech speed from localStorage
// Returns null if user hasn't set a speed (backend will use default)
export const getSpeechSpeed = (): number | null => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem(SPEECH_SPEED_STORAGE_KEY)
    if (stored) {
      const speed = parseFloat(stored)
      if (!isNaN(speed) && speed >= MIN_SPEECH_SPEED && speed <= MAX_SPEECH_SPEED) {
        return speed
      }
    }
  }
  return null  // No user setting - let backend use default (1.0)
}

// Set speech speed to localStorage
export const setSpeechSpeed = (speed: number): void => {
  if (typeof window !== "undefined") {
    // Validate range
    const validSpeed = Math.max(MIN_SPEECH_SPEED, Math.min(MAX_SPEECH_SPEED, speed))
    localStorage.setItem(SPEECH_SPEED_STORAGE_KEY, validSpeed.toString())
  }
}

// ============================================
// Hook Return Types
// ============================================

export interface UseVoiceRecorderReturn {
  // State
  state: VoiceState
  isRecording: boolean

  // Actions
  startRecording: (teamId: string, roleId: string) => Promise<void>
  stopRecording: () => void
  clearTranscript: () => void  // Clear transcript without stopping recording

  // Computed
  canRecord: boolean
  canClear: boolean  // Show clear button when transcript exists and not processing
}
