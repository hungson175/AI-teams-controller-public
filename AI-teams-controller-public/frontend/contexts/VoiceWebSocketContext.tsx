"use client"

/**
 * VoiceWebSocketContext - WebSocket Connection Management (Sprint 6: SRP)
 *
 * Extracted from VoiceFeedbackContext as part of SOLID refactoring.
 *
 * Responsibility: WebSocket connection management ONLY
 * - Connect/disconnect WebSocket
 * - Connection state tracking
 * - Auto-reconnection on abnormal close
 * - Keepalive ping/pong (prevents proxy timeouts)
 * - Message sending/receiving
 *
 * Does NOT handle:
 * - Audio playback (VoiceAudioContext responsibility)
 * - Notifications (VoiceFeedbackProvider responsibility)
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
import { getWebSocketBaseUrl } from "@/lib/websocket-utils"

// ============================================
// Types
// ============================================

/**
 * WebSocket Factory Type (DIP - Dependency Inversion Principle)
 */
type WebSocketFactory = (url: string) => WebSocket

/**
 * Default WebSocket factory - creates native browser WebSocket instances
 * NOTE: Don't inline this - defined as a separate function to allow test mocking
 */
const defaultWebSocketFactory: WebSocketFactory = (url: string) => {
  // @ts-ignore - WebSocket will be mocked in tests
  return new WebSocket(url)
}

/**
 * Keepalive ping interval (30 seconds) - prevents Cloudflare/proxy timeouts
 */
const PING_INTERVAL_MS = 30000

/**
 * Auto-reconnect delay (5 seconds)
 */
const RECONNECT_DELAY_MS = 5000

interface VoiceWebSocketContextValue {
  /** Whether WebSocket is currently connected */
  isConnected: boolean
  /** Connect to WebSocket (idempotent - safe to call multiple times) */
  connect: () => void
  /** Disconnect from WebSocket */
  disconnect: () => void
  /** Send message to WebSocket (only when connected) */
  sendMessage: (message: unknown) => void
}

// ============================================
// Context
// ============================================

const VoiceWebSocketContext = createContext<VoiceWebSocketContextValue | null>(null)

// ============================================
// Provider Component
// ============================================

interface VoiceWebSocketProviderProps {
  children: ReactNode
  /** Optional message handler for received WebSocket messages */
  onMessage?: (message: unknown) => void
  /** Optional WebSocket factory for dependency injection (testing) */
  wsFactory?: WebSocketFactory
}

export function VoiceWebSocketProvider({
  children,
  onMessage,
  wsFactory = defaultWebSocketFactory,
}: VoiceWebSocketProviderProps) {
  // State
  const [isConnected, setIsConnected] = useState(false)

  // Refs
  const wsRef = useRef<WebSocket | null>(null)
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const onMessageRef = useRef(onMessage)

  // Sync onMessage ref (prevents stale closures)
  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  // ============================================
  // Keepalive Ping/Pong
  // ============================================

  const stopPingInterval = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
      pingIntervalRef.current = null
    }
  }, [])

  const startPingInterval = useCallback(() => {
    stopPingInterval() // Clear any existing interval

    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send("ping")
          console.log("[VoiceWebSocket] Keepalive ping sent")
        } catch (error) {
          console.error("[VoiceWebSocket] Failed to send ping:", error)
        }
      }
    }, PING_INTERVAL_MS)

    console.log(`[VoiceWebSocket] Started keepalive ping interval (${PING_INTERVAL_MS / 1000}s)`)
  }, [stopPingInterval])

  // ============================================
  // Message Handler
  // ============================================

  const handleMessage = useCallback((event: MessageEvent) => {
    // Handle plain text "pong" response from keepalive ping
    if (event.data === "pong") {
      console.log("[VoiceWebSocket] Received keepalive pong")
      return
    }

    try {
      const data = JSON.parse(event.data)
      console.log("[VoiceWebSocket] Message received:", data.type || "unknown")

      // Forward to parent via callback
      if (onMessageRef.current) {
        onMessageRef.current(data)
      }
    } catch (error) {
      console.error("[VoiceWebSocket] Message parse error:", error)
    }
  }, [])

  // ============================================
  // WebSocket Connection Management
  // ============================================

  const connect = useCallback(() => {
    // Already connected or connecting
    if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
      console.log("[VoiceWebSocket] Already connected or connecting")
      return
    }

    // WebSocket must connect directly to backend (Next.js rewrites don't support WS)
    const wsUrl = `${getWebSocketBaseUrl()}/api/voice/ws/feedback/global`

    console.log("[VoiceWebSocket] Connecting to:", wsUrl)

    const ws = wsFactory(wsUrl)

    ws.onopen = () => {
      console.log("[VoiceWebSocket] Connected")
      setIsConnected(true)
      startPingInterval()
    }

    ws.onmessage = handleMessage

    ws.onerror = (error) => {
      console.error("[VoiceWebSocket] Error:", error)
    }

    ws.onclose = (event) => {
      console.log("[VoiceWebSocket] Closed:", event.code, event.reason)
      setIsConnected(false)
      wsRef.current = null
      stopPingInterval()

      // Auto-reconnect after 5 seconds (unless normal close)
      if (event.code !== 1000) {
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log("[VoiceWebSocket] Auto-reconnecting...")
          connect()
        }, RECONNECT_DELAY_MS)
      }
    }

    wsRef.current = ws
  }, [wsFactory, handleMessage, startPingInterval, stopPingInterval])

  const disconnect = useCallback(() => {
    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    // Stop keepalive ping interval
    stopPingInterval()

    if (wsRef.current) {
      wsRef.current.close(1000, "manual-disconnect")
      wsRef.current = null
    }

    setIsConnected(false)
  }, [stopPingInterval])

  const sendMessage = useCallback((message: unknown) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn("[VoiceWebSocket] Cannot send message - not connected")
      return
    }

    try {
      wsRef.current.send(JSON.stringify(message))
      console.log("[VoiceWebSocket] Message sent:", message)
    } catch (error) {
      console.error("[VoiceWebSocket] Failed to send message:", error)
    }
  }, [])

  // ============================================
  // Effects
  // ============================================

  // Auto-connect on mount
  useEffect(() => {
    connect()
    return () => {
      disconnect()
    }
  // eslint-disable-next-line
  }, [])

  // Visibility change handler - reconnect WebSocket when tab becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        console.log("[VoiceWebSocket] Tab became visible, checking connection...")
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          console.log("[VoiceWebSocket] Not connected, reconnecting...")
          connect()
        }
      }
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange)
    }
  // eslint-disable-next-line
  }, [])

  // ============================================
  // Context Value
  // ============================================

  const contextValue: VoiceWebSocketContextValue = useMemo(
    () => ({
      isConnected,
      connect,
      disconnect,
      sendMessage,
    }),
    [isConnected, connect, disconnect, sendMessage]
  )

  return (
    <VoiceWebSocketContext.Provider value={contextValue}>
      {children}
    </VoiceWebSocketContext.Provider>
  )
}

// ============================================
// Hook
// ============================================

export function useVoiceWebSocket(): VoiceWebSocketContextValue {
  const context = useContext(VoiceWebSocketContext)
  if (!context) {
    throw new Error("useVoiceWebSocket must be used within VoiceWebSocketProvider")
  }
  return context
}

export default VoiceWebSocketContext
