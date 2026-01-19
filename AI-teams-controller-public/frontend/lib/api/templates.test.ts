/**
 * Tests for Template API Client
 *
 * TDD Sprint 1: JWT Migration - Testing auth headers
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { fetchTemplates, createTeam, type CreateTeamRequest } from './templates'

// Mock auth headers
vi.mock('@/lib/auth-utils', () => ({
  getAuthHeaders: vi.fn(() => ({
    'Authorization': 'Bearer mock-token',
    'Content-Type': 'application/json',
  })),
}))

// Mock fetch
global.fetch = vi.fn()

describe('Template API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchTemplates', () => {
    it('should fetch templates from backend with auth headers', async () => {
      const mockResponse = {
        templates: [
          {
            name: 'scrum-team',
            display_name: 'Scrum Team',
            description: 'Standard Scrum team',
            version: '1.0.0',
            roles: [
              { id: 'PO', name: 'Product Owner', description: 'Owns backlog', optional: false },
              { id: 'SM', name: 'Scrum Master', description: 'Facilitates', optional: false },
            ],
          },
        ],
      }

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as any)

      const templates = await fetchTemplates()

      expect(templates).toEqual(mockResponse.templates)
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/templates',
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: expect.stringContaining('Bearer'),
          }),
        })
      )
    })

    it('should include Authorization header with Bearer token', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ templates: [] }),
      } as any)

      await fetchTemplates()

      const callArgs = vi.mocked(global.fetch).mock.calls[0]
      const options = callArgs[1] as any
      expect(options.headers.Authorization).toBeDefined()
      expect(options.headers.Authorization).toMatch(/^Bearer /)
    })

    it('should throw error when fetch fails', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      } as any)

      await expect(fetchTemplates()).rejects.toThrow(
        'Failed to fetch templates: Not Found'
      )
    })

    it('should handle empty template list', async () => {
      const mockResponse = {
        templates: [],
      }

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as any)

      const templates = await fetchTemplates()

      expect(templates).toEqual([])
    })
  })

  describe('createTeam', () => {
    it('should create team with auth headers', async () => {
      const request: CreateTeamRequest = {
        template_name: 'scrum-team',
        project_name: 'my-project',
        prd: 'Build a cool app',
      }

      const mockResponse = {
        success: true,
        team_id: 'my-project',
        message: 'Team created',
        output_dir: 'docs/tmux/my-project',
      }

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as any)

      const result = await createTeam(request)

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/templates/create',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: expect.stringContaining('Bearer'),
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify(request),
        })
      )
    })

    it('should include Authorization header with Bearer token', async () => {
      const request: CreateTeamRequest = {
        template_name: 'scrum-team',
        project_name: 'test',
        prd: 'Test',
      }

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          team_id: 'test',
          message: 'OK',
          output_dir: 'docs/tmux/test',
        }),
      } as any)

      await createTeam(request)

      const callArgs = vi.mocked(global.fetch).mock.calls[0]
      const options = callArgs[1] as any
      expect(options.headers.Authorization).toBeDefined()
      expect(options.headers.Authorization).toMatch(/^Bearer /)
      expect(options.headers['Content-Type']).toBe('application/json')
    })

    it('should throw error when creation fails', async () => {
      const request: CreateTeamRequest = {
        template_name: 'invalid',
        project_name: 'test',
        prd: 'Test',
      }

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        statusText: 'Bad Request',
        json: async () => ({ detail: 'Template not found' }),
      } as any)

      await expect(createTeam(request)).rejects.toThrow('Template not found')
    })

    it('should handle error response without detail', async () => {
      const request: CreateTeamRequest = {
        template_name: 'invalid',
        project_name: 'test',
        prd: 'Test',
      }

      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        statusText: 'Server Error',
        json: async () => { throw new Error('Invalid JSON') },
      } as any)

      await expect(createTeam(request)).rejects.toThrow(
        'Server Error'
      )
    })
  })
})
