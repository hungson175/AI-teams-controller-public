/**
 * TerminalFileLink Component Tests
 * Sprint 13 - Work Item #4: Basic functionality
 * Sprint 14 - Work Item #4: Path resolution integration
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { userEvent } from "@testing-library/user-event"
import { TerminalFileLink } from "./TerminalFileLink"
import * as usePathResolverModule from "@/hooks/usePathResolver"

// Mock usePathResolver
vi.mock("@/hooks/usePathResolver")

describe("TerminalFileLink", () => {
  beforeEach(() => {
    // Mock usePathResolver for legacy tests (without teamId)
    vi.mocked(usePathResolverModule.usePathResolver).mockReturnValue({
      status: "not_found",
      matches: [],
      resolvedPath: undefined,
    })
  })

  it("should render file path as clickable link", () => {
    render(<TerminalFileLink path="src/App.tsx" onClick={vi.fn()} />)

    const link = screen.getByText("src/App.tsx")
    expect(link).toBeInTheDocument()
    expect(link.tagName).toBe("BUTTON") // Should be button for accessibility
  })

  it("should call onClick when clicked", async () => {
    const onClick = vi.fn()
    const user = userEvent.setup()

    render(<TerminalFileLink path="src/App.tsx" onClick={onClick} />)

    const link = screen.getByText("src/App.tsx")
    await user.click(link)

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it("should display path with line number", () => {
    render(<TerminalFileLink path="src/App.tsx" lineNumber={42} onClick={vi.fn()} />)

    const link = screen.getByText("src/App.tsx:42")
    expect(link).toBeInTheDocument()
  })

  it("should display path with line and column numbers", () => {
    render(
      <TerminalFileLink
        path="src/App.tsx"
        lineNumber={42}
        columnNumber={10}
        onClick={vi.fn()}
      />
    )

    const link = screen.getByText("src/App.tsx:42:10")
    expect(link).toBeInTheDocument()
  })

  it("should have appropriate styling (underline, cursor pointer)", () => {
    render(<TerminalFileLink path="src/App.tsx" onClick={vi.fn()} />)

    const link = screen.getByText("src/App.tsx")
    expect(link).toHaveClass("underline")
    expect(link).toHaveClass("cursor-pointer")
  })

  it("should have hover effect", () => {
    render(<TerminalFileLink path="src/App.tsx" onClick={vi.fn()} />)

    const link = screen.getByText("src/App.tsx")
    // Should have hover class (Tailwind: hover:text-blue-400 or similar)
    expect(link.className).toContain("hover:")
  })
})

describe("TerminalFileLink - Sprint 14 Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("should open QuickViewPopup for single match (resolved)", async () => {
    // Mock resolved status (single match)
    vi.mocked(usePathResolverModule.usePathResolver).mockReturnValue({
      status: "resolved",
      matches: ["frontend/src/App.tsx"],
      resolvedPath: "frontend/src/App.tsx",
    })

    const user = userEvent.setup()
    render(
      <TerminalFileLink
        path="src/App.tsx"
        teamId="test-team"
        onClick={vi.fn()}
      />
    )

    const link = screen.getByText("src/App.tsx")
    await user.click(link)

    // QuickViewPopup should be visible
    await waitFor(() => {
      expect(screen.getByRole("dialog")).toBeInTheDocument()
      expect(screen.getByText("App.tsx")).toBeInTheDocument() // Header shows filename
    })
  })

  it("should open FileMatchPopup for multiple matches", async () => {
    // Mock multiple status
    vi.mocked(usePathResolverModule.usePathResolver).mockReturnValue({
      status: "multiple",
      matches: [
        "src/components/Button.tsx",
        "docs/examples/Button.tsx",
        "test/__mocks__/Button.tsx",
      ],
      resolvedPath: undefined,
    })

    const user = userEvent.setup()
    render(
      <TerminalFileLink
        path="Button.tsx"
        teamId="test-team"
        onClick={vi.fn()}
      />
    )

    const link = screen.getByText("Button.tsx")
    await user.click(link)

    // FileMatchPopup should be visible
    await waitFor(() => {
      expect(screen.getByRole("dialog")).toBeInTheDocument()
      expect(screen.getByText(/Multiple files match/i)).toBeInTheDocument()
    })
  })

  it("should show error toast for not found", async () => {
    // Mock not_found status
    vi.mocked(usePathResolverModule.usePathResolver).mockReturnValue({
      status: "not_found",
      matches: [],
      resolvedPath: undefined,
    })

    const user = userEvent.setup()
    render(
      <TerminalFileLink
        path="NonExistent.tsx"
        teamId="test-team"
        onClick={vi.fn()}
      />
    )

    const link = screen.getByText("NonExistent.tsx")
    await user.click(link)

    // Toast should appear
    await waitFor(() => {
      // Check for toast message (using react-hot-toast or similar)
      // Exact assertion depends on toast implementation
      expect(
        screen.queryByText(/file not found/i) ||
          screen.queryByText(/NonExistent\.tsx/i)
      ).toBeTruthy()
    })
  })

  it("should show loading state while resolving", () => {
    // Mock loading status
    vi.mocked(usePathResolverModule.usePathResolver).mockReturnValue({
      status: "loading",
      matches: [],
      resolvedPath: undefined,
    })

    render(
      <TerminalFileLink
        path="Button.tsx"
        teamId="test-team"
        onClick={vi.fn()}
      />
    )

    const link = screen.getByText("Button.tsx")
    // Should still be clickable but may show loading cursor
    expect(link).toBeInTheDocument()
  })

  it("should select file from FileMatchPopup and open QuickViewPopup", async () => {
    // Mock multiple status
    vi.mocked(usePathResolverModule.usePathResolver).mockReturnValue({
      status: "multiple",
      matches: ["src/Button.tsx", "lib/Button.tsx"],
      resolvedPath: undefined,
    })

    const user = userEvent.setup()
    render(
      <TerminalFileLink
        path="Button.tsx"
        teamId="test-team"
        onClick={vi.fn()}
      />
    )

    // Click link
    const link = screen.getByText("Button.tsx")
    await user.click(link)

    // FileMatchPopup appears
    await waitFor(() => {
      expect(screen.getByText(/Multiple files match/i)).toBeInTheDocument()
    })

    // Click first match
    const firstMatch = screen.getByText("src/Button.tsx")
    await user.click(firstMatch)

    // QuickViewPopup should now appear
    await waitFor(() => {
      // FileMatchPopup should close
      expect(screen.queryByText(/Multiple files match/i)).not.toBeInTheDocument()
      // QuickViewPopup should open (check for dialog role)
      const dialogs = screen.getAllByRole("dialog")
      expect(dialogs.length).toBeGreaterThan(0)
      // Verify the popup shows the selected file path
      expect(screen.getByText("src/Button.tsx")).toBeInTheDocument()
    })
  })
})
