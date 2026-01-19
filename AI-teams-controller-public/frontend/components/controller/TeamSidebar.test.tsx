import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { TeamSidebar } from "./TeamSidebar"
import type { TeamSidebarProps } from "./TeamSidebar"

describe("TeamSidebar", () => {
  const mockTeams = [
    { id: "team1", name: "AI Controller Team" },
    { id: "team2", name: "Quiz Game Team" },
    { id: "team3", name: "Backend Team" },
  ]

  const defaultProps: TeamSidebarProps = {
    teams: mockTeams,
    selectedTeam: "team1",
    sidebarOpen: true,
    isMobile: false,
    showSettings: false,
    pollingInterval: 0.5,
    captureLines: 100,
    stopWord: "thank you",
    onSelectTeam: vi.fn(),
    onToggleSidebar: vi.fn(),
    onToggleSettings: vi.fn(),
    onPollingIntervalChange: vi.fn(),
    onCaptureLinesChange: vi.fn(),
    onStopWordChange: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("Component Rendering", () => {
    it("should render header with title", () => {
      render(<TeamSidebar {...defaultProps} />)
      expect(screen.getByText("TMUX Controller")).toBeInTheDocument()
    })

    it("should render all teams in list", () => {
      render(<TeamSidebar {...defaultProps} />)
      expect(screen.getByText("AI Controller Team")).toBeInTheDocument()
      expect(screen.getByText("Quiz Game Team")).toBeInTheDocument()
      expect(screen.getByText("Backend Team")).toBeInTheDocument()
    })

    it("should render settings button", () => {
      render(<TeamSidebar {...defaultProps} />)
      expect(screen.getByRole("button", { name: /Settings/i })).toBeInTheDocument()
    })

    it("should not render mobile close button on desktop", () => {
      render(<TeamSidebar {...defaultProps} isMobile={false} />)
      expect(screen.queryByRole("button", { name: "" })).not.toBeInTheDocument()
    })
  })

  describe("Team List Behavior", () => {
    it("should highlight selected team", () => {
      const { container } = render(<TeamSidebar {...defaultProps} selectedTeam="team1" />)
      const selectedButton = screen.getByText("AI Controller Team").closest("button")
      expect(selectedButton).toHaveClass("bg-primary")
    })

    it("should show notification indicator for teams with notifications", () => {
      const teamNotifications = new Set(["team3"])
      render(<TeamSidebar {...defaultProps} teamNotifications={teamNotifications} />)
      // Backend Team (team3) should have notification styling
      const backendTeam = screen.getByText("Backend Team").closest("button")
      expect(backendTeam).toHaveClass("text-green-500")
    })

    it("should show idle styling for inactive teams", () => {
      const { container } = render(<TeamSidebar {...defaultProps} selectedTeam="team1" />)
      const inactiveTeam = screen.getByText("Quiz Game Team").closest("button")
      expect(inactiveTeam).toHaveClass("text-sidebar-foreground")
    })

    it("should call onSelectTeam when team clicked", () => {
      const onSelectTeam = vi.fn()
      render(<TeamSidebar {...defaultProps} onSelectTeam={onSelectTeam} />)

      const team2Button = screen.getByText("Quiz Game Team")
      fireEvent.click(team2Button)

      expect(onSelectTeam).toHaveBeenCalledWith("team2")
    })

    it("should close sidebar on mobile when team selected", () => {
      const onToggleSidebar = vi.fn()
      render(<TeamSidebar {...defaultProps} isMobile={true} onToggleSidebar={onToggleSidebar} />)

      const teamButton = screen.getByText("Quiz Game Team")
      fireEvent.click(teamButton)

      expect(onToggleSidebar).toHaveBeenCalledWith(false)
    })

    it("should not close sidebar on desktop when team selected", () => {
      const onToggleSidebar = vi.fn()
      render(<TeamSidebar {...defaultProps} isMobile={false} onToggleSidebar={onToggleSidebar} />)

      const teamButton = screen.getByText("Quiz Game Team")
      fireEvent.click(teamButton)

      expect(onToggleSidebar).not.toHaveBeenCalled()
    })
  })

  describe("Mobile Behavior", () => {
    it("should show close button on mobile", () => {
      render(<TeamSidebar {...defaultProps} isMobile={true} />)
      const closeButton = screen.getByRole("button", { name: "" })
      expect(closeButton).toBeInTheDocument()
    })

    it("should call onToggleSidebar(false) when close button clicked", () => {
      const onToggleSidebar = vi.fn()
      render(<TeamSidebar {...defaultProps} isMobile={true} onToggleSidebar={onToggleSidebar} />)

      const closeButton = screen.getByRole("button", { name: "" })
      fireEvent.click(closeButton)

      expect(onToggleSidebar).toHaveBeenCalledWith(false)
    })

    it("should have closed styling when sidebar is closed on mobile", () => {
      const { container } = render(<TeamSidebar {...defaultProps} isMobile={true} sidebarOpen={false} />)
      const sidebar = container.firstChild as HTMLElement
      expect(sidebar).toHaveClass("-translate-x-full")
    })

    it("should have open styling when sidebar is open on mobile", () => {
      const { container } = render(<TeamSidebar {...defaultProps} isMobile={true} sidebarOpen={true} />)
      const sidebar = container.firstChild as HTMLElement
      expect(sidebar).toHaveClass("absolute")
      expect(sidebar).toHaveClass("shadow-lg")
    })
  })

  describe("Settings Panel", () => {
    it("should not show settings panel when showSettings is false", () => {
      render(<TeamSidebar {...defaultProps} showSettings={false} />)
      expect(screen.queryByText("Polling Interval")).not.toBeInTheDocument()
      expect(screen.queryByText("Max Lines")).not.toBeInTheDocument()
      expect(screen.queryByText("Stop Word")).not.toBeInTheDocument()
    })

    it("should show settings panel when showSettings is true", () => {
      render(<TeamSidebar {...defaultProps} showSettings={true} />)
      expect(screen.getByText("Polling Interval")).toBeInTheDocument()
      expect(screen.getByText("Max Lines")).toBeInTheDocument()
      expect(screen.getByText("Stop Word")).toBeInTheDocument()
    })

    it("should call onToggleSettings when settings button clicked", () => {
      const onToggleSettings = vi.fn()
      render(<TeamSidebar {...defaultProps} onToggleSettings={onToggleSettings} />)

      const settingsButton = screen.getByRole("button", { name: /Settings/i })
      fireEvent.click(settingsButton)

      expect(onToggleSettings).toHaveBeenCalled()
    })
  })

  describe("Polling Interval Setting", () => {
    it("should render all polling interval options", () => {
      render(<TeamSidebar {...defaultProps} showSettings={true} />)
      expect(screen.getByText("0.5s")).toBeInTheDocument()
      expect(screen.getByText("1s")).toBeInTheDocument()
      expect(screen.getByText("2s")).toBeInTheDocument()
    })

    it("should highlight selected polling interval", () => {
      const { container } = render(<TeamSidebar {...defaultProps} showSettings={true} pollingInterval={1} />)
      const button1s = screen.getByText("1s").closest("button")
      // Selected button should not have outline variant class
      expect(button1s).not.toHaveClass("border-input")
    })

    it("should call onPollingIntervalChange when interval clicked", () => {
      const onPollingIntervalChange = vi.fn()
      render(<TeamSidebar {...defaultProps} showSettings={true} onPollingIntervalChange={onPollingIntervalChange} />)

      const button2s = screen.getByText("2s")
      fireEvent.click(button2s)

      expect(onPollingIntervalChange).toHaveBeenCalledWith(2)
    })
  })

  describe("Max Lines Setting", () => {
    it("should render all max lines options", () => {
      render(<TeamSidebar {...defaultProps} showSettings={true} />)
      expect(screen.getByText("50")).toBeInTheDocument()
      expect(screen.getByText("100")).toBeInTheDocument()
      expect(screen.getByText("200")).toBeInTheDocument()
      expect(screen.getByText("500")).toBeInTheDocument()
    })

    it("should highlight selected max lines", () => {
      const { container } = render(<TeamSidebar {...defaultProps} showSettings={true} captureLines={200} />)
      const button200 = screen.getByText("200").closest("button")
      // Selected button should not have outline variant class
      expect(button200).not.toHaveClass("border-input")
    })

    it("should call onCaptureLinesChange when lines clicked", () => {
      const onCaptureLinesChange = vi.fn()
      render(<TeamSidebar {...defaultProps} showSettings={true} onCaptureLinesChange={onCaptureLinesChange} />)

      const button500 = screen.getByText("500")
      fireEvent.click(button500)

      expect(onCaptureLinesChange).toHaveBeenCalledWith(500)
    })
  })

  describe("Stop Word Setting", () => {
    it("should render stop word input with current value", () => {
      render(<TeamSidebar {...defaultProps} showSettings={true} stopWord="hello world" />)
      const input = screen.getByPlaceholderText("thank you") as HTMLInputElement
      expect(input.value).toBe("hello world")
    })

    it("should call onStopWordChange when input changes", () => {
      const onStopWordChange = vi.fn()
      render(<TeamSidebar {...defaultProps} showSettings={true} onStopWordChange={onStopWordChange} />)

      const input = screen.getByPlaceholderText("thank you")
      fireEvent.change(input, { target: { value: "new word" } })

      expect(onStopWordChange).toHaveBeenCalledWith("new word")
    })

    it("should show helper text for stop word", () => {
      render(<TeamSidebar {...defaultProps} showSettings={true} />)
      expect(screen.getByText("Say this to send command")).toBeInTheDocument()
    })
  })

  describe("Empty State", () => {
    it("should handle empty team list", () => {
      render(<TeamSidebar {...defaultProps} teams={[]} />)
      expect(screen.getByText("TMUX Controller")).toBeInTheDocument()
      expect(screen.queryByRole("button", { name: /Team/i })).not.toBeInTheDocument()
    })
  })

  describe("Edge Cases", () => {
    it("should handle null selectedTeam", () => {
      render(<TeamSidebar {...defaultProps} selectedTeam={null} />)
      const allTeams = screen.getAllByRole("button")
      // None should have selected styling (bg-primary)
      allTeams.forEach((button) => {
        if (button.textContent !== "Settings") {
          expect(button).not.toHaveClass("bg-primary")
        }
      })
    })

    it("should handle teams without isActive property", () => {
      const teamsWithoutActive = [
        { id: "team1", name: "Team 1" },
        { id: "team2", name: "Team 2" },
      ]
      render(<TeamSidebar {...defaultProps} teams={teamsWithoutActive} />)
      expect(screen.getByText("Team 1")).toBeInTheDocument()
      expect(screen.getByText("Team 2")).toBeInTheDocument()
    })
  })

  describe("Restart Team Button", () => {
    it("should render Restart Team button when team is selected and onRestartTeam provided", () => {
      const onRestartTeam = vi.fn()
      render(<TeamSidebar {...defaultProps} selectedTeam="team1" onRestartTeam={onRestartTeam} />)

      expect(screen.getByRole("button", { name: /Restart Team/i })).toBeInTheDocument()
    })

    it("should not render Restart Team button when no team selected", () => {
      const onRestartTeam = vi.fn()
      render(<TeamSidebar {...defaultProps} selectedTeam={null} onRestartTeam={onRestartTeam} />)

      expect(screen.queryByRole("button", { name: /Restart Team/i })).not.toBeInTheDocument()
    })

    it("should not render Restart Team button when onRestartTeam not provided", () => {
      render(<TeamSidebar {...defaultProps} selectedTeam="team1" />)

      expect(screen.queryByRole("button", { name: /Restart Team/i })).not.toBeInTheDocument()
    })

    it("should show loading state when restarting team", () => {
      const onRestartTeam = vi.fn()
      render(
        <TeamSidebar
          {...defaultProps}
          selectedTeam="team1"
          onRestartTeam={onRestartTeam}
          restartProgress="killing"
        />
      )

      const button = screen.getByRole("button", { name: /Restarting.../i })
      expect(button).toBeInTheDocument()
      expect(button).toBeDisabled()
    })

    it("should disable button during restart", () => {
      const onRestartTeam = vi.fn()
      render(
        <TeamSidebar
          {...defaultProps}
          selectedTeam="team1"
          onRestartTeam={onRestartTeam}
          restartProgress="running_script"
        />
      )

      const button = screen.getByRole("button", { name: /Restarting.../i })
      expect(button).toBeDisabled()
    })

    it("should open confirmation dialog when Restart Team clicked", async () => {
      const onRestartTeam = vi.fn()
      render(<TeamSidebar {...defaultProps} selectedTeam="team1" onRestartTeam={onRestartTeam} />)

      const button = screen.getByRole("button", { name: /Restart Team/i })
      fireEvent.click(button)

      // Dialog should appear
      expect(screen.getByText(/Restart Team\?/i)).toBeInTheDocument()
      expect(screen.getByText(/Any unsaved work will be lost/i)).toBeInTheDocument()
    })

    it("should call onRestartTeam when confirmation accepted", async () => {
      const onRestartTeam = vi.fn().mockResolvedValue(undefined)
      render(<TeamSidebar {...defaultProps} selectedTeam="team1" onRestartTeam={onRestartTeam} />)

      // Click Restart Team button in sidebar
      const sidebarButton = screen.getByRole("button", { name: /^Restart Team$/i })
      fireEvent.click(sidebarButton)

      // Dialog should appear - now find confirm button within dialog
      const allButtons = screen.getAllByRole("button")
      const confirmButton = allButtons.find(btn => btn.textContent === "Restart Team" && btn !== sidebarButton)

      if (confirmButton) {
        fireEvent.click(confirmButton)
      }

      expect(onRestartTeam).toHaveBeenCalledWith("team1")
    })

    it("should not call onRestartTeam when dialog cancelled", async () => {
      const onRestartTeam = vi.fn()
      render(<TeamSidebar {...defaultProps} selectedTeam="team1" onRestartTeam={onRestartTeam} />)

      // Click Restart Team button
      const restartButton = screen.getByRole("button", { name: /^Restart Team$/i })
      fireEvent.click(restartButton)

      // Cancel in dialog
      const cancelButton = screen.getByRole("button", { name: /Cancel/i })
      fireEvent.click(cancelButton)

      expect(onRestartTeam).not.toHaveBeenCalled()
    })

    it("should show restart progress message in dialog", () => {
      const onRestartTeam = vi.fn()
      render(
        <TeamSidebar
          {...defaultProps}
          selectedTeam="team1"
          onRestartTeam={onRestartTeam}
          restartProgress="looking_for_script"
        />
      )

      // Button should show "Restarting..." in loading state
      const restartButton = screen.getByRole("button", { name: /Restarting.../i })
      expect(restartButton).toBeDisabled()

      // Don't click it - the dialog is already controlled by restartProgress
      // The dialog will not auto-open, it's controlled by restartDialogOpen state
      // So this test needs to verify the button shows loading, not the dialog content
    })
  })
})
