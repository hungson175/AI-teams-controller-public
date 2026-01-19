import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { VoiceCommand } from './VoiceCommand'

// Mock the useVoiceRecorder hook
const mockStartRecording = vi.fn()
const mockStopRecording = vi.fn()
const mockClearTranscript = vi.fn()

vi.mock('@/hooks/useVoiceRecorder', () => ({
  useVoiceRecorder: () => mockUseVoiceRecorder(),
}))

// Mock the toast hook
const mockToast = vi.fn()
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: mockToast }),
}))

// Mock the useVoiceFeedback hook
const mockSetHandsFreeMode = vi.fn()

vi.mock('@/contexts/VoiceFeedbackContext', () => ({
  useVoiceFeedback: () => ({
    setHandsFreeMode: mockSetHandsFreeMode,
    notifications: [],
    unreadCount: 0,
    isPanelOpen: false,
    isConnected: false,
    isHandsFreeMode: false,
    connectWebSocket: vi.fn(),
    disconnectWebSocket: vi.fn(),
    togglePanel: vi.fn(),
    openPanel: vi.fn(),
    closePanel: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    playNotification: vi.fn(),
    clearNotifications: vi.fn(),
  }),
}))

// Default mock state
let mockState = {
  status: 'idle' as const,
  transcript: '',
  correctedCommand: '',
  error: null,
  isSpeaking: false,
  feedbackSummary: '',
  isPlayingFeedback: false,
}

const mockUseVoiceRecorder = () => ({
  state: mockState,
  isRecording: mockState.status === 'listening' || mockState.status === 'connecting',
  startRecording: mockStartRecording,
  stopRecording: mockStopRecording,
  clearTranscript: mockClearTranscript,
  canRecord: mockState.status === 'idle' || mockState.status === 'error' || mockState.status === 'speaking',
  canClear: mockState.transcript.length > 0 &&
    mockState.status !== 'processing' &&
    mockState.status !== 'correcting' &&
    mockState.status !== 'sent',
})

