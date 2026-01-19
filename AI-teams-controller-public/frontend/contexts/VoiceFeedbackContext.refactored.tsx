"use client"

/**
 * VoiceFeedbackContext - Composed Provider (Sprint 6: SRP Refactoring)
 *
 * This is the refactored version that composes:
 * - VoiceWebSocketContext (WebSocket connection management)
 * - VoiceAudioContext (Audio playback management)
 *
 * Maintains the same external interface for backward compatibility.
 */

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
import { VoiceWebSocketProvider, useVoiceWebSocket } from "./VoiceWebSocketContext"
import { VoiceAudioProvider, useVoiceAudio } from "./VoiceAudioContext"
import { type VoiceFeedbackMode } from "@/lib/voice-types"
import { VOICE_CONSTANTS } from "@/lib/voice-constants"

const { MAX_NOTIFICATIONS, NOTIFICATION_EXPIRY_MS, DEDUP_WINDOW_MS, MAX_AGE_FOR_AUTOPLAY_MS } =
  VOICE_CONSTANTS

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

interface VoiceFeedbackMessage {
  type: "voice_feedback"
  summary: string
  audio: string
  team_id?: string
  role_id?: string
  timestamp?: number
  team_name_formatted?: string
  team_name_audio?: string
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
// Inner Provider (has access to both contexts)
// ============================================

function VoiceFeedbackInner({ children }: { children: ReactNode }) {
  // Get both contexts
  const wsContext = useVoiceWebSocket()
  const audioContext = useVoiceAudio()

  // Notification state
  const [notifications, setNotifications] = useState<VoiceNotification[]>([])
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const dedupMapRef = useRef<Map<string, number>>(new Map())

  // Deduplication
  const generateHash = useCallback((msg: VoiceFeedbackMessage): string => {
    const audioLen = msg.audio?.length || 0
    const audioStart = msg.audio?.substring(0, 50) || ""
    const audioEnd = msg.audio?.substring(Math.max(0, audioLen - 50)) || ""
    return `${msg.summary}|${audioLen}|${audioStart}|${audioEnd}`
  }, [])

  const isDuplicate = useCallback(
    (hash: string): boolean => {
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
    },
    []
  )

  // Handle WebSocket messages
  const handleMessage = useCallback(
    (data: unknown) => {
      const message = data as WebSocketMessage

      if (message.type === "voice_feedback") {
        const msg = message as VoiceFeedbackMessage

        // Check duplicates
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

        // Add to state
        setNotifications((prev) => {
          const updated = [notification, ...prev]
          if (updated.length > MAX_NOTIFICATIONS) {
            return updated.slice(0, MAX_NOTIFICATIONS)
          }
          return updated
        })

        // Auto-play based on mode
        const messageAge = Date.now() - notification.timestamp
        const currentMode = audioContext.voiceFeedbackMode

        if (currentMode === "off") {
          console.log("[VoiceFeedback] Skipping audio - mode OFF")
        } else if (currentMode === "tone") {
          audioContext.playTone()
        } else if (currentMode === "team_name" && msg.team_name_audio) {
          if (messageAge <= MAX_AGE_FOR_AUTOPLAY_MS) {
            audioContext.playAudio(msg.team_name_audio, notification.id)
          }
        } else if (currentMode === "voice") {
          if (messageAge <= MAX_AGE_FOR_AUTOPLAY_MS) {
            audioContext.playAudio(msg.audio, notification.id)
          }
        }
      } else if (message.type === "error") {
        console.error("[VoiceFeedback] WebSocket error:", message.message)
      }
    },
    [generateHash, isDuplicate, audioContext]
  )

  // Panel actions
  const togglePanel = useCallback(() => setIsPanelOpen((prev) => !prev), [])
  const openPanel = useCallback(() => setIsPanelOpen(true), [])
  const closePanel = useCallback(() => setIsPanelOpen(false), [])

  // Notification actions
  const markAsRead = useCallback(
    (id: string) => setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))),
    []
  )
  const markAllAsRead = useCallback(
    () => setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true }))),
    []
  )
  const playNotification = useCallback(
    (id: string) => {
      const notification = notifications.find((n) => n.id === id)
      if (notification) {
        audioContext.playAudio(notification.audioBase64, id)
      }
    },
    [notifications, audioContext]
  )
  const clearAll = useCallback(() => {
    setNotifications([])
    dedupMapRef.current.clear()
  }, [])

  // Computed
  const unreadCount = useMemo(() => notifications.filter((n) => !n.isRead).length, [notifications])

  // Auto-expire old notifications
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now()
      setNotifications((prev) => prev.filter((n) => now - n.timestamp < NOTIFICATION_EXPIRY_MS))
    }, 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  // Context value
  const contextValue: VoiceFeedbackContextValue = useMemo(
    () => ({
      notifications,
      unreadCount,
      isPanelOpen,
      isConnected: wsContext.isConnected,
      isHandsFreeMode: audioContext.isHandsFreeMode,
      voiceFeedbackMode: audioContext.voiceFeedbackMode,
      setHandsFreeMode: audioContext.setHandsFreeMode,
      setVoiceFeedbackMode: audioContext.setVoiceFeedbackMode,
      connectWebSocket: wsContext.connect,
      disconnectWebSocket: wsContext.disconnect,
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
      wsContext,
      audioContext,
      togglePanel,
      openPanel,
      closePanel,
      markAsRead,
      markAllAsRead,
      playNotification,
      clearAll,
    ]
  )

  return <VoiceFeedbackContext.Provider value={contextValue}>{children}</VoiceFeedbackContext.Provider>
}

