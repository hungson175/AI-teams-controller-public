"use client"

import { useState, useRef, useCallback, useEffect } from "react"
import {
  VoiceState,
  VoiceCommandRequest,
  UseVoiceRecorderReturn,
  getStopWord,
  CommandSentMessage,
  getSpeechSpeed,
} from "@/lib/voice-types"
import { SonioxSTTService } from "@/lib/stt"
import { getToken } from "@/lib/auth"
import { VOICE_CONSTANTS } from "@/lib/voice-constants"
import { toast } from "@/hooks/use-toast"
import { useAudioManager } from "@/hooks/useAudioManager"
import { useWakeLockManager } from "@/hooks/useWakeLockManager"

/**
 * Custom hook for HANDS-FREE voice recording with Soniox STT integration.
 *
 * HANDS-FREE MODE:
 * - Click mic once to START - stays listening continuously
 * - Speak naturally, then say "thank you" (stop word) → command auto-sends
 * - After sending, returns to listening for next command
 * - Click mic again to STOP hands-free mode
 *
 * Flow:
 * 1. Connect to Soniox WebSocket API
 * 2. Capture microphone audio (16kHz, mono, PCM16)
 * 3. Stream audio to Soniox, receive transcriptions
 * 4. Detect stop word to finalize command
 * 5. Send command to backend for LLM correction
 * 6. Return to listening state (hands-free continues)
 */
