/**
 * Tests for Teams API Client
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { listAvailableTeams } from './teams'

// Mock auth headers
vi.mock('@/lib/auth-utils', () => ({
  getAuthHeaders: vi.fn(() => ({
    'Authorization': 'Bearer mock-token',
    'Content-Type': 'application/json',
  })),
}))

// Mock fetch
global.fetch = vi.fn()

describe('Teams API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('listAvailableTeams', () => {
    it('should fetch available teams from backend', async () => {
      const mockResponse = {
        teams: [
          {
            name: 'ai_controller_full_team',
            path: 'docs/tmux/ai_controller_full_team',
            hasSetupScript: true,
            isActive: true,
          },
          {
            name: 'my_custom_team',
            path: 'docs/tmux/my_custom_team',
            hasSetupScript: true,
            isActive: false,
          },
        ],
      }

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as any)

      const teams = await listAvailableTeams()

      expect(teams).toEqual(mockResponse.teams)
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/teams/available',
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: expect.stringContaining('Bearer'),
          }),
        })
      )
    })

    it('should throw error when fetch fails', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        statusText: 'Internal Server Error',
      } as any)

      await expect(listAvailableTeams()).rejects.toThrow(
        'Failed to fetch available teams'
      )
    })

    it('should throw error when response is not JSON', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON')
        },
      } as any)

      await expect(listAvailableTeams()).rejects.toThrow()
    })

    it('should handle empty team list', async () => {
      const mockResponse = {
        teams: [],
      }

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as any)

      const teams = await listAvailableTeams()

      expect(teams).toEqual([])
    })

    it('should include authorization header', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ teams: [] }),
      } as any)

      await listAvailableTeams()

      const callArgs = vi.mocked(global.fetch).mock.calls[0]
      const options = callArgs[1]
      expect(options.headers.Authorization).toBeDefined()
      expect(options.headers.Authorization).toMatch(/^Bearer /)
    })
  })
})