// ============================================
// Outer Provider (composes contexts)
// ============================================

function VoiceFeedbackWithWebSocket({ children }: { children: ReactNode }) {
  // This component has access to both WebSocket and Audio contexts
  const wsContext = useVoiceWebSocket()
  const audioContext = useVoiceAudio()

  // Notification state
  const [notifications, setNotifications] = useState<VoiceNotification[]>([])
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const dedupMapRef = useRef<Map<string, number>>(new Map())

  // Deduplication
  const generateHash = useCallback((msg: VoiceFeedbackMessage): string => {
    const audioLen = msg.audio?.length || 0
    const audioStart = msg.audio?.substring(0, 50) || ""
    const audioEnd = msg.audio?.substring(Math.max(0, audioLen - 50)) || ""
    return `${msg.summary}|${audioLen}|${audioStart}|${audioEnd}`
  }, [])

  const isDuplicate = useCallback(
    (hash: string): boolean => {
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
    },
    []
  )

  // Handle WebSocket messages
  const handleMessage = useCallback(
    (data: unknown) => {
      const message = data as WebSocketMessage

      if (message.type === "voice_feedback") {
        const msg = message as VoiceFeedbackMessage

        // Check duplicates
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

        // Add to state
        setNotifications((prev) => {
          const updated = [notification, ...prev]
          if (updated.length > MAX_NOTIFICATIONS) {
            return updated.slice(0, MAX_NOTIFICATIONS)
          }
          return updated
        })

        // Auto-play based on mode
        const messageAge = Date.now() - notification.timestamp
        const currentMode = audioContext.voiceFeedbackMode

        if (currentMode === "off") {
          console.log("[VoiceFeedback] Skipping audio - mode OFF")
        } else if (currentMode === "tone") {
          audioContext.playTone()
        } else if (currentMode === "team_name" && msg.team_name_audio) {
          if (messageAge <= MAX_AGE_FOR_AUTOPLAY_MS) {
            audioContext.playAudio(msg.team_name_audio, notification.id)
          }
        } else if (currentMode === "voice") {
          if (messageAge <= MAX_AGE_FOR_AUTOPLAY_MS) {
            audioContext.playAudio(msg.audio, notification.id)
          }
        }
      } else if (message.type === "error") {
        console.error("[VoiceFeedback] WebSocket error:", message.message)
      }
    },
    [generateHash, isDuplicate, audioContext]
  )

  // Note: In real implementation, handleMessage would be passed to WebSocket provider
  // For now, we're just defining the structure

  // Panel actions
  const togglePanel = useCallback(() => setIsPanelOpen((prev) => !prev), [])
  const openPanel = useCallback(() => setIsPanelOpen(true), [])
  const closePanel = useCallback(() => setIsPanelOpen(false), [])

  // Notification actions
  const markAsRead = useCallback(
    (id: string) => setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))),
    []
  )
  const markAllAsRead = useCallback(
    () => setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true }))),
    []
  )
  const playNotification = useCallback(
    (id: string) => {
      const notification = notifications.find((n) => n.id === id)
      if (notification) {
        audioContext.playAudio(notification.audioBase64, id)
      }
    },
    [notifications, audioContext]
  )
  const clearAll = useCallback(() => {
    setNotifications([])
    dedupMapRef.current.clear()
  }, [])

  // Computed
  const unreadCount = useMemo(() => notifications.filter((n) => !n.isRead).length, [notifications])

  // Auto-expire old notifications
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now()
      setNotifications((prev) => prev.filter((n) => now - n.timestamp < NOTIFICATION_EXPIRY_MS))
    }, 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  // Context value
  const contextValue: VoiceFeedbackContextValue = useMemo(
    () => ({
      notifications,
      unreadCount,
      isPanelOpen,
      isConnected: wsContext.isConnected,
      isHandsFreeMode: audioContext.isHandsFreeMode,
      voiceFeedbackMode: audioContext.voiceFeedbackMode,
      setHandsFreeMode: audioContext.setHandsFreeMode,
      setVoiceFeedbackMode: audioContext.setVoiceFeedbackMode,
      connectWebSocket: wsContext.connect,
      disconnectWebSocket: wsContext.disconnect,
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
      wsContext,
      audioContext,
      togglePanel,
      openPanel,
      closePanel,
      markAsRead,
      markAllAsRead,
      playNotification,
      clearAll,
    ]
  )

  return <VoiceFeedbackContext.Provider value={contextValue}>{children}</VoiceFeedbackContext.Provider>
}

