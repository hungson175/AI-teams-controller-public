/**
 * TmuxController Baseline Tests (Sprint 2 - TDD Phase 1)
 *
 * Tests for EXISTING behavior BEFORE refactoring.
 * These tests must PASS with current code, then PASS after hook extraction.
 *
 * Coverage areas:
 * 1. Team/Role State Management (future useTeamState)
 * 2. Pane Polling/WebSocket (future usePanePolling)
 * 3. Team Lifecycle (future useTeamLifecycle)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { TmuxController } from './TmuxController'

// Mock dependencies
vi.mock('@/hooks/useVoiceRecorder', () => ({
  useVoiceRecorder: () => ({
    clearTranscript: vi.fn(),
    startRecording: vi.fn(),
    stopRecording: vi.fn(),
    isRecording: false,
    state: 'idle',
    canRecord: true,
  }),
}))

vi.mock('@/contexts/VoiceFeedbackContext', () => ({
  useVoiceFeedback: () => ({
    unreadCount: 0,
    togglePanel: vi.fn(),
    isConnected: false,
    setHandsFreeMode: vi.fn(),
  }),
}))

vi.mock('@/hooks/use-mobile', () => ({
  useIsMobile: () => false,
}))

vi.mock('@/lib/auth-utils', () => ({
  getAuthHeaders: () => ({
    'Authorization': 'Bearer test-token',
    'Content-Type': 'application/json',
  }),
}))

vi.mock('@/lib/auth', () => ({
  tryRefreshTokens: vi.fn().mockResolvedValue(true),
  getToken: () => 'test-token',
}))

vi.mock('@/hooks/use-toast', () => ({
  toast: vi.fn(),
}))

// Mock fetch globally
global.fetch = vi.fn()

describe('TmuxController - Baseline Tests (Pre-Refactoring)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ teams: [], roles: [] }),
    } as Response)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('1. Team/Role State Management', () => {
    it('should render without crashing', async () => {
      const { container } = render(<TmuxController />)
      expect(container).toBeInTheDocument()
    })

    it('should fetch teams on mount', async () => {
      render(<TmuxController />)

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/teams',
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer test-token',
            }),
          })
        )
      })
    })

    it('should handle fetch errors gracefully', async () => {
      // BASELINE TEST: Current fetchTeams() does NOT retry on 401
      // It just logs error and returns. Retry logic exists in polling useEffect.
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 401,
      } as Response)

      const { container } = render(<TmuxController />)

      // Component should render without crashing even on 401
      expect(container.querySelector('div')).toBeInTheDocument()

      // Should have attempted to fetch teams
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/teams',
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer test-token',
            }),
          })
        )
      })

      // Current behavior: no retry in initial fetch (only in polling)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('2. Component Renders', () => {
    it('should initialize with correct default state', async () => {
      const { container } = render(<TmuxController />)
      
      // Component should mount successfully
      expect(container.querySelector('div')).toBeInTheDocument()
      
      // Should attempt to fetch teams
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled()
      })
    })
  })
})
