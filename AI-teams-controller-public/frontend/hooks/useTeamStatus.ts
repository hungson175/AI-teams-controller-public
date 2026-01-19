/**
 * useTeamStatus Hook
 *
 * WebSocket hook for real-time team status in Monitor mode.
 * Connects to /api/ws/state/{team}/{role} for each role.
 * Sprint 32: Team Creator S5 - Real-time Status
 */

import { useState, useEffect, useCallback, useRef } from "react"
import type { RoleStatus, MonitorConnectionStatus } from "@/lib/team-creator/types"

// WebSocket URLs must connect DIRECTLY to backend (Next.js rewrites don't support WebSocket)
function getWebSocketBaseUrl(): string {
  if (typeof window === "undefined") return "ws://localhost:17061"

  const hostname = window.location.hostname
  if (hostname === "voice-ui.hungson175.com") {
    // Cloudflare: connect to backend domain directly
    return "wss://voice-backend.hungson175.com"
  }
  // Localhost: connect to backend port directly
  return "ws://localhost:17061"
}

// ============================================
// Types
// ============================================

export interface RoleStatusMap {
  [roleId: string]: RoleStatus
}

interface UseTeamStatusOptions {
  team: string | null
  roles: string[] // Role IDs to monitor (e.g., ["PM", "SA", "FE"])
  enabled: boolean // Only connect when in Monitor mode
  pollingInterval?: number // ms between status checks (default 5000)
}

interface UseTeamStatusReturn {
  statusMap: RoleStatusMap
  connectionStatus: MonitorConnectionStatus
  error: string | null
  reconnect: () => void
}

// ============================================
// Hook
// ============================================

export function useTeamStatus({
  team,
  roles,
  enabled,
  pollingInterval = 5000,
}: UseTeamStatusOptions): UseTeamStatusReturn {
  const [statusMap, setStatusMap] = useState<RoleStatusMap>({})
  const [connectionStatus, setConnectionStatus] = useState<MonitorConnectionStatus>("disconnected")
  const [error, setError] = useState<string | null>(null)

  const wsRefs = useRef<Map<string, WebSocket>>(new Map())
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Cleanup function
  const cleanup = useCallback(() => {
    // Clear any pending reconnect
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    // Close all WebSockets
    wsRefs.current.forEach((ws, role) => {
      console.log(`[TeamStatus] Closing WebSocket for ${role}`)
      ws.close()
    })
    wsRefs.current.clear()
    setStatusMap({})
    setConnectionStatus("disconnected")
    setError(null)
  }, [])

  // Connect to WebSocket for a single role
  const connectRole = useCallback((role: string) => {
    if (!team) return

    const wsUrl = `${getWebSocketBaseUrl()}/api/ws/state/${team}/${role}`
    console.log(`[TeamStatus] Connecting to ${wsUrl}`)

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log(`[TeamStatus] Connected: ${role}`)
      ws.send(JSON.stringify({ interval: pollingInterval, captureLines: 50 }))

      // Update connection status if this is the first connection
      setConnectionStatus("connected")
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        const isActive = typeof data.isActive === "boolean" ? data.isActive : false

        setStatusMap((prev) => ({
          ...prev,
          [role]: isActive ? "active" : "idle",
        }))
      } catch (e) {
        console.error(`[TeamStatus] Parse error for ${role}:`, e)
      }
    }

    ws.onclose = () => {
      console.log(`[TeamStatus] Disconnected: ${role}`)
      wsRefs.current.delete(role)

      // Check if all connections are closed
      if (wsRefs.current.size === 0) {
        setConnectionStatus("disconnected")
      }
    }

    ws.onerror = (err) => {
      console.error(`[TeamStatus] Error for ${role}:`, err)
      setError(`Connection error for ${role}`)
      setConnectionStatus("error")
    }

    wsRefs.current.set(role, ws)
  }, [team, pollingInterval])

  // Connect to all roles
  const connectAll = useCallback(() => {
    if (!team || !enabled || roles.length === 0) {
      return
    }

    setConnectionStatus("connecting")
    setError(null)

    roles.forEach((role) => {
      connectRole(role)
    })
  }, [team, enabled, roles, connectRole])

  // Reconnect function (exposed to consumer)
  const reconnect = useCallback(() => {
    cleanup()
    // Small delay before reconnecting
    reconnectTimeoutRef.current = setTimeout(() => {
      connectAll()
    }, 500)
  }, [cleanup, connectAll])

  // Effect: Connect/disconnect based on enabled state
  useEffect(() => {
    if (enabled && team && roles.length > 0) {
      connectAll()
    } else {
      cleanup()
    }

    return cleanup
  }, [enabled, team, roles.length, connectAll, cleanup])

  // Effect: Update polling interval on existing connections
  useEffect(() => {
    wsRefs.current.forEach((ws) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ interval: pollingInterval }))
      }
    })
  }, [pollingInterval])

  return {
    statusMap,
    connectionStatus,
    error,
    reconnect,
  }
}