describe('VoiceCommand', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSetHandsFreeMode.mockClear()
    mockClearTranscript.mockClear()
    mockToast.mockClear()
    mockState = {
      status: 'idle',
      transcript: '',
      correctedCommand: '',
      error: null,
      isSpeaking: false,
      feedbackSummary: '',
      isPlayingFeedback: false,
    }
  })

  describe('rendering', () => {
    it('should render mic button', () => {
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
    })

    it('should show "Hands-free mode OFF" when idle', () => {
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Hands-free mode OFF')).toBeInTheDocument()
    })

    it('should disable button when teamId is null', () => {
      render(<VoiceCommand teamId={null} roleId="role1" />)
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
    })

    it('should disable button when roleId is null', () => {
      render(<VoiceCommand teamId="team1" roleId={null} />)
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
    })
  })

  describe('status display', () => {
    it('should show "Connecting..." when connecting', () => {
      mockState = { ...mockState, status: 'connecting' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Connecting...')).toBeInTheDocument()
    })

    it('should show "Hands-free ON - speak anytime" when listening but not speaking', () => {
      mockState = { ...mockState, status: 'listening', isSpeaking: false }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Hands-free ON - speak anytime')).toBeInTheDocument()
    })

    it('should show "Listening..." when listening and speaking', () => {
      mockState = { ...mockState, status: 'listening', isSpeaking: true }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Listening...')).toBeInTheDocument()
    })

    it('should show "Sending command..." when processing', () => {
      mockState = { ...mockState, status: 'processing' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Sending command...')).toBeInTheDocument()
    })

    it('should show "Correcting..." when correcting', () => {
      mockState = { ...mockState, status: 'correcting' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Correcting...')).toBeInTheDocument()
    })

    it('should show "Command sent! Still listening..." when sent', () => {
      mockState = { ...mockState, status: 'sent' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Command sent! Still listening...')).toBeInTheDocument()
    })

    it('should show "Speaking..." when speaking feedback', () => {
      mockState = { ...mockState, status: 'speaking' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Speaking...')).toBeInTheDocument()
    })

    it('should show error message when in error state', () => {
      mockState = { ...mockState, status: 'error', error: 'Connection failed' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Connection failed')).toBeInTheDocument()
    })
  })

  describe('transcript display', () => {
    it('should show transcript when available', () => {
      mockState = { ...mockState, transcript: 'fix the bug' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('fix the bug')).toBeInTheDocument()
    })

    it('should not show transcript section when empty', () => {
      mockState = { ...mockState, transcript: '' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.queryByText('fix the bug')).not.toBeInTheDocument()
    })
  })

  describe('corrected command display', () => {
    it('should show corrected command when available', () => {
      mockState = { ...mockState, correctedCommand: 'Fix the authentication bug' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Fix the authentication bug')).toBeInTheDocument()
    })
  })

  describe('feedback summary display', () => {
    it('should show feedback summary when speaking', () => {
      mockState = {
        ...mockState,
        status: 'speaking',
        feedbackSummary: 'Done. Fixed the bug.'
      }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Done. Fixed the bug.')).toBeInTheDocument()
    })

    it('should not show feedback summary when not speaking', () => {
      mockState = {
        ...mockState,
        status: 'idle',
        feedbackSummary: 'Done. Fixed the bug.'
      }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.queryByText('Done. Fixed the bug.')).not.toBeInTheDocument()
    })
  })

  describe('hands-free hint', () => {
    it('should show hands-free hint when listening and not speaking', () => {
      mockState = { ...mockState, status: 'listening', isSpeaking: false }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByText('Pause 5s after speaking to auto-send • Click mic to stop')).toBeInTheDocument()
    })

    it('should not show hands-free hint when listening and speaking', () => {
      mockState = { ...mockState, status: 'listening', isSpeaking: true }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.queryByText('Pause 5s after speaking to auto-send • Click mic to stop')).not.toBeInTheDocument()
    })

    it('should not show hands-free hint when idle', () => {
      mockState = { ...mockState, status: 'idle' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.queryByText('Pause 5s after speaking to auto-send • Click mic to stop')).not.toBeInTheDocument()
    })
  })

  describe('button interactions', () => {
    it('should call startRecording when clicked in idle state', async () => {
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      const button = screen.getByRole('button')
      fireEvent.click(button)
      expect(mockStartRecording).toHaveBeenCalledWith('team1', 'role1')
    })

    it('should call stopRecording when clicked while recording', () => {
      mockState = { ...mockState, status: 'listening' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      const button = screen.getByRole('button')
      fireEvent.click(button)
      expect(mockStopRecording).toHaveBeenCalled()
    })

    it('should not call any function when disabled', () => {
      render(<VoiceCommand teamId={null} roleId="role1" />)
      const button = screen.getByRole('button')
      fireEvent.click(button)
      expect(mockStartRecording).not.toHaveBeenCalled()
      expect(mockStopRecording).not.toHaveBeenCalled()
    })
  })

  describe('VAD indicator', () => {
    it('should show VAD indicator when recording', () => {
      mockState = { ...mockState, status: 'listening' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      // VAD indicator is a div with specific classes
      const vadIndicator = document.querySelector('[title="Waiting for speech"]')
      expect(vadIndicator).toBeInTheDocument()
    })

    it('should show VAD indicator when speaking feedback', () => {
      mockState = { ...mockState, status: 'speaking' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      const vadIndicator = document.querySelector('[title="Playing feedback"]')
      expect(vadIndicator).toBeInTheDocument()
    })

    it('should not show VAD indicator when idle', () => {
      mockState = { ...mockState, status: 'idle' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      const vadIndicator = document.querySelector('[title="Waiting for speech"]')
      expect(vadIndicator).not.toBeInTheDocument()
    })
  })

  describe('clear button', () => {
    it('should show clear button when transcript exists', () => {
      mockState = { ...mockState, transcript: 'fix the bug' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByLabelText('Clear recording')).toBeInTheDocument()
    })

    it('should hide clear button when no transcript', () => {
      mockState = { ...mockState, transcript: '' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.queryByLabelText('Clear recording')).not.toBeInTheDocument()
    })

    it('should hide clear button when processing', () => {
      mockState = { ...mockState, transcript: 'fix the bug', status: 'processing' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.queryByLabelText('Clear recording')).not.toBeInTheDocument()
    })

    it('should hide clear button when correcting', () => {
      mockState = { ...mockState, transcript: 'fix the bug', status: 'correcting' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.queryByLabelText('Clear recording')).not.toBeInTheDocument()
    })

    it('should hide clear button when sent', () => {
      mockState = { ...mockState, transcript: 'fix the bug', status: 'sent' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.queryByLabelText('Clear recording')).not.toBeInTheDocument()
    })

    it('should call clearTranscript when clicked', () => {
      mockState = { ...mockState, transcript: 'fix the bug' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      const clearButton = screen.getByLabelText('Clear recording')
      fireEvent.click(clearButton)
      expect(mockClearTranscript).toHaveBeenCalled()
    })

    it('should show toast when clearing', () => {
      mockState = { ...mockState, transcript: 'fix the bug' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      const clearButton = screen.getByLabelText('Clear recording')
      fireEvent.click(clearButton)
      expect(mockToast).toHaveBeenCalledWith({
        description: 'Recording cleared',
        duration: 1500,
      })
    })

    it('should show clear button when listening with transcript', () => {
      mockState = { ...mockState, transcript: 'fix the bug', status: 'listening' }
      render(<VoiceCommand teamId="team1" roleId="role1" />)
      expect(screen.getByLabelText('Clear recording')).toBeInTheDocument()
    })
  })
})
