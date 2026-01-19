import { getAuthHeaders } from "@/lib/auth-utils"
import { tryRefreshTokens } from "@/lib/auth"

/**
 * Team type matching API response
 */
export interface Team {
  id: string
  name: string
  isActive?: boolean
}

/**
 * Role type matching API response
 */
export interface Role {
  id: string
  name: string
  order: number
  isActive?: boolean
}

/**
 * Team Service Interface (DIP - Dependency Inversion Principle)
 *
 * Abstraction for team/role data fetching. Allows for:
 * - Easy testing with mock implementations
 * - Switching between different API implementations
 * - Decoupling business logic from HTTP details
 */
export interface ITeamService {
  /**
   * Fetch all teams
   * @returns Array of teams
   * @throws Error if request fails
   */
  getTeams(): Promise<Team[]>

  /**
   * Fetch roles for a specific team
   * @param teamId - Team identifier
   * @returns Array of roles
   * @throws Error if request fails
   */
  getRoles(teamId: string): Promise<Role[]>
}

/**
 * Team API Service Implementation
 *
 * Production implementation of ITeamService using fetch API.
 * Handles auth headers, token refresh on 401, and error handling.
 *
 * @example
 * ```typescript
 * const service = new TeamApiService("/api", fetch)
 * const teams = await service.getTeams()
 * const roles = await service.getRoles("team-id")
 * ```
 */
export class TeamApiService implements ITeamService {
  constructor(
    private baseUrl: string,
    private fetcher: typeof fetch = fetch
  ) {}

  /**
   * Fetch all teams from API
   * Automatically retries with token refresh on 401
   */
  async getTeams(): Promise<Team[]> {
    let response = await this.fetcher(`${this.baseUrl}/teams`, {
      headers: getAuthHeaders(),
    })

    // Handle 401: try refresh tokens and retry once
    if (response.status === 401) {
      const refreshed = await tryRefreshTokens()
      if (refreshed) {
        response = await this.fetcher(`${this.baseUrl}/teams`, {
          headers: getAuthHeaders(),
        })
      } else {
        throw new Error("Failed to fetch teams: 401 (auth refresh failed)")
      }
    }

    if (!response.ok) {
      throw new Error(`Failed to fetch teams: ${response.status}`)
    }

    const data = await response.json()
    return data.teams || []
  }

  /**
   * Fetch roles for a specific team
   * Automatically retries with token refresh on 401
   */
  async getRoles(teamId: string): Promise<Role[]> {
    let response = await this.fetcher(`${this.baseUrl}/teams/${teamId}/roles`, {
      headers: getAuthHeaders(),
    })

    // Handle 401: try refresh tokens and retry once
    if (response.status === 401) {
      const refreshed = await tryRefreshTokens()
      if (refreshed) {
        response = await this.fetcher(`${this.baseUrl}/teams/${teamId}/roles`, {
          headers: getAuthHeaders(),
        })
      } else {
        throw new Error(`Failed to fetch roles: 401 (auth refresh failed)`)
      }
    }

    if (!response.ok) {
      throw new Error(`Failed to fetch roles: ${response.status}`)
    }

    const data = await response.json()
    return data.roles || []
  }
}

/**
 * Default singleton instance for production use
 * Uses browser's native fetch and /api base URL
 * NOTE: Arrow function wrapper prevents "Illegal invocation" error (maintains fetch binding)
 */
export const teamApiService = new TeamApiService("/api", (input, init) => fetch(input, init))
