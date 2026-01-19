/**
 * FileMatchPopup Component Tests (Sprint 14 - Work Item #3)
 *
 * TDD: Tests written FIRST per Boss requirement
 */

import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import { userEvent } from "@testing-library/user-event"
import { FileMatchPopup } from "./FileMatchPopup"

describe("FileMatchPopup", () => {
  const mockMatches = [
    "src/components/Button.tsx",
    "docs/examples/Button.tsx",
    "test/__mocks__/Button.tsx",
  ]

  it("should render when open", () => {
    render(
      <FileMatchPopup
        isOpen={true}
        onClose={vi.fn()}
        matches={mockMatches}
        onSelect={vi.fn()}
      />
    )

    expect(screen.getByRole("dialog")).toBeInTheDocument()
    expect(screen.getByText(/Multiple files match/i)).toBeInTheDocument()
  })

  it("should not render when closed", () => {
    render(
      <FileMatchPopup
        isOpen={false}
        onClose={vi.fn()}
        matches={mockMatches}
        onSelect={vi.fn()}
      />
    )

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument()
  })

  it("should render list of file matches", () => {
    render(
      <FileMatchPopup
        isOpen={true}
        onClose={vi.fn()}
        matches={mockMatches}
        onSelect={vi.fn()}
      />
    )

    // All matches should be visible
    expect(screen.getByText("src/components/Button.tsx")).toBeInTheDocument()
    expect(screen.getByText("docs/examples/Button.tsx")).toBeInTheDocument()
    expect(screen.getByText("test/__mocks__/Button.tsx")).toBeInTheDocument()
  })

  it("should call onSelect when file item clicked", async () => {
    const onSelect = vi.fn()
    const user = userEvent.setup()

    render(
      <FileMatchPopup
        isOpen={true}
        onClose={vi.fn()}
        matches={mockMatches}
        onSelect={onSelect}
      />
    )

    // Click first match
    const firstMatch = screen.getByText("src/components/Button.tsx")
    await user.click(firstMatch)

    expect(onSelect).toHaveBeenCalledWith("src/components/Button.tsx")
    expect(onSelect).toHaveBeenCalledTimes(1)
  })

  it("should call onClose when ESC key pressed", async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()

    render(
      <FileMatchPopup
        isOpen={true}
        onClose={onClose}
        matches={mockMatches}
        onSelect={vi.fn()}
      />
    )

    // Press ESC key
    await user.keyboard("{Escape}")

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it("should call onClose when close button clicked", async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()

    render(
      <FileMatchPopup
        isOpen={true}
        onClose={onClose}
        matches={mockMatches}
        onSelect={vi.fn()}
      />
    )

    // Click X button
    const closeButton = screen.getByRole("button", { name: /close/i })
    await user.click(closeButton)

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it("should call onClose when overlay clicked", async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()

    render(
      <FileMatchPopup
        isOpen={true}
        onClose={onClose}
        matches={mockMatches}
        onSelect={vi.fn()}
      />
    )

    // Click overlay (outside content)
    const overlay = screen.getByTestId("popup-overlay")
    await user.click(overlay)

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it("should NOT close when clicking inside content", async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()

    render(
      <FileMatchPopup
        isOpen={true}
        onClose={onClose}
        matches={mockMatches}
        onSelect={vi.fn()}
      />
    )

    // Click inside content area
    const content = screen.getByTestId("popup-content")
    await user.click(content)

    expect(onClose).not.toHaveBeenCalled()
  })

  it("should show filename in header", () => {
    const matches = ["src/Button.tsx"]

    render(
      <FileMatchPopup
        isOpen={true}
        onClose={vi.fn()}
        matches={matches}
        onSelect={vi.fn()}
      />
    )

    // Should show just the filename (not full path) in header
    const heading = screen.getByRole("heading")
    expect(heading).toHaveTextContent('Multiple files match "Button.tsx"')
  })

  it("should handle single match", () => {
    const singleMatch = ["src/App.tsx"]

    render(
      <FileMatchPopup
        isOpen={true}
        onClose={vi.fn()}
        matches={singleMatch}
        onSelect={vi.fn()}
      />
    )

    expect(screen.getByText("src/App.tsx")).toBeInTheDocument()
  })

  it("should handle empty matches gracefully", () => {
    render(
      <FileMatchPopup
        isOpen={true}
        onClose={vi.fn()}
        matches={[]}
        onSelect={vi.fn()}
      />
    )

    expect(screen.getByRole("dialog")).toBeInTheDocument()
    // Should show some message about no matches
  })
})
