/**
 * Tests for LoadTeamDialog Component
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { LoadTeamDialog } from './LoadTeamDialog'

// Mock auth headers
vi.mock('@/lib/auth-utils', () => ({
  getAuthHeaders: vi.fn(() => ({
    'Authorization': 'Bearer mock-token',
    'Content-Type': 'application/json',
  })),
}))

// Mock the API
vi.mock('@/lib/api/teams', () => ({
  listAvailableTeams: vi.fn(),
  loadTeam: vi.fn(),
}))

import { listAvailableTeams, loadTeam } from '@/lib/api/teams'

describe('LoadTeamDialog', () => {
  const mockAvailableTeams = [
    {
      name: 'ai_controller_full_team',
      path: 'docs/tmux/ai_controller_full_team',
      hasSetupScript: true,
      isActive: true,
    },
    {
      name: 'inactive_team',
      path: 'docs/tmux/inactive_team',
      hasSetupScript: true,
      isActive: false,
    },
    {
      name: 'no_script_team',
      path: 'docs/tmux/no_script_team',
      hasSetupScript: false,
      isActive: false,
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(listAvailableTeams).mockResolvedValue(mockAvailableTeams)
  })

  it('should fetch teams when dialog opens', async () => {
    render(
      <LoadTeamDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />
    )

    await waitFor(() => {
      expect(listAvailableTeams).toHaveBeenCalled()
    })
  })

  it('should display teams in list', async () => {
    render(
      <LoadTeamDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('ai_controller_full_team')).toBeInTheDocument()
      expect(screen.getByText('inactive_team')).toBeInTheDocument()
      expect(screen.getByText('no_script_team')).toBeInTheDocument()
    })
  })

  it('should allow selecting a team', async () => {
    const user = userEvent.setup()

    render(
      <LoadTeamDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('ai_controller_full_team')).toBeInTheDocument()
    })

    const teamButton = screen.getByText('ai_controller_full_team')
    await user.click(teamButton)

    // Load button should be enabled after selecting team with setup script
    const loadButton = screen.getByRole('button', { name: /load/i })
    expect(loadButton).not.toBeDisabled()
  })

  it('should disable Load button for team without setup script', async () => {
    const user = userEvent.setup()

    render(
      <LoadTeamDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('no_script_team')).toBeInTheDocument()
    })

    const teamButton = screen.getByText('no_script_team')
    await user.click(teamButton)

    const loadButton = screen.getByRole('button', { name: /load/i })
    expect(loadButton).toBeDisabled()
  })

  it('should call loadTeam API and onSuccess when Load button clicked', async () => {
    const user = userEvent.setup()
    const onSuccess = vi.fn()

    vi.mocked(loadTeam).mockResolvedValueOnce({
      success: true,
      message: 'Team loaded',
      setupScriptRun: true,
    })

    render(
      <LoadTeamDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={onSuccess}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('ai_controller_full_team')).toBeInTheDocument()
    })

    const teamButton = screen.getByText('ai_controller_full_team')
    await user.click(teamButton)

    const loadButton = screen.getByRole('button', { name: /load/i })
    await user.click(loadButton)

    await waitFor(() => {
      expect(loadTeam).toHaveBeenCalledWith('ai_controller_full_team')
      expect(onSuccess).toHaveBeenCalledWith('ai_controller_full_team')
    })
  })

  it('should close dialog on cancel', async () => {
    const user = userEvent.setup()
    const onOpenChange = vi.fn()

    render(
      <LoadTeamDialog
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={vi.fn()}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('ai_controller_full_team')).toBeInTheDocument()
    })

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('should handle fetch teams error', async () => {
    vi.mocked(listAvailableTeams).mockRejectedValueOnce(
      new Error('Failed to fetch')
    )

    render(
      <LoadTeamDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/failed to load teams/i)).toBeInTheDocument()
    })
  })

  it('should display empty state when no teams', async () => {
    vi.mocked(listAvailableTeams).mockResolvedValueOnce([])

    render(
      <LoadTeamDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/no teams found/i)).toBeInTheDocument()
    })
  })
})
