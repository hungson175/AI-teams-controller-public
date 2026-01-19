import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { VoiceOverlay } from "./VoiceOverlay"
import type { VoiceOverlayProps } from "./VoiceOverlay"

// Mock the voice components
vi.mock("@/components/voice/VoiceInputToggle", () => ({
  VoiceInputToggle: ({ teamId, roleId, onTranscriptChange }: any) => (
    <div data-testid="voice-input-toggle" data-team={teamId} data-role={roleId}>
      Voice Input Toggle
    </div>
  ),
}))

vi.mock("@/components/voice/VoiceOutputToggle", () => ({
  VoiceOutputToggle: () => <div data-testid="voice-output-toggle">Voice Output Toggle</div>,
}))

describe("VoiceOverlay", () => {
  const defaultVoiceState = {
    status: "idle" as const,
    transcript: "",
    correctedCommand: "",
    error: null,
    isSpeaking: false,
    feedbackSummary: "",
    isPlayingFeedback: false,
  }

  const defaultProps: VoiceOverlayProps = {
    unreadCount: 0,
    isFeedbackConnected: true,
    selectedTeam: "team1",
    selectedRole: "PM",
    onTogglePanel: vi.fn(),
    onTranscriptChange: vi.fn(),
    voiceState: defaultVoiceState,
    isRecording: false,
    startRecording: vi.fn(),
    stopRecording: vi.fn(),
    canRecord: true,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("Component Rendering", () => {
    it("should render all voice components", () => {
      render(<VoiceOverlay {...defaultProps} />)

      expect(screen.getByTestId("voice-input-toggle")).toBeInTheDocument()
      expect(screen.getByTestId("voice-output-toggle")).toBeInTheDocument()
      expect(screen.getByLabelText("Voice notifications")).toBeInTheDocument()
    })

    it("should pass correct props to VoiceInputToggle", () => {
      render(<VoiceOverlay {...defaultProps} />)

      const voiceInput = screen.getByTestId("voice-input-toggle")
      expect(voiceInput).toHaveAttribute("data-team", "team1")
      expect(voiceInput).toHaveAttribute("data-role", "PM")
    })
  })

  describe("Unread Count Badge", () => {
    it("should hide badge when unreadCount is 0", () => {
      render(<VoiceOverlay {...defaultProps} unreadCount={0} />)
      expect(screen.queryByText(/\d+/)).not.toBeInTheDocument()
    })

    it("should show badge when unreadCount is greater than 0", () => {
      render(<VoiceOverlay {...defaultProps} unreadCount={5} />)
      expect(screen.getByText("5")).toBeInTheDocument()
    })

    it("should show '99+' when unreadCount exceeds 99", () => {
      render(<VoiceOverlay {...defaultProps} unreadCount={150} />)
      expect(screen.getByText("99+")).toBeInTheDocument()
    })

    it("should show exact count when unreadCount is 99", () => {
      render(<VoiceOverlay {...defaultProps} unreadCount={99} />)
      expect(screen.getByText("99")).toBeInTheDocument()
    })

    it("should show exact count when unreadCount is less than 99", () => {
      render(<VoiceOverlay {...defaultProps} unreadCount={42} />)
      expect(screen.getByText("42")).toBeInTheDocument()
    })
  })

  describe("Connection Status Indicator", () => {
    it("should show green indicator when connected", () => {
      const { container } = render(<VoiceOverlay {...defaultProps} isFeedbackConnected={true} />)
      const indicator = container.querySelector(".bg-green-500")
      expect(indicator).toBeInTheDocument()
    })

    it("should show yellow pulsing indicator when disconnected", () => {
      const { container } = render(<VoiceOverlay {...defaultProps} isFeedbackConnected={false} />)
      const indicator = container.querySelector(".bg-yellow-500")
      expect(indicator).toBeInTheDocument()
      expect(indicator).toHaveClass("animate-pulse")
    })

    it("should not show green when disconnected", () => {
      const { container } = render(<VoiceOverlay {...defaultProps} isFeedbackConnected={false} />)
      const greenIndicator = container.querySelector(".bg-green-500")
      expect(greenIndicator).not.toBeInTheDocument()
    })

    it("should not show yellow when connected", () => {
      const { container } = render(<VoiceOverlay {...defaultProps} isFeedbackConnected={true} />)
      const yellowIndicator = container.querySelector(".bg-yellow-500")
      expect(yellowIndicator).not.toBeInTheDocument()
    })
  })

  describe("Voice Feedback Button Interactions", () => {
    it("should call onTogglePanel when feedback button clicked", () => {
      const onTogglePanel = vi.fn()
      render(<VoiceOverlay {...defaultProps} onTogglePanel={onTogglePanel} />)

      const button = screen.getByLabelText("Voice notifications")
      fireEvent.click(button)

      expect(onTogglePanel).toHaveBeenCalledOnce()
    })

    it("should not call onTogglePanel on initial render", () => {
      const onTogglePanel = vi.fn()
      render(<VoiceOverlay {...defaultProps} onTogglePanel={onTogglePanel} />)

      expect(onTogglePanel).not.toHaveBeenCalled()
    })
  })

  describe("Accessibility", () => {
    it("should have aria-label without unread count when count is 0", () => {
      render(<VoiceOverlay {...defaultProps} unreadCount={0} />)
      expect(screen.getByLabelText("Voice notifications")).toBeInTheDocument()
    })

    it("should have aria-label with unread count when count is greater than 0", () => {
      render(<VoiceOverlay {...defaultProps} unreadCount={5} />)
      expect(screen.getByLabelText("Voice notifications (5 unread)")).toBeInTheDocument()
    })

    it("should have aria-label with large unread count", () => {
      render(<VoiceOverlay {...defaultProps} unreadCount={150} />)
      expect(screen.getByLabelText("Voice notifications (150 unread)")).toBeInTheDocument()
    })
  })

  describe("Edge Cases", () => {
    it("should handle null selectedTeam", () => {
      render(<VoiceOverlay {...defaultProps} selectedTeam={null} />)
      const voiceInput = screen.getByTestId("voice-input-toggle")
      expect(voiceInput).toBeInTheDocument()
    })

    it("should handle null selectedRole", () => {
      render(<VoiceOverlay {...defaultProps} selectedRole={null} />)
      const voiceInput = screen.getByTestId("voice-input-toggle")
      expect(voiceInput).toBeInTheDocument()
    })

    it("should handle both team and role being null", () => {
      render(<VoiceOverlay {...defaultProps} selectedTeam={null} selectedRole={null} />)

      const voiceInput = screen.getByTestId("voice-input-toggle")
      expect(voiceInput).toBeInTheDocument()
      expect(screen.getByTestId("voice-output-toggle")).toBeInTheDocument()
    })
  })

  describe("Recording Target Indicator", () => {
    it("should NOT show recording indicator when not recording", () => {
      render(<VoiceOverlay {...defaultProps} isRecording={false} />)
      expect(screen.queryByTestId("recording-target-indicator")).not.toBeInTheDocument()
    })

    it("should show recording indicator when isRecording is true", () => {
      render(<VoiceOverlay {...defaultProps} isRecording={true} selectedTeam="ai_controller_full_team" selectedRole="PM" />)
      expect(screen.getByTestId("recording-target-indicator")).toBeInTheDocument()
    })

    it("should display team name in recording indicator", () => {
      render(<VoiceOverlay {...defaultProps} isRecording={true} selectedTeam="ai_controller_full_team" selectedRole="PM" />)
      expect(screen.getByText(/ai_controller_full_team/)).toBeInTheDocument()
    })

    it("should display role name in recording indicator", () => {
      render(<VoiceOverlay {...defaultProps} isRecording={true} selectedTeam="team1" selectedRole="FE" />)
      expect(screen.getByText(/FE/)).toBeInTheDocument()
    })

    it("should show both team and role in indicator", () => {
      render(<VoiceOverlay {...defaultProps} isRecording={true} selectedTeam="my_project" selectedRole="BE" />)
      const indicator = screen.getByTestId("recording-target-indicator")
      expect(indicator).toHaveTextContent("my_project")
      expect(indicator).toHaveTextContent("BE")
    })

    it("should hide indicator when recording stops", () => {
      const { rerender } = render(<VoiceOverlay {...defaultProps} isRecording={true} selectedTeam="team1" selectedRole="PM" />)
      expect(screen.getByTestId("recording-target-indicator")).toBeInTheDocument()

      rerender(<VoiceOverlay {...defaultProps} isRecording={false} selectedTeam="team1" selectedRole="PM" />)
      expect(screen.queryByTestId("recording-target-indicator")).not.toBeInTheDocument()
    })

    it("should have accessible label for recording indicator", () => {
      render(<VoiceOverlay {...defaultProps} isRecording={true} selectedTeam="team1" selectedRole="PM" />)
      expect(screen.getByLabelText(/recording to/i)).toBeInTheDocument()
    })
  })
})
