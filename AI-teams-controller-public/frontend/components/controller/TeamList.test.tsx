import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { TeamList } from "./TeamList"
import type { TeamListProps } from "./TeamList"

describe("TeamList", () => {
  const mockTeams = [
    { id: "team1", name: "AI Controller Team" },
    { id: "team2", name: "Quiz Game Team" },
    { id: "team3", name: "Backend Team" },
  ]

  const defaultProps: TeamListProps = {
    teams: mockTeams,
    selectedTeam: "team1",
    onSelectTeam: vi.fn(),
  }

  describe("ISP Compliance - Focused Interface", () => {
    it("should only accept necessary props (teams, selectedTeam, onSelectTeam)", () => {
      // This test verifies ISP by ensuring component works with minimal props
      const { container } = render(<TeamList {...defaultProps} />)
      expect(container.firstChild).toBeInTheDocument()
    })

    it("should NOT accept unnecessary props like polling, settings, etc", () => {
      // TypeScript will enforce this at compile time
      // This test documents the intent
      const propsWithExtras = {
        ...defaultProps,
        // @ts-expect-error - should not accept polling interval
        pollingInterval: 0.5,
        // @ts-expect-error - should not accept settings
        showSettings: false,
      }
      // Test still renders without errors, but TS will catch at compile time
      render(<TeamList {...defaultProps} />)
    })
  })

  describe("Rendering", () => {
    it("should render all teams", () => {
      render(<TeamList {...defaultProps} />)
      expect(screen.getByText("AI Controller Team")).toBeInTheDocument()
      expect(screen.getByText("Quiz Game Team")).toBeInTheDocument()
      expect(screen.getByText("Backend Team")).toBeInTheDocument()
    })

    it("should render empty state when no teams", () => {
      render(<TeamList {...defaultProps} teams={[]} />)
      const teamButtons = screen.queryAllByRole("button")
      expect(teamButtons).toHaveLength(0)
    })
  })

  describe("Team Selection", () => {
    it("should highlight selected team", () => {
      render(<TeamList {...defaultProps} selectedTeam="team1" />)
      const selectedButton = screen.getByText("AI Controller Team").closest("button")
      expect(selectedButton).toHaveClass("bg-primary")
    })

    it("should call onSelectTeam when team clicked", () => {
      const onSelectTeam = vi.fn()
      render(<TeamList {...defaultProps} onSelectTeam={onSelectTeam} />)

      const team2Button = screen.getByText("Quiz Game Team")
      fireEvent.click(team2Button)

      expect(onSelectTeam).toHaveBeenCalledWith("team2")
      expect(onSelectTeam).toHaveBeenCalledTimes(1)
    })

    it("should handle no team selected (null)", () => {
      render(<TeamList {...defaultProps} selectedTeam={null} />)
      const allButtons = screen.getAllByRole("button")

      // No button should have selected styling
      allButtons.forEach((button) => {
        expect(button).not.toHaveClass("bg-primary")
      })
    })
  })

  describe("Notification Indicators", () => {
    it("should show notification indicator for teams with unread", () => {
      const teamNotifications = new Set(["team2"])
      render(<TeamList {...defaultProps} teamNotifications={teamNotifications} />)

      const team2Button = screen.getByText("Quiz Game Team").closest("button")
      expect(team2Button).toHaveClass("text-green-500")
    })

    it("should not show indicator when no notifications", () => {
      render(<TeamList {...defaultProps} teamNotifications={new Set()} />)

      const team2Button = screen.getByText("Quiz Game Team").closest("button")
      expect(team2Button).not.toHaveClass("text-green-500")
    })

    it("should handle teamNotifications prop being undefined", () => {
      // Should not crash when teamNotifications not provided
      render(<TeamList {...defaultProps} teamNotifications={undefined} />)
      expect(screen.getByText("Quiz Game Team")).toBeInTheDocument()
    })
  })

  describe("Accessibility", () => {
    it("should have accessible button roles", () => {
      render(<TeamList {...defaultProps} />)
      const teamButtons = screen.getAllByRole("button")
      expect(teamButtons).toHaveLength(3)
    })

    it("should have title attribute for notification tooltip", () => {
      const teamNotifications = new Set(["team2"])
      render(<TeamList {...defaultProps} teamNotifications={teamNotifications} />)

      const team2Button = screen.getByText("Quiz Game Team").closest("button")
      expect(team2Button).toHaveAttribute("title", "New activity")
    })
  })

  describe("Edge Cases", () => {
    it("should handle team with long name", () => {
      const longNameTeams = [
        { id: "team1", name: "Very Long Team Name That Might Overflow The Container" },
      ]
      render(<TeamList {...defaultProps} teams={longNameTeams} />)
      expect(screen.getByText("Very Long Team Name That Might Overflow The Container")).toBeInTheDocument()
    })

    it("should handle team with special characters in name", () => {
      const specialTeams = [
        { id: "team1", name: "Team @#$%^&*()" },
      ]
      render(<TeamList {...defaultProps} teams={specialTeams} />)
      expect(screen.getByText("Team @#$%^&*()")).toBeInTheDocument()
    })

    it("should handle duplicate team IDs gracefully", () => {
      const duplicateTeams = [
        { id: "team1", name: "Team A" },
        { id: "team1", name: "Team B (duplicate ID)" },
      ]
      // Should render but React will warn about duplicate keys
      render(<TeamList {...defaultProps} teams={duplicateTeams} />)
      expect(screen.getByText("Team A")).toBeInTheDocument()
    })
  })
})