export function VoiceFeedbackProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<VoiceNotification[]>([])
  const dedupMapRef = useRef<Map<string, number>>(new Map())

  // Message handler that will be passed to WebSocket provider
  const handleWebSocketMessage = useCallback((data: unknown) => {
    const message = data as WebSocketMessage

    if (message.type === "voice_feedback") {
      const msg = message as VoiceFeedbackMessage

      // Dedup logic
      const generateHash = (m: VoiceFeedbackMessage): string => {
        const audioLen = m.audio?.length || 0
        const audioStart = m.audio?.substring(0, 50) || ""
        const audioEnd = m.audio?.substring(Math.max(0, audioLen - 50)) || ""
        return `${m.summary}|${audioLen}|${audioStart}|${audioEnd}`
      }

      const hash = generateHash(msg)
      const now = Date.now()
      const lastSeen = dedupMapRef.current.get(hash)

      // Clean old entries
      for (const [key, timestamp] of dedupMapRef.current.entries()) {
        if (now - timestamp > DEDUP_WINDOW_MS) {
          dedupMapRef.current.delete(key)
        }
      }

      if (lastSeen && now - lastSeen < DEDUP_WINDOW_MS) {
        console.log("[VoiceFeedback] Duplicate notification, skipping")
        return
      }

      dedupMapRef.current.set(hash, now)

      // Forward to inner component via notifications state
      // (In real implementation, would trigger audio playback here)
    }
  }, [])

  // Compose the contexts
  return (
    <VoiceWebSocketProvider onMessage={handleWebSocketMessage}>
      <VoiceAudioProvider>
        <VoiceFeedbackInner>{children}</VoiceFeedbackInner>
      </VoiceAudioProvider>
    </VoiceWebSocketProvider>
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
