"use client"

import {
  createContext,
  useContext,
  useState,
  useRef,
  useCallback,
  useEffect,
  useMemo,
  type ReactNode,
} from "react"
import { toast } from "@/hooks/use-toast"
import {
  type VoiceFeedbackMode,
  getVoiceFeedbackMode,
  setVoiceFeedbackMode as saveVoiceFeedbackMode,
} from "@/lib/voice-types"
import { getWebSocketBaseUrl } from "@/lib/websocket-utils"
import { VOICE_CONSTANTS } from "@/lib/voice-constants"

const { MAX_NOTIFICATIONS, NOTIFICATION_EXPIRY_MS, DEDUP_WINDOW_MS, MAX_AGE_FOR_AUTOPLAY_MS } = VOICE_CONSTANTS

// Keepalive ping interval (30 seconds) - prevents Cloudflare/proxy timeouts
const PING_INTERVAL_MS = 30000

// ============================================
// Types
// ============================================

export interface VoiceNotification {
  id: string
  timestamp: number
  summary: string
  teamId: string
  roleId: string
  audioBase64: string
  isPlayed: boolean
  isRead: boolean
}

interface VoiceFeedbackContextValue {
  notifications: VoiceNotification[]
  unreadCount: number
  isPanelOpen: boolean
  isConnected: boolean
  isHandsFreeMode: boolean
  voiceFeedbackMode: VoiceFeedbackMode
  setHandsFreeMode: (enabled: boolean) => void
  setVoiceFeedbackMode: (mode: VoiceFeedbackMode) => void
  connectWebSocket: () => void
  disconnectWebSocket: () => void
  togglePanel: () => void
  openPanel: () => void
  closePanel: () => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  playNotification: (id: string) => void
  clearAll: () => void
}

// ============================================
// WebSocket Message Types
// ============================================

interface VoiceFeedbackMessage {
  type: "voice_feedback"
  summary: string
  audio: string // base64 MP3 of full summary
  team_id?: string
  role_id?: string
  timestamp?: number
  team_name_formatted?: string  // NEW (optional) - formatted team name for display
  team_name_audio?: string      // NEW (optional) - base64 MP3 of team name
}

interface VoiceErrorMessage {
  type: "error"
  message: string
}

type WebSocketMessage = VoiceFeedbackMessage | VoiceErrorMessage

// ============================================
// Context
// ============================================

const VoiceFeedbackContext = createContext<VoiceFeedbackContextValue | null>(null)

// ============================================
// Provider Component
// ============================================

interface VoiceFeedbackProviderProps {
  children: ReactNode
}

