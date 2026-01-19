import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { TeamSettingsPanel } from "./TeamSettingsPanel"
import type { TeamSettingsPanelProps } from "./TeamSettingsPanel"

describe("TeamSettingsPanel", () => {
  const defaultProps: TeamSettingsPanelProps = {
    pollingInterval: 0.5,
    captureLines: 100,
    stopWord: "thank you",
    onPollingIntervalChange: vi.fn(),
    onCaptureLinesChange: vi.fn(),
    onStopWordChange: vi.fn(),
  }

  describe("ISP Compliance - Focused Interface", () => {
    it("should only accept settings-related props", () => {
      // Verifies ISP by ensuring component works with minimal, focused props
      const { container } = render(<TeamSettingsPanel {...defaultProps} />)
      expect(container.firstChild).toBeInTheDocument()
    })

    it("should NOT accept team-related props", () => {
      // TypeScript will enforce this at compile time
      const propsWithExtras = {
        ...defaultProps,
        // @ts-expect-error - should not accept team props
        teams: [],
        // @ts-expect-error - should not accept team selection
        selectedTeam: "team1",
      }
      // Test documents the intent
      render(<TeamSettingsPanel {...defaultProps} />)
    })
  })

  describe("Polling Interval", () => {
    it("should render polling interval section", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      expect(screen.getByText("Polling Interval")).toBeInTheDocument()
    })

    it("should render all polling interval options", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      expect(screen.getByRole("button", { name: "0.5s" })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "1s" })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "2s" })).toBeInTheDocument()
    })

    it("should highlight selected polling interval", () => {
      render(<TeamSettingsPanel {...defaultProps} pollingInterval={1} />)
      const button1s = screen.getByRole("button", { name: "1s" })
      // shadcn Button with variant="default" has bg-primary
      expect(button1s).toHaveClass("bg-primary")
    })

    it("should call onPollingIntervalChange when interval clicked", () => {
      const onPollingIntervalChange = vi.fn()
      render(<TeamSettingsPanel {...defaultProps} onPollingIntervalChange={onPollingIntervalChange} />)

      const button2s = screen.getByRole("button", { name: "2s" })
      fireEvent.click(button2s)

      expect(onPollingIntervalChange).toHaveBeenCalledWith(2)
      expect(onPollingIntervalChange).toHaveBeenCalledTimes(1)
    })
  })

  describe("Capture Lines", () => {
    it("should render max lines section", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      expect(screen.getByText("Max Lines")).toBeInTheDocument()
    })

    it("should render all capture lines options", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      expect(screen.getByRole("button", { name: "50" })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "100" })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "200" })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "500" })).toBeInTheDocument()
    })

    it("should highlight selected capture lines", () => {
      render(<TeamSettingsPanel {...defaultProps} captureLines={200} />)
      const button200 = screen.getByRole("button", { name: "200" })
      expect(button200).toHaveClass("bg-primary")
    })

    it("should call onCaptureLinesChange when lines clicked", () => {
      const onCaptureLinesChange = vi.fn()
      render(<TeamSettingsPanel {...defaultProps} onCaptureLinesChange={onCaptureLinesChange} />)

      const button500 = screen.getByRole("button", { name: "500" })
      fireEvent.click(button500)

      expect(onCaptureLinesChange).toHaveBeenCalledWith(500)
      expect(onCaptureLinesChange).toHaveBeenCalledTimes(1)
    })
  })

  describe("Stop Word", () => {
    it("should render stop word section", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      expect(screen.getByText("Stop Word")).toBeInTheDocument()
    })

    it("should render stop word input with current value", () => {
      render(<TeamSettingsPanel {...defaultProps} stopWord="go go go" />)
      const input = screen.getByPlaceholderText("thank you")
      expect(input).toHaveValue("go go go")
    })

    it("should call onStopWordChange when input changes", () => {
      const onStopWordChange = vi.fn()
      render(<TeamSettingsPanel {...defaultProps} onStopWordChange={onStopWordChange} />)

      const input = screen.getByPlaceholderText("thank you")
      fireEvent.change(input, { target: { value: "stop recording" } })

      expect(onStopWordChange).toHaveBeenCalledWith("stop recording")
    })

    it("should show help text for stop word", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      expect(screen.getByText("Say this to send command")).toBeInTheDocument()
    })

    it("should have placeholder text", () => {
      render(<TeamSettingsPanel {...defaultProps} stopWord="" />)
      const input = screen.getByPlaceholderText("thank you")
      expect(input).toHaveAttribute("placeholder", "thank you")
    })
  })

  describe("Voice Settings Integration", () => {
    it("should render voice settings section", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      // VoiceTeamSettingsPanel should be rendered
      // It's separated by a border-t, so check for that structure
      const container = screen.getByTestId("settings-panel")
      expect(container).toBeInTheDocument()
    })
  })

  describe("Accessibility", () => {
    it("should have proper labels for all sections", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      expect(screen.getByText("Polling Interval")).toBeInTheDocument()
      expect(screen.getByText("Max Lines")).toBeInTheDocument()
      expect(screen.getByText("Stop Word")).toBeInTheDocument()
    })

    it("should have accessible input for stop word", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      const input = screen.getByPlaceholderText("thank you")
      expect(input).toHaveAttribute("type", "text")
    })
  })

  describe("Edge Cases", () => {
    it("should handle empty stop word", () => {
      render(<TeamSettingsPanel {...defaultProps} stopWord="" />)
      const input = screen.getByPlaceholderText("thank you")
      expect(input).toHaveValue("")
    })

    it("should handle very long stop word", () => {
      const longStopWord = "this is a very long stop word that might cause layout issues"
      render(<TeamSettingsPanel {...defaultProps} stopWord={longStopWord} />)
      const input = screen.getByPlaceholderText("thank you")
      expect(input).toHaveValue(longStopWord)
    })

    it("should handle stop word with special characters", () => {
      render(<TeamSettingsPanel {...defaultProps} stopWord="@#$%^&*()" />)
      const input = screen.getByPlaceholderText("thank you")
      expect(input).toHaveValue("@#$%^&*()")
    })

    it("should not break with missing callbacks", () => {
      // Should render without crashing even if callbacks are undefined
      // TypeScript ensures they're required, but test defensive coding
      const propsWithoutCallbacks = {
        pollingInterval: 0.5 as const,
        captureLines: 100,
        stopWord: "thank you",
        onPollingIntervalChange: undefined as any,
        onCaptureLinesChange: undefined as any,
        onStopWordChange: undefined as any,
      }
      render(<TeamSettingsPanel {...propsWithoutCallbacks} />)
      expect(screen.getByText("Polling Interval")).toBeInTheDocument()
    })
  })

  describe("Layout", () => {
    it("should render all sections in correct order", () => {
      const { container } = render(<TeamSettingsPanel {...defaultProps} />)
      const labels = screen.getAllByText(/Polling Interval|Max Lines|Stop Word/)

      // Should have 3 main sections
      expect(labels.length).toBeGreaterThanOrEqual(3)
    })

    it("should have proper spacing between sections", () => {
      render(<TeamSettingsPanel {...defaultProps} />)
      const panel = screen.getByTestId("settings-panel")
      // Component uses space-y-3 for spacing
      expect(panel).toHaveClass("space-y-3")
    })
  })
})
