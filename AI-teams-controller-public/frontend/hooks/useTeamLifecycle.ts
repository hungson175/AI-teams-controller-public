/**
 * useTeamLifecycle - Team Lifecycle Management Hook
 *
 * Extracted from TmuxController.tsx as part of Sprint 2 refactoring.
 *
 * Manages:
 * - Kill team operations
 * - Restart team with setup script
 * - Create terminal (single pane)
 * - Create team callbacks
 * - Load team callbacks
 */

import { useState } from 'react'
import { getAuthHeaders } from '@/lib/auth-utils'
import { toast } from '@/hooks/use-toast'

interface Team {
  id: string
  name: string
}

export type RestartProgress =
  | "idle"
  | "killing"
  | "looking_for_script"
  | "running_script"
  | "complete"
  | "no_script"

interface UseTeamLifecycleParams {
  teams: Team[]
  selectedTeam: string | null
  onTeamListRefresh: () => Promise<void>
  onTeamSelect: (teamId: string | null) => void
  onRoleSelect: (roleId: string | null) => void
  onRolesUpdate: (roles: any[]) => void
}

export function useTeamLifecycle({
  teams,
  selectedTeam,
  onTeamListRefresh,
  onTeamSelect,
  onRoleSelect,
  onRolesUpdate,
}: UseTeamLifecycleParams) {
  const [isKillingTeam, setIsKillingTeam] = useState(false)
  const [restartProgress, setRestartProgress] = useState<RestartProgress>("idle")
  const [isCreatingTerminal, setIsCreatingTerminal] = useState(false)

  const handleKillTeam = async (teamId: string) => {
    const teamName = teams.find((t) => t.id === teamId)?.name || teamId
    setIsKillingTeam(true)

    try {
      const response = await fetch(`/api/teams/${teamId}/kill`, {
        method: "POST",
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Unknown error" }))
        toast({
          title: "Failed to kill team",
          description: errorData.message || `Error: ${response.status}`,
          variant: "destructive",
        })
        return
      }

      // Success - refresh team list and clear selection if killed team was selected
      toast({
        title: "Team terminated",
        description: `${teamName} has been killed.`,
      })

      // Clear selection if killed team was selected
      if (selectedTeam === teamId) {
        onTeamSelect(null)
        onRoleSelect(null)
        onRolesUpdate([])
      }

      // Refresh team list
      await onTeamListRefresh()
    } catch (error) {
      console.error("[TmuxController] killTeam error:", error)
      toast({
        title: "Failed to kill team",
        description: "Network error occurred",
        variant: "destructive",
      })
    } finally {
      setIsKillingTeam(false)
    }
  }

  const handleRestartTeam = async (teamId: string) => {
    const teamName = teams.find((t) => t.id === teamId)?.name || teamId

    try {
      // Step 1: Killing session
      setRestartProgress("killing")
      await new Promise((resolve) => setTimeout(resolve, 500)) // Brief delay for UX

      // Step 2: Looking for setup script
      setRestartProgress("looking_for_script")
      await new Promise((resolve) => setTimeout(resolve, 300)) // Brief delay for UX

      // Step 3: Call API (backend handles the actual restart)
      setRestartProgress("running_script")

      const response = await fetch(`/api/teams/${teamId}/restart`, {
        method: "POST",
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Unknown error" }))
        toast({
          title: "Failed to restart team",
          description: errorData.message || `Error: ${response.status}`,
          variant: "destructive",
        })
        return
      }

      const data = await response.json()

      // Step 4: Show result
      if (data.setupScriptRun) {
        setRestartProgress("complete")
        toast({
          title: "Team restarted",
          description: `${teamName} has been restarted with setup script.`,
        })
      } else {
        setRestartProgress("no_script")
        toast({
          title: "Team killed",
          description: data.message || `${teamName} killed. No setup script found.`,
        })
      }

      // Refresh team list and auto-select if still exists
      await onTeamListRefresh()

      // Brief delay to show final status
      await new Promise((resolve) => setTimeout(resolve, 1000))
    } catch (error) {
      console.error("[TmuxController] restartTeam error:", error)
      toast({
        title: "Failed to restart team",
        description: "Network error occurred",
        variant: "destructive",
      })
    } finally {
      setRestartProgress("idle")
    }
  }

  const handleCreateTerminal = async (name?: string, directory?: string) => {
    setIsCreatingTerminal(true)

    try {
      const response = await fetch(`/api/teams/create-terminal`, {
        method: "POST",
        headers: {
          ...getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: name || null, directory: directory || null }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Unknown error" }))
        toast({
          title: "Failed to create terminal",
          description: errorData.message || `Error: ${response.status}`,
          variant: "destructive",
        })
        return
      }

      const data = await response.json()

      toast({
        title: "Terminal created",
        description: `Terminal "${data.teamId}" created successfully.`,
      })

      // Refresh team list and auto-select new terminal
      await onTeamListRefresh()
      onTeamSelect(data.teamId)
      onRoleSelect(null)
      onRolesUpdate([])
    } catch (error) {
      console.error("[TmuxController] createTerminal error:", error)
      toast({
        title: "Failed to create terminal",
        description: "Network error occurred",
        variant: "destructive",
      })
    } finally {
      setIsCreatingTerminal(false)
    }
  }

  const handleCreateTeam = async (teamId: string) => {
    toast({
      title: "Team created",
      description: `Team "${teamId}" created successfully.`,
    })

    // Refresh team list and auto-select new team
    await onTeamListRefresh()
    onTeamSelect(teamId)
    onRoleSelect(null)
    onRolesUpdate([])
  }

  const handleLoadTeam = async (teamName: string) => {
    toast({
      title: "Team loaded",
      description: `Team "${teamName}" loaded successfully.`,
    })

    // Refresh team list and auto-select loaded team
    await onTeamListRefresh()
    onTeamSelect(teamName)
    onRoleSelect(null)
    onRolesUpdate([])
  }

  return {
    // State
    isKillingTeam,
    restartProgress,
    isCreatingTerminal,

    // Actions
    handleKillTeam,
    handleRestartTeam,
    handleCreateTerminal,
    handleCreateTeam,
    handleLoadTeam,
  }
}
