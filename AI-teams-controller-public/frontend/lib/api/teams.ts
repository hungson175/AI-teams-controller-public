/**
 * Teams API Client
 *
 * Fetches and loads teams from backend API.
 */

import { getAuthHeaders } from '../auth-utils'

// Types matching backend schemas
export interface AvailableTeam {
  name: string
  path: string
  hasSetupScript: boolean
  isActive: boolean
}

export interface ListAvailableTeamsResponse {
  teams: AvailableTeam[]
}

export interface LoadTeamResponse {
  success: boolean
  message: string
  setupScriptRun: boolean
}

export interface RestartTeamResponse {
  status: string
  team: string
  panes: Array<{ id: string; role: string }>
}

/**
 * Fetch all available teams from backend
 */
export async function listAvailableTeams(): Promise<AvailableTeam[]> {
  const response = await fetch('/api/teams/available', {
    headers: getAuthHeaders(),
  })

  if (!response.ok) {
    throw new Error('Failed to fetch available teams')
  }

  const data: ListAvailableTeamsResponse = await response.json()
  return data.teams
}

/**
 * Load a team by running its setup script
 */
export async function loadTeam(teamName: string): Promise<LoadTeamResponse> {
  const response = await fetch(`/api/teams/load/${teamName}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `Failed to load team: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Restart an entire team (full restart)
 */
export async function restartTeam(teamName: string): Promise<RestartTeamResponse> {
  const response = await fetch(`/api/teams/${teamName}/restart`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `Failed to restart team: ${response.statusText}`)
  }

  return response.json()
}
