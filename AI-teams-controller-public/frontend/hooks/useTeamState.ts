/**
 * useTeamState - Team and Role State Management Hook
 *
 * Extracted from TmuxController.tsx as part of Sprint 2 refactoring.
 * Refactored in Sprint 6 to use TeamApiService (DIP - Dependency Inversion Principle).
 *
 * Manages:
 * - Team list and selected team
 * - Role list and selected role
 * - Team notification indicators
 * - Role activity tracking
 * - Fetching teams and roles via injected service
 */

import { useState, useEffect, useRef } from 'react'
import { teamApiService, type ITeamService, type Team, type Role } from '@/lib/services/teamApi'

/**
 * useTeamState Hook
 *
 * @param teamService - Optional team service for dependency injection (defaults to teamApiService)
 * @returns Team state and actions
 */
export function useTeamState(teamService: ITeamService = teamApiService) {
  const [teams, setTeams] = useState<Team[]>([])
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)
  const [roles, setRoles] = useState<Role[]>([])
  const [selectedRole, setSelectedRole] = useState<string | null>(null)
  const [teamNotifications, setTeamNotifications] = useState<Set<string>>(new Set())
  const [roleActivity, setRoleActivity] = useState<Record<string, boolean>>({})
  const prevTeamActivityRef = useRef<Record<string, boolean>>({})

  const fetchTeams = async () => {
    try {
      const fetchedTeams = await teamService.getTeams()

      // Detect new activity for non-selected teams
      const newNotifications = new Set(teamNotifications)
      fetchedTeams.forEach((team) => {
        const wasActive = prevTeamActivityRef.current[team.id] ?? false
        const isNowActive = team.isActive ?? false

        // If activity changed from false to true AND it's not the selected team, add notification
        if (!wasActive && isNowActive && team.id !== selectedTeam) {
          newNotifications.add(team.id)
        }

        // Update previous state
        prevTeamActivityRef.current[team.id] = isNowActive
      })
      setTeamNotifications(newNotifications)

      setTeams(fetchedTeams)
      if (fetchedTeams.length > 0 && !selectedTeam) {
        setSelectedTeam(fetchedTeams[0].id)
      }
    } catch (err) {
      console.error("[useTeamState] fetchTeams error:", err)
    }
  }

  const fetchRoles = async (teamId: string) => {
    try {
      const fetchedRoles = await teamService.getRoles(teamId)
      setRoles(fetchedRoles)

      // Initialize roleActivity from roles endpoint (all roles at once)
      const activityMap: Record<string, boolean> = {}
      fetchedRoles.forEach((role) => {
        activityMap[role.id] = role.isActive ?? false
      })
      setRoleActivity(activityMap)

      if (fetchedRoles.length > 0 && !selectedRole) {
        setSelectedRole(fetchedRoles[0].id)
      }
    } catch (err) {
      console.error("[useTeamState] fetchRoles error:", err)
    }
  }

  const handleSelectTeam = (teamId: string) => {
    setSelectedTeam(teamId)
    setSelectedRole(null)
    // Clear notification for this team when clicked
    setTeamNotifications((prev) => {
      const next = new Set(prev)
      next.delete(teamId)
      return next
    })
  }

  // Sprint 3: Team activity polling (moved from TmuxController)
  // Sprint 6: Refactored to use TeamApiService (DIP compliance)
  useEffect(() => {
    const pollTeams = async () => {
      try {
        const fetchedTeams = await teamService.getTeams()

        // Detect new activity for non-selected teams
        const newNotifications = new Set(teamNotifications)
        fetchedTeams.forEach((team) => {
          const wasActive = prevTeamActivityRef.current[team.id] ?? false
          const isNowActive = team.isActive ?? false

          // If activity changed from false to true AND it's not the selected team, add notification
          if (!wasActive && isNowActive && team.id !== selectedTeam) {
            newNotifications.add(team.id)
          }

          // Update previous state
          prevTeamActivityRef.current[team.id] = isNowActive
        })
        setTeamNotifications(newNotifications)

        // P0 FIX: Only update if teams actually changed (prevents re-render every 10s)
        if (JSON.stringify(teams) !== JSON.stringify(fetchedTeams)) {
          setTeams(fetchedTeams)
        }
      } catch (err) {
        console.error("[useTeamState] Team polling error:", err)
      }
    }

    const intervalId = setInterval(pollTeams, 10000) // Poll every 10 seconds
    return () => clearInterval(intervalId)
  }, [selectedTeam, teamNotifications, teamService])

  return {
    // State
    teams,
    selectedTeam,
    roles,
    selectedRole,
    teamNotifications,
    roleActivity,
    prevTeamActivityRef,

    // Setters (for other hooks to update)
    setTeams,
    setSelectedTeam,
    setRoles,
    setSelectedRole,
    setTeamNotifications,
    setRoleActivity,

    // Actions
    fetchTeams,
    fetchRoles,
    handleSelectTeam,
  }
}