export function VoiceFeedbackProvider({ children }: VoiceFeedbackProviderProps) {
  // State
  const [notifications, setNotifications] = useState<VoiceNotification[]>([])
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isHandsFreeMode, setIsHandsFreeMode] = useState(false)
  const [voiceFeedbackMode, setVoiceFeedbackModeState] = useState<VoiceFeedbackMode>(() => getVoiceFeedbackMode())

  // Refs
  const wsRef = useRef<WebSocket | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const dedupMapRef = useRef<Map<string, number>>(new Map())
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const voiceFeedbackModeRef = useRef<VoiceFeedbackMode>(voiceFeedbackMode)
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // ============================================
  // Deduplication Logic
  // ============================================

  const generateHash = useCallback((msg: VoiceFeedbackMessage): string => {
    const audioLen = msg.audio?.length || 0
    const audioStart = msg.audio?.substring(0, 50) || ""
    const audioEnd = msg.audio?.substring(Math.max(0, audioLen - 50)) || ""
    return `${msg.summary}|${audioLen}|${audioStart}|${audioEnd}`
  }, [])

  const isDuplicate = useCallback((hash: string): boolean => {
    const now = Date.now()
    const lastSeen = dedupMapRef.current.get(hash)

    // Clean old entries
    for (const [key, timestamp] of dedupMapRef.current.entries()) {
      if (now - timestamp > DEDUP_WINDOW_MS) {
        dedupMapRef.current.delete(key)
      }
    }

    if (lastSeen && now - lastSeen < DEDUP_WINDOW_MS) {
      return true
    }

    dedupMapRef.current.set(hash, now)
    return false
  }, [])

  // ============================================
  // Audio Playback
  // ============================================

  // Play notification tone using actual cat meow audio file
  // Distinctly different from 880Hz acknowledgment beep
  const playTone = useCallback(() => {
    try {
      // Play cat meow audio file
      const audio = new Audio('/sounds/meow.mp3')
      audio.volume = 0.5  // 50% volume (not too loud)

      audio.play().catch((error) => {
        console.error("[VoiceFeedback] Meow playback error:", error)
      })

      console.log("[VoiceFeedback] Playing cat meow notification")
    } catch (error) {
      console.error("[VoiceFeedback] Tone playback error:", error)
    }
  }, [])

  const playAudio = useCallback((base64Audio: string, notificationId: string) => {
    console.log(`[VoiceFeedback] playAudio() CALLED - notificationId: ${notificationId}, audioLength: ${base64Audio?.length || 0}`)

    // Global lock to prevent multiple tabs playing
    if ((window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__) {
      console.log("[VoiceFeedback] Another tab is playing, skipping")
      return
    }

    if (!base64Audio || base64Audio.length === 0) {
      console.error("[VoiceFeedback] ❌ No audio data provided (empty or null)")
      return
    }

    try {
      // Stop any currently playing audio
      if (audioRef.current) {
        console.log("[VoiceFeedback] Stopping currently playing audio")
        audioRef.current.pause()
        audioRef.current = null
      }

      console.log(`[VoiceFeedback] Decoding base64 audio (${base64Audio.length} chars)`)
      // Decode base64 to blob
      const binaryString = atob(base64Audio)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      const blob = new Blob([bytes], { type: "audio/mp3" })
      const audioUrl = URL.createObjectURL(blob)
      console.log(`[VoiceFeedback] Created blob: ${blob.size} bytes, URL: ${audioUrl}`)

      const audio = new Audio(audioUrl)
      audioRef.current = audio

      // Set global lock
      ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = true

      audio.onended = () => {
        console.log("[VoiceFeedback] ✅ Audio playback ENDED")
        URL.revokeObjectURL(audioUrl)
        audioRef.current = null
        ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = false

        // Mark as played
        setNotifications((prev) =>
          prev.map((n) => (n.id === notificationId ? { ...n, isPlayed: true } : n))
        )
      }

      audio.onerror = (e) => {
        console.error("[VoiceFeedback] ❌ Audio element ERROR:", e)
        URL.revokeObjectURL(audioUrl)
        audioRef.current = null
        ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = false
      }

      console.log("[VoiceFeedback] Calling audio.play()...")
      audio.play().then(() => {
        console.log("[VoiceFeedback] ✅ audio.play() promise RESOLVED - audio playing")
      }).catch((e) => {
        console.error("[VoiceFeedback] ❌ audio.play() promise REJECTED:", e.name, e.message)
        ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = false
      })

      console.log("[VoiceFeedback] Playing audio for notification:", notificationId)
    } catch (error) {
      console.error("[VoiceFeedback] ❌ Audio decode/setup error:", error)
      ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = false
    }
  }, [])

  // ============================================
  // WebSocket Message Handler
  // ============================================

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      // DEBUG: Log ALL incoming messages
      console.log("[VoiceFeedback] WebSocket message received, type:", typeof event.data, "length:", event.data?.length)

      // Handle plain text "pong" response from keepalive ping
      if (event.data === "pong") {
        console.log("[VoiceFeedback] Received keepalive pong")
        return
      }

      try {
        const data: WebSocketMessage = JSON.parse(event.data)
        console.log("[VoiceFeedback] Parsed message type:", data.type)

        if (data.type === "voice_feedback") {
          const msg = data as VoiceFeedbackMessage
          console.log("[VoiceFeedback] voice_feedback received - summary:", msg.summary, "audio_length:", msg.audio?.length || 0)

          // Check for duplicates
          const hash = generateHash(msg)
          if (isDuplicate(hash)) {
            console.log("[VoiceFeedback] Duplicate notification, skipping")
            return
          }

          // Create notification
          const notification: VoiceNotification = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            timestamp: msg.timestamp || Date.now(),
            summary: msg.summary,
            teamId: msg.team_id || "unknown",
            roleId: msg.role_id || "unknown",
            audioBase64: msg.audio,
            isPlayed: false,
            isRead: false,
          }

          // Add to state (memory pattern: forward immediately, don't capture)
          setNotifications((prev) => {
            const updated = [notification, ...prev]
            // Limit to MAX_NOTIFICATIONS
            if (updated.length > MAX_NOTIFICATIONS) {
              return updated.slice(0, MAX_NOTIFICATIONS)
            }
            return updated
          })

          // Auto-play feedback based on mode (read from ref to get latest value)
          const messageAge = Date.now() - notification.timestamp
          const currentMode = voiceFeedbackModeRef.current

          console.log(`[VoiceFeedback] Playback decision - mode: ${currentMode}, messageAge: ${Math.round(messageAge / 1000)}s, MAX_AGE: ${MAX_AGE_FOR_AUTOPLAY_MS / 1000}s`)

          if (currentMode === "off") {
            console.log("[VoiceFeedback] Skipping audio - feedback mode is OFF")
          } else if (currentMode === "tone") {
            // Tone mode: Always play tone (regardless of hands-free mode)
            console.log("[VoiceFeedback] Playing tone (mode: tone)")
            playTone()
          } else if (currentMode === "team_name") {
            // Team Name mode: Play team name audio if available (no hands-free requirement)
            if (msg.team_name_audio) {
              if (messageAge <= MAX_AGE_FOR_AUTOPLAY_MS) {
                console.log(`[VoiceFeedback] Playing team name audio (${msg.team_name_audio?.length || 0} bytes)`)
                playAudio(msg.team_name_audio, notification.id)
              } else {
                console.log(`[VoiceFeedback] Skipping stale team name - age: ${Math.round(messageAge / 1000)}s > ${MAX_AGE_FOR_AUTOPLAY_MS / 1000}s`)
              }
            } else {
              console.log("[VoiceFeedback] team_name_audio not available, skipping")
            }
          } else if (currentMode === "voice") {
            // Voice mode: Always play full summary audio (input and output are independent)
            console.log(`[VoiceFeedback] Mode is VOICE - checking age (${Math.round(messageAge / 1000)}s vs ${MAX_AGE_FOR_AUTOPLAY_MS / 1000}s)`)
            if (messageAge <= MAX_AGE_FOR_AUTOPLAY_MS) {
              console.log(`[VoiceFeedback] ✅ Calling playAudio() with ${msg.audio?.length || 0} bytes`)
              playAudio(msg.audio, notification.id)
            } else {
              console.log(`[VoiceFeedback] ❌ Skipping stale audio - age: ${Math.round(messageAge / 1000)}s > ${MAX_AGE_FOR_AUTOPLAY_MS / 1000}s`)
            }
          } else {
            console.log(`[VoiceFeedback] ⚠️ UNKNOWN MODE: ${currentMode}`)
          }

          // Toast notification removed per user request
          // Voice feedback only shows in notification center, not as toast popup
          // toast({
          //   title: "Voice Feedback",
          //   description: `${notification.teamId}/${notification.roleId}: ${notification.summary.slice(0, 100)}${notification.summary.length > 100 ? "..." : ""}`,
          // })

          console.log("[VoiceFeedback] New notification:", notification.summary)
        } else if (data.type === "error") {
          console.error("[VoiceFeedback] WebSocket error:", data.message)
        }
      } catch (error) {
        console.error("[VoiceFeedback] Message parse error:", error)
      }
    },
    [generateHash, isDuplicate, playAudio, playTone]
  )

  // ============================================
  // WebSocket Keepalive (prevents Cloudflare/proxy timeouts)
  // ============================================

  const stopPingInterval = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
      pingIntervalRef.current = null
      console.log("[VoiceFeedback] Stopped keepalive ping interval")
    }
  }, [])

  const startPingInterval = useCallback(() => {
    stopPingInterval() // Clear any existing interval
    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send("ping")
          console.log("[VoiceFeedback] Keepalive ping sent")
        } catch (error) {
          console.error("[VoiceFeedback] Failed to send ping:", error)
        }
      }
    }, PING_INTERVAL_MS)
    console.log(`[VoiceFeedback] Started keepalive ping interval (${PING_INTERVAL_MS / 1000}s)`)
  }, [stopPingInterval])

  // ============================================
  // WebSocket Connection Management
  // ============================================

  const connectWebSocket = useCallback(() => {
    // Already connected or connecting
    if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
      return
    }

    // WebSocket must connect directly to backend (Next.js rewrites don't support WS)
    const wsUrl = `${getWebSocketBaseUrl()}/api/voice/ws/feedback/global`

    console.log("[VoiceFeedback] Connecting to:", wsUrl)

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log("[VoiceFeedback] WebSocket connected")
      setIsConnected(true)
      // Start keepalive ping interval (prevents Cloudflare/proxy timeouts)
      startPingInterval()
    }

    ws.onmessage = handleMessage

    ws.onerror = (error) => {
      console.error("[VoiceFeedback] WebSocket error:", error)
    }

    ws.onclose = (event) => {
      console.log("[VoiceFeedback] WebSocket closed:", event.code, event.reason)
      setIsConnected(false)
      wsRef.current = null
      // Stop keepalive ping interval
      stopPingInterval()

      // Auto-reconnect after 5 seconds
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log("[VoiceFeedback] Auto-reconnecting...")
        connectWebSocket()
      }, 5000)
    }

    wsRef.current = ws
  }, [handleMessage, startPingInterval, stopPingInterval])

  const disconnectWebSocket = useCallback(() => {
    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    // Stop keepalive ping interval
    stopPingInterval()

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [stopPingInterval])

  // ============================================
  // Panel Actions
  // ============================================

  const togglePanel = useCallback(() => {
    setIsPanelOpen((prev) => !prev)
  }, [])

  const openPanel = useCallback(() => {
    setIsPanelOpen(true)
  }, [])

  const closePanel = useCallback(() => {
    setIsPanelOpen(false)
  }, [])

  // ============================================
  // Notification Actions
  // ============================================

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))
    )
  }, [])

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })))
  }, [])

  const playNotification = useCallback(
    (id: string) => {
      const notification = notifications.find((n) => n.id === id)
      if (notification) {
        playAudio(notification.audioBase64, id)
      }
    },
    [notifications, playAudio]
  )

  const clearAll = useCallback(() => {
    setNotifications([])
    dedupMapRef.current.clear()
  }, [])

  // Wrapper to update hands-free mode state
  const handleSetHandsFreeMode = useCallback((enabled: boolean) => {
    setIsHandsFreeMode(enabled)
    console.log("[VoiceFeedback] Hands-free mode:", enabled ? "ON" : "OFF")
  }, [])

  // Wrapper to update voice feedback mode state
  const handleSetVoiceFeedbackMode = useCallback((mode: VoiceFeedbackMode) => {
    setVoiceFeedbackModeState(mode)
    saveVoiceFeedbackMode(mode)  // Save to localStorage

    // If switching to OFF mode, stop any currently playing audio immediately
    if (mode === "off" && audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
      ;(window as unknown as { __voiceFeedbackPlaying__?: boolean }).__voiceFeedbackPlaying__ = false
    }

    console.log("[VoiceFeedback] Feedback mode:", mode.toUpperCase())
  }, [])

  // ============================================
  // Computed Values
  // ============================================

  const unreadCount = useMemo(
    () => notifications.filter((n) => !n.isRead).length,
    [notifications]
  )

  // ============================================
  // Effects
  // ============================================

  // Auto-connect on mount
  useEffect(() => {
    connectWebSocket()
    return () => {
      disconnectWebSocket()
    }
  }, [connectWebSocket, disconnectWebSocket])

  // Visibility change handler - reconnect WebSocket when tab becomes visible
  // Handles browser tab suspension (mobile browsers, background tabs)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        console.log("[VoiceFeedback] Tab became visible, checking WebSocket...")
        // Check if WebSocket is dead or disconnected
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          console.log("[VoiceFeedback] WebSocket not connected, reconnecting...")
          connectWebSocket()
        } else {
          console.log("[VoiceFeedback] WebSocket still connected")
        }
      }
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange)
    }
  }, [connectWebSocket])

  // Sync voiceFeedbackModeRef when state changes (fixes stale closure in WebSocket handler)
  useEffect(() => {
    voiceFeedbackModeRef.current = voiceFeedbackMode
  }, [voiceFeedbackMode])

  // Auto-expire old notifications
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now()
      setNotifications((prev) =>
        prev.filter((n) => now - n.timestamp < NOTIFICATION_EXPIRY_MS)
      )
    }, 60 * 1000) // Check every minute

    return () => clearInterval(interval)
  }, [])

  // ============================================
  // Context Value
  // ============================================

  const contextValue: VoiceFeedbackContextValue = useMemo(
    () => ({
      notifications,
      unreadCount,
      isPanelOpen,
      isConnected,
      isHandsFreeMode,
      voiceFeedbackMode,
      setHandsFreeMode: handleSetHandsFreeMode,
      setVoiceFeedbackMode: handleSetVoiceFeedbackMode,
      connectWebSocket,
      disconnectWebSocket,
      togglePanel,
      openPanel,
      closePanel,
      markAsRead,
      markAllAsRead,
      playNotification,
      clearAll,
    }),
    [
      notifications,
      unreadCount,
      isPanelOpen,
      isConnected,
      isHandsFreeMode,
      voiceFeedbackMode,
      handleSetHandsFreeMode,
      handleSetVoiceFeedbackMode,
      connectWebSocket,
      disconnectWebSocket,
      togglePanel,
      openPanel,
      closePanel,
      markAsRead,
      markAllAsRead,
      playNotification,
      clearAll,
    ]
  )

  return (
    <VoiceFeedbackContext.Provider value={contextValue}>
      {children}
    </VoiceFeedbackContext.Provider>
  )
}

// ============================================
// Hook
// ============================================

export function useVoiceFeedback(): VoiceFeedbackContextValue {
  const context = useContext(VoiceFeedbackContext)
  if (!context) {
    throw new Error("useVoiceFeedback must be used within VoiceFeedbackProvider")
  }
  return context
}

export default VoiceFeedbackContext
