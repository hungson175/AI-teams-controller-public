import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { VoiceInputToggle } from "./VoiceInputToggle"
import type { VoiceState } from "@/lib/voice-types"

describe("VoiceInputToggle", () => {
  const defaultVoiceState: VoiceState = {
    status: "idle",
    transcript: "",
    correctedCommand: "",
    error: null,
    isSpeaking: false,
    feedbackSummary: "",
    isPlayingFeedback: false,
  }

  const defaultProps = {
    teamId: "team1",
    roleId: "PM",
    voiceState: defaultVoiceState,
    isRecording: false,
    startRecording: vi.fn(),
    stopRecording: vi.fn(),
    canRecord: true,
    onTranscriptChange: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("Basic Rendering", () => {
    it("should render the voice input button", () => {
      render(<VoiceInputToggle {...defaultProps} />)
      expect(screen.getByRole("button")).toBeInTheDocument()
    })

    it("should show 'Voice Input' text when not recording", () => {
      render(<VoiceInputToggle {...defaultProps} />)
      expect(screen.getByText("Voice Input")).toBeInTheDocument()
    })

    it("should show 'Stop' text when recording", () => {
      render(<VoiceInputToggle {...defaultProps} isRecording={true} />)
      expect(screen.getByText("Stop")).toBeInTheDocument()
    })

    it("should show 'Connecting...' when status is connecting", () => {
      const connectingState = { ...defaultVoiceState, status: "connecting" as const }
      render(<VoiceInputToggle {...defaultProps} voiceState={connectingState} />)
      expect(screen.getByText("Connecting...")).toBeInTheDocument()
    })
  })

  describe("Button Interactions", () => {
    it("should call startRecording when clicked while not recording", async () => {
      const startRecording = vi.fn()
      render(<VoiceInputToggle {...defaultProps} startRecording={startRecording} />)

      fireEvent.click(screen.getByRole("button"))

      expect(startRecording).toHaveBeenCalledWith("team1", "PM")
    })

    it("should call stopRecording when clicked while recording", () => {
      const stopRecording = vi.fn()
      render(<VoiceInputToggle {...defaultProps} isRecording={true} stopRecording={stopRecording} />)

      fireEvent.click(screen.getByRole("button"))

      expect(stopRecording).toHaveBeenCalled()
    })

    it("should be disabled when teamId is null", () => {
      render(<VoiceInputToggle {...defaultProps} teamId={null} />)
      expect(screen.getByRole("button")).toBeDisabled()
    })

    it("should be disabled when roleId is null", () => {
      render(<VoiceInputToggle {...defaultProps} roleId={null} />)
      expect(screen.getByRole("button")).toBeDisabled()
    })

    it("should be disabled when canRecord is false and not recording", () => {
      render(<VoiceInputToggle {...defaultProps} canRecord={false} />)
      expect(screen.getByRole("button")).toBeDisabled()
    })

    it("should NOT be disabled when recording (even if canRecord is false)", () => {
      render(<VoiceInputToggle {...defaultProps} isRecording={true} canRecord={false} />)
      expect(screen.getByRole("button")).not.toBeDisabled()
    })
  })

  describe("Auto-stop on Project Switch", () => {
    it("should NOT stop recording when team remains the same", () => {
      const stopRecording = vi.fn()
      const { rerender } = render(
        <VoiceInputToggle {...defaultProps} isRecording={true} teamId="team1" stopRecording={stopRecording} />
      )

      // Re-render with same team (simulating other prop changes)
      rerender(
        <VoiceInputToggle {...defaultProps} isRecording={true} teamId="team1" stopRecording={stopRecording} />
      )

      expect(stopRecording).not.toHaveBeenCalled()
    })

    it("should stop recording when team changes", () => {
      const stopRecording = vi.fn()
      const { rerender } = render(
        <VoiceInputToggle {...defaultProps} isRecording={true} teamId="team1" stopRecording={stopRecording} />
      )

      // Switch to different team
      rerender(
        <VoiceInputToggle {...defaultProps} isRecording={true} teamId="team2" stopRecording={stopRecording} />
      )

      expect(stopRecording).toHaveBeenCalled()
    })

    it("should NOT stop when team changes but NOT recording", () => {
      const stopRecording = vi.fn()
      const { rerender } = render(
        <VoiceInputToggle {...defaultProps} isRecording={false} teamId="team1" stopRecording={stopRecording} />
      )

      // Switch to different team while not recording
      rerender(
        <VoiceInputToggle {...defaultProps} isRecording={false} teamId="team2" stopRecording={stopRecording} />
      )

      expect(stopRecording).not.toHaveBeenCalled()
    })

    it("should allow role change within same project without stopping", () => {
      const stopRecording = vi.fn()
      const { rerender } = render(
        <VoiceInputToggle {...defaultProps} isRecording={true} teamId="team1" roleId="PM" stopRecording={stopRecording} />
      )

      // Switch role within same team (same project, different tab)
      rerender(
        <VoiceInputToggle {...defaultProps} isRecording={true} teamId="team1" roleId="FE" stopRecording={stopRecording} />
      )

      // Should NOT stop - same project, just different tab
      expect(stopRecording).not.toHaveBeenCalled()
    })
  })

  describe("Accessibility", () => {
    it("should have correct aria-label when not recording", () => {
      render(<VoiceInputToggle {...defaultProps} />)
      expect(screen.getByLabelText("Start voice recording")).toBeInTheDocument()
    })

    it("should have correct aria-label when recording", () => {
      render(<VoiceInputToggle {...defaultProps} isRecording={true} />)
      expect(screen.getByLabelText("Stop voice recording")).toBeInTheDocument()
    })

    it("should have aria-pressed=false when not recording", () => {
      render(<VoiceInputToggle {...defaultProps} />)
      expect(screen.getByRole("button")).toHaveAttribute("aria-pressed", "false")
    })

    it("should have aria-pressed=true when recording", () => {
      render(<VoiceInputToggle {...defaultProps} isRecording={true} />)
      expect(screen.getByRole("button")).toHaveAttribute("aria-pressed", "true")
    })
  })
})
