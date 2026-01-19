/**
 * TeamSelector Component
 *
 * Dropdown to select a tmux team session in Monitor mode.
 * Fetches available teams from /api/teams and shows connection status.
 *
 * Edge cases handled:
 * - Loading state while fetching teams
 * - Error state if API fails
 * - Empty state if no teams found
 * - Connection status indicator with tooltip
 *
 * Sprint 32: Team Creator S5 - Real-time Status
 * Sprint 33: Added connection status tooltips
 */
"use client"

import { useState, useEffect } from "react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Loader2, Circle, AlertCircle } from "lucide-react"
import { MonitorConnectionStatus } from "@/lib/team-creator/types"
import { getAuthHeaders } from "@/lib/auth-utils"
import { tryRefreshTokens } from "@/lib/auth"

interface TeamSelectorProps {
  selectedTeam: string | null
  onSelectTeam: (team: string) => void
  connectionStatus: MonitorConnectionStatus
}

interface Team {
  name: string
  panes: number
}

export function TeamSelector({
  selectedTeam,
  onSelectTeam,
  connectionStatus,
}: TeamSelectorProps) {
  const [teams, setTeams] = useState<Team[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch teams from API
  useEffect(() => {
    const fetchTeams = async () => {
      setIsLoading(true)
      setError(null)

      try {
        let response = await fetch(`/api/teams`, {
          headers: getAuthHeaders(),
        })

        // Handle 401: try refresh tokens and retry once
        if (response.status === 401) {
          const refreshed = await tryRefreshTokens()
          if (refreshed) {
            response = await fetch(`/api/teams`, {
              headers: getAuthHeaders(),
            })
          } else {
            console.error("[TeamSelector] Token refresh failed")
            setError("Authentication required")
            return
          }
        }

        if (!response.ok) {
          throw new Error(`Failed to fetch teams: ${response.status}`)
        }

        const data = await response.json()
        setTeams(data.teams || [])
      } catch (err) {
        console.error("[TeamSelector] Error fetching teams:", err)
        setError("Failed to load teams")
      } finally {
        setIsLoading(false)
      }
    }

    fetchTeams()
  }, [])

  // Connection status indicator
  const StatusIndicator = () => {
    switch (connectionStatus) {
      case "connected":
        return <Circle className="h-3 w-3 fill-green-500 text-green-500" />
      case "connecting":
        return <Loader2 className="h-3 w-3 animate-spin text-yellow-500" />
      case "error":
        return <AlertCircle className="h-3 w-3 text-red-500" />
      default:
        return <Circle className="h-3 w-3 text-muted-foreground" />
    }
  }

  const statusText = () => {
    switch (connectionStatus) {
      case "connected":
        return "Live"
      case "connecting":
        return "Connecting..."
      case "error":
        return "Error"
      default:
        return ""
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading teams...
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 text-sm text-red-500">
        <AlertCircle className="h-4 w-4" />
        {error}
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-muted-foreground">Team:</span>
      <Select value={selectedTeam || ""} onValueChange={onSelectTeam}>
        <SelectTrigger className="w-[220px] h-9">
          <SelectValue placeholder="Select team..." />
        </SelectTrigger>
        <SelectContent>
          {teams.length === 0 ? (
            <div className="p-2 text-sm text-muted-foreground text-center">
              No teams found
            </div>
          ) : (
            teams.map((team) => (
              <SelectItem key={team.name} value={team.name}>
                <div className="flex items-center justify-between w-full">
                  <span>{team.name}</span>
                  <span className="text-xs text-muted-foreground ml-2">
                    ({team.panes} panes)
                  </span>
                </div>
              </SelectItem>
            ))
          )}
        </SelectContent>
      </Select>

      {/* Connection status with tooltip */}
      {selectedTeam && (
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-1.5 text-xs cursor-help">
              <StatusIndicator />
              <span className="text-muted-foreground">{statusText()}</span>
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom" sideOffset={8}>
            {connectionStatus === "connected" && "WebSocket connected - receiving live status updates"}
            {connectionStatus === "connecting" && "Establishing WebSocket connection..."}
            {connectionStatus === "error" && "Connection failed - check backend server"}
            {connectionStatus === "disconnected" && "Not connected to team"}
          </TooltipContent>
        </Tooltip>
      )}
    </div>
  )
}
