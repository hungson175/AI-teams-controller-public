/**
 * usePanePolling - WebSocket Pane State Management Hook
 *
 * Extracted from TmuxController.tsx as part of Sprint 2 refactoring.
 *
 * Manages:
 * - WebSocket connection to backend for real-time pane updates
 * - Pane state polling and updates
 * - Keepalive ping/pong to prevent connection timeouts
 * - Auto-reconnection on connection loss
 * - Scroll position preservation during updates
 */

import { useState, useEffect, useRef, RefObject } from 'react'
import { getWebSocketBaseUrl } from '@/lib/websocket-utils'
import { getAuthHeaders } from '@/lib/auth-utils'
import { tryRefreshTokens } from '@/lib/auth'

interface PaneState {
  output: string
  highlightText?: string | null
  isActive?: boolean
}

type PollingInterval = 0.5 | 1 | 2

/**
 * WebSocket Factory Type (DIP - Dependency Inversion Principle)
 *
 * Abstraction for creating WebSocket instances. Allows for:
 * - Easy testing with mock WebSocket implementations
 * - Switching between different WebSocket libraries
 * - Decoupling hook logic from concrete WebSocket implementation
 */
type WebSocketFactory = (url: string) => WebSocket

/**
 * Default WebSocket factory - creates native browser WebSocket instances
 */
const defaultWebSocketFactory: WebSocketFactory = (url: string) => new WebSocket(url)

interface UsePanePollingParams {
  selectedTeam: string | null
  selectedRole: string | null
  pollingInterval: PollingInterval
  captureLines: number
  outputRef: RefObject<HTMLDivElement>
  isAutoScrollEnabledRef: RefObject<boolean>
  onRoleActivityUpdate?: (roleId: string, isActive: boolean) => void
  /** Optional WebSocket factory for dependency injection (DIP) */
  wsFactory?: WebSocketFactory
}

export function usePanePolling({
  selectedTeam,
  selectedRole,
  pollingInterval,
  captureLines,
  outputRef,
  isAutoScrollEnabledRef,
  onRoleActivityUpdate,
  wsFactory = defaultWebSocketFactory,
}: UsePanePollingParams) {
  const [paneStates, setPaneStates] = useState<Record<string, PaneState>>({})
  const [wsConnected, setWsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Main WebSocket connection effect
  useEffect(() => {
    // Cleanup function for ping interval and reconnect timeout
    const cleanup = () => {
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current)
        pingIntervalRef.current = null
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
    }

    if (!selectedTeam || !selectedRole) {
      cleanup()
      if (wsRef.current) {
        wsRef.current.close(1000, "cleanup")
        wsRef.current = null
        setWsConnected(false)
      }
      return
    }

    if (wsRef.current) {
      cleanup()
      wsRef.current.close(1000, "switching")
    }

    const connect = () => {
      const wsUrl = `${getWebSocketBaseUrl()}/api/ws/state/${selectedTeam}/${selectedRole}`
      const ws = wsFactory(wsUrl)

      ws.onopen = () => {
        setWsConnected(true)
        ws.send(JSON.stringify({ interval: pollingInterval, captureLines }))

        // Start keepalive ping interval (30 seconds)
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send("ping")
          }
        }, 30000)
      }

      ws.onmessage = (event) => {
        // Handle plain text "pong" response from keepalive ping
        if (event.data === "pong") {
          return
        }

        try {
          const data = JSON.parse(event.data)

          // Ignore keepalive messages from server
          if (data.type === "keepalive") {
            return
          }

          // CRITICAL: Ignore empty output messages during reconnection
          // This prevents clearing content when WebSocket reconnects
          if (!data.output || data.output.length === 0) {
            return
          }

          const scrollContainer = outputRef.current
          const savedScrollTop = scrollContainer?.scrollTop ?? 0
          const savedScrollHeight = scrollContainer?.scrollHeight ?? 0

          setPaneStates((prev) => ({
            ...prev,
            [`${selectedTeam}-${selectedRole}`]: data,
          }))

          // Update role activity indicator via callback
          if (typeof data.isActive === "boolean" && onRoleActivityUpdate) {
            onRoleActivityUpdate(selectedRole, data.isActive)
          }

          if (scrollContainer && !isAutoScrollEnabledRef.current) {
            requestAnimationFrame(() => {
              const newScrollHeight = scrollContainer.scrollHeight
              const heightDiff = newScrollHeight - savedScrollHeight
              scrollContainer.scrollTop = savedScrollTop + heightDiff
            })
          }
        } catch (e) {
          console.error("[WS] Error parsing message:", e)
        }
      }

      ws.onclose = (event) => {
        setWsConnected(false)

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current)
          pingIntervalRef.current = null
        }

        // Auto-reconnect after 5 seconds (unless intentional close)
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, 5000)
        }
      }

      ws.onerror = (error) => {
        console.error("[WS] Error:", error)
        // P0 FIX: Removed setWsConnected(false) - onclose handles it
        // Root cause: Both onerror + onclose called setWsConnected(false)
        // Result: Double state update → double re-render → topbar flicker
      }

      wsRef.current = ws
    }

    connect()

    return () => {
      cleanup()
      if (wsRef.current) {
        wsRef.current.close(1000, "effect-cleanup")
      }
    }
    // NOTE: wsFactory intentionally excluded from deps - only used during connection creation
    // Including it would cause unnecessary reconnections when factory reference changes
  }, [selectedTeam, selectedRole, pollingInterval, captureLines, outputRef, isAutoScrollEnabledRef, onRoleActivityUpdate])

  // Update polling interval on change
  useEffect(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ interval: pollingInterval }))
    }
  }, [pollingInterval])

  // Update capture lines on change
  useEffect(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ captureLines }))
    }
  }, [captureLines])

  // Visibility change handler - just log state, let auto-reconnect handle recovery
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && selectedTeam && selectedRole) {
        const state = wsRef.current?.readyState
      }
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange)
  }, [selectedTeam, selectedRole])

  // Sprint 3: Role activity polling (moved from TmuxController)
  useEffect(() => {
    if (!selectedTeam) return

    const pollActivity = async () => {
      try {
        let response = await fetch(`/api/teams/${selectedTeam}/roles`, {
          headers: getAuthHeaders(),
        })

        // Handle 401: try refresh tokens and retry once
        if (response.status === 401) {
          const refreshed = await tryRefreshTokens()
          if (refreshed) {
            response = await fetch(`/api/teams/${selectedTeam}/roles`, {
              headers: getAuthHeaders(),
            })
          } else {
            console.error("[Activity Poll] Token refresh failed, auth required")
            return
          }
        }

        if (response.ok) {
          const data = await response.json()
          // Update roleActivity via callback for each role
          if (onRoleActivityUpdate) {
            data.roles.forEach((role: { id: string; isActive?: boolean }) => {
              onRoleActivityUpdate(role.id, role.isActive ?? false)
            })
          }
        }
      } catch (err) {
        console.error("[Activity Poll] Error:", err)
      }
    }

    const intervalId = setInterval(pollActivity, 5000)
    return () => clearInterval(intervalId)
  }, [selectedTeam, onRoleActivityUpdate])

  return {
    paneStates,
    wsConnected,
    setPaneStates,
    wsRef,
  }
}