export function useVoiceRecorder(): UseVoiceRecorderReturn {
  // State
  const [state, setState] = useState<VoiceState>({
    status: "idle",
    transcript: "",
    correctedCommand: "",
    error: null,
    isSpeaking: false,
    feedbackSummary: "",
    isPlayingFeedback: false,
  })

  // Separate hands-free tracking - not tied to status changes
  const [isHandsFree, setIsHandsFree] = useState<boolean>(false)
  // Ref to access isHandsFree in callbacks without stale closure
  const isHandsFreeRef = useRef<boolean>(false)

  // Extracted hooks
  const { playBeep } = useAudioManager()
  const { requestWakeLock, releaseWakeLock } = useWakeLockManager({ isActive: isHandsFree })

  // Soniox service ref
  const sonioxRef = useRef<SonioxSTTService | null>(null)

  // Reconnection state with exponential backoff
  const reconnectAttemptsRef = useRef<number>(0)
  const MAX_RECONNECT_ATTEMPTS = 5
  const BASE_RECONNECT_DELAY_MS = 1000  // Start at 1 second
  const MAX_RECONNECT_DELAY_MS = 30000  // Cap at 30 seconds

  // Target team/role for command sending
  const targetRef = useRef<{ teamId: string; roleId: string } | null>(null)

  // Debounce: track last sent command and timestamp to prevent duplicates
  const lastSentRef = useRef<{ command: string; timestamp: number } | null>(null)
  const isSendingRef = useRef<boolean>(false)  // Mutex to prevent concurrent sends
  const DEBOUNCE_MS = VOICE_CONSTANTS.DEBOUNCE_MS  // Ignore duplicate commands within debounce window

  // Transition mutex: prevents race conditions during start/stop operations
  const isTransitioningRef = useRef<boolean>(false)
  // Pending stop: queues stop request when mutex blocks stopRecording
  const pendingStopRef = useRef<boolean>(false)

  /**
   * Update state helper - merges partial state
   */
  const updateState = useCallback((partial: Partial<VoiceState>) => {
    setState((prev) => ({ ...prev, ...partial }))
  }, [])

  // Keep isHandsFreeRef in sync with isHandsFree state (fixes stale closure in callbacks)
  useEffect(() => {
    isHandsFreeRef.current = isHandsFree
  }, [isHandsFree])

  /**
   * Internal stop recording (cleanup resources)
   */
  const stopRecordingInternal = useCallback(() => {
    if (sonioxRef.current) {
      sonioxRef.current.disconnect()
      sonioxRef.current = null
    }
  }, [])

  /**
   * Send command to backend for LLM correction
   */
  const sendCommand = useCallback(async (rawCommand: string, command: string) => {
    if (!targetRef.current) return

    const { teamId, roleId } = targetRef.current
    updateState({ status: "correcting" })

    try {
      const userSpeed = getSpeechSpeed()

      // Build request - only include speed if user has set it
      // If user hasn't set speed, backend will use its default (1.0)
      const request: VoiceCommandRequest = {
        raw_command: rawCommand,
        transcript: command,
        ...(userSpeed !== null && { speed: userSpeed }), // Conditionally include speed
      }

      // 30 second timeout for streaming fetch
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000)

      const response = await fetch(
        `/api/voice/command/${teamId}/${roleId}`,
        {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${getToken()}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(request),
          signal: controller.signal,
        }
      )

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`)
      }

      // Play acknowledgment beep immediately when backend receives command
      playBeep()

      // Handle streaming response
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let correctedCommand = ""

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          // Parse NDJSON lines
          const lines = chunk.split("\n").filter((line) => line.trim())

          for (const line of lines) {
            try {
              const msg = JSON.parse(line)
              if (msg.type === "llm_token") {
                correctedCommand += msg.token
                updateState({ correctedCommand })
              } else if (msg.type === "command_sent") {
                const sentMsg = msg as CommandSentMessage
                correctedCommand = sentMsg.corrected_command
                updateState({
                  status: "sent",
                  correctedCommand,
                })

                // Show toast notification when command is routed to Backlog Organizer
                if (sentMsg.routed_to_backlog) {
                  toast({
                    title: "Routed to Backlog Organizer",
                    description: "Your command was sent to BL for backlog management.",
                  })
                }
              }
            } catch {
              // Skip non-JSON lines
            }
          }
        }
      }

      // Return to listening state after short delay (hands-free mode continues)
      setTimeout(() => {
        // Reset sending mutex
        isSendingRef.current = false
        // Only return to listening if still in hands-free mode
        // Use ref to avoid stale closure
        if (isHandsFreeRef.current && sonioxRef.current?.connected) {
          updateState({
            status: "listening",
            correctedCommand: "",
          })
        } else {
          updateState({
            status: "idle",
            correctedCommand: "",
          })
        }
      }, 2000)
    } catch (error) {
      console.error("[Voice] Command send error:", error)
      // Reset sending mutex on error
      isSendingRef.current = false
      updateState({
        status: "error",
        error: error instanceof Error ? error.message : "Failed to send command",
      })
    }
  }, [updateState, playBeep])  // isHandsFree removed - using ref now

  /**
   * Handle command finalization from Soniox
   */
  const handleFinalize = useCallback((command: string) => {
    if (!command.trim()) return

    // Mutex: prevent concurrent sends
    if (isSendingRef.current) {
      console.log("[Voice] Already sending, skipping")
      return
    }

    // Debounce: check if same/similar command was sent recently
    const now = Date.now()
    if (lastSentRef.current) {
      const timeSinceLast = now - lastSentRef.current.timestamp
      if (timeSinceLast < DEBOUNCE_MS) {
        console.log("[Voice] Debounced - command sent", timeSinceLast, "ms ago")
        return
      }
    }

    console.log("[Voice] Finalizing command:", command)
    // Set mutex and track this command
    isSendingRef.current = true
    lastSentRef.current = { command, timestamp: now }
    updateState({ status: "processing", transcript: "" })
    // Send command but DON'T stop recording - hands-free mode!
    sendCommand(command, command)
  }, [updateState, sendCommand])

  /**
   * Start recording - main entry point
   */
  const startRecording = useCallback(async (teamId: string, roleId: string) => {
    // Mutex guard: prevent race conditions during transitions
    if (isTransitioningRef.current) {
      console.log("[Voice] Transition in progress, skipping startRecording")
      return
    }
    isTransitioningRef.current = true

    try {
      // Store target for command sending
      targetRef.current = { teamId, roleId }

      // Reset reconnection attempts on manual start
      reconnectAttemptsRef.current = 0

      // Reset state
      updateState({
        status: "connecting",
        transcript: "",
        correctedCommand: "",
        error: null,
        isSpeaking: false,
        feedbackSummary: "",
        isPlayingFeedback: false,
      })

      // Enable hands-free mode
      setIsHandsFree(true)

      // Request wake lock to keep screen on (mobile)
      await requestWakeLock()

      // Read stop word from localStorage
      const stopWord = getStopWord()

      console.log(`[Voice] Starting with mode: stopword, stop word: "${stopWord}"`)

      // Create Soniox service with settings
      const soniox = new SonioxSTTService(
        {
          detectionMode: "stopword",
          stopWord,
        },
        {
          onTranscript: (transcript, isFinal) => {
            updateState({ transcript, isSpeaking: !isFinal })
          },
          onFinalize: handleFinalize,
          onConnectionChange: (connected) => {
            if (connected) {
              updateState({ status: "listening" })
              // Reset reconnection attempts on successful connection
              reconnectAttemptsRef.current = 0
              // Clear transition mutex - connection established
              isTransitioningRef.current = false
              // Check for pending stop (queued while transition was in progress)
              if (pendingStopRef.current) {
                console.log("[Voice] Executing pending stop")
                pendingStopRef.current = false
                // Execute stop inline (can't call stopRecording - not yet defined)
                setIsHandsFree(false)
                stopRecordingInternal()
                releaseWakeLock()
                updateState({ status: "idle", isSpeaking: false })
              }
            } else if (isHandsFreeRef.current) {
              // Disconnected while hands-free - try to reconnect with exponential backoff
              // Use ref instead of state to avoid stale closure
              reconnectAttemptsRef.current += 1
              const attempts = reconnectAttemptsRef.current

              if (attempts > MAX_RECONNECT_ATTEMPTS) {
                console.error(`[Voice] Max reconnection attempts (${MAX_RECONNECT_ATTEMPTS}) exceeded. Giving up.`)
                updateState({
                  status: "error",
                  error: `Connection lost. Failed to reconnect after ${MAX_RECONNECT_ATTEMPTS} attempts.`,
                })
                setIsHandsFree(false)
                return
              }

              // Exponential backoff: 1s, 2s, 4s, 8s, 16s, capped at 30s
              const delay = Math.min(
                BASE_RECONNECT_DELAY_MS * Math.pow(2, attempts - 1),
                MAX_RECONNECT_DELAY_MS
              )
              console.log(`[Voice] Disconnected. Reconnect attempt ${attempts}/${MAX_RECONNECT_ATTEMPTS} in ${delay}ms...`)

              setTimeout(() => {
                // Check ref again in case user stopped recording during delay
                if (isHandsFreeRef.current && targetRef.current) {
                  startRecording(targetRef.current.teamId, targetRef.current.roleId)
                }
              }, delay)
            }
          },
          onError: (error) => {
            console.error("[Voice] Soniox error:", error)
            updateState({
              status: "error",
              error: error.message,
            })
          },
          onAudioLevel: (levelDb) => {
            // Could be used for UI feedback (audio meter)
          },
        }
      )

      sonioxRef.current = soniox

      // Connect to Soniox
      console.log("[Voice] Connecting to Soniox...")
      await soniox.connect()

      console.log("[Voice] Recording started with Soniox")
    } catch (error) {
      console.error("[Voice] Start recording error:", error)
      // Clear transition mutex on error
      isTransitioningRef.current = false
      // Clear pending stop (error already stops recording)
      pendingStopRef.current = false
      stopRecordingInternal()
      setIsHandsFree(false)
      updateState({
        status: "error",
        error: error instanceof Error ? error.message : "Failed to start recording",
      })
    }
  }, [updateState, stopRecordingInternal, requestWakeLock, releaseWakeLock, handleFinalize])

  /**
   * Stop recording - user action
   */
  const stopRecording = useCallback(() => {
    // Mutex guard: prevent race conditions during transitions
    if (isTransitioningRef.current) {
      console.log("[Voice] Transition in progress, queueing stop")
      // Queue stop for after transition completes
      pendingStopRef.current = true
      return
    }
    isTransitioningRef.current = true

    try {
      setIsHandsFree(false)  // Disable hands-free mode
      stopRecordingInternal()
      releaseWakeLock()  // Release wake lock
      updateState({
        status: "idle",
        isSpeaking: false,
      })
    } finally {
      isTransitioningRef.current = false
    }
  }, [stopRecordingInternal, updateState, releaseWakeLock])

  /**
   * Clear transcript without stopping recording
   * Allows user to discard accidental recordings
   */
  const clearTranscript = useCallback(() => {
    // Reset transcript in Soniox service
    if (sonioxRef.current) {
      sonioxRef.current.resetTranscript()
    }

    // Reset local state
    updateState({
      transcript: "",
      correctedCommand: "",
    })

    // Haptic feedback (double-tap pattern)
    if ('vibrate' in navigator) {
      navigator.vibrate([50, 30, 50])
    }

    console.log("[Voice] Transcript cleared")
  }, [updateState])

  /**
   * Full cleanup - stops recording resources
   */
  const cleanup = useCallback(() => {
    setIsHandsFree(false)  // Disable hands-free mode
    stopRecordingInternal()
    releaseWakeLock()  // Release wake lock
  }, [stopRecordingInternal, releaseWakeLock])


  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup()
    }
  }, [cleanup])

  // Compute canClear: show clear button when transcript exists and not in processing states
  const canClear = state.transcript.length > 0 &&
    state.status !== "processing" &&
    state.status !== "correcting" &&
    state.status !== "sent"

  return {
    state,
    isRecording: isHandsFree,
    startRecording,
    stopRecording,
    clearTranscript,
    canRecord: state.status === "idle" || state.status === "error" || state.status === "speaking",
    canClear,
  }
}
