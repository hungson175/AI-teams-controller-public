/**
 * QuickViewPopup Component Tests (Sprint 13 - Work Item #4)
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { userEvent } from "@testing-library/user-event"
import { QuickViewPopup } from "./QuickViewPopup"

// Mock CodeEditor component
vi.mock("@/components/file-browser/CodeEditor", () => ({
  CodeEditor: ({ value, fileName }: { value: string; fileName: string }) => (
    <div data-testid="code-editor" data-filename={fileName}>
      {value}
    </div>
  ),
}))

// Mock fetch for file content
global.fetch = vi.fn()

describe("QuickViewPopup", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(global.fetch as any).mockClear()
  })

  it("should render modal when open", () => {
    render(
      <QuickViewPopup
        isOpen={true}
        onClose={vi.fn()}
        filePath="src/App.tsx"
        teamId="test-team"
      />
    )

    // Dialog should be visible
    expect(screen.getByRole("dialog")).toBeInTheDocument()
  })

  it("should not render when closed", () => {
    render(
      <QuickViewPopup
        isOpen={false}
        onClose={vi.fn()}
        filePath="src/App.tsx"
        teamId="test-team"
      />
    )

    // Dialog should not be in document
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument()
  })

  it("should display file path in title", () => {
    render(
      <QuickViewPopup
        isOpen={true}
        onClose={vi.fn()}
        filePath="src/components/Button.tsx"
        teamId="test-team"
      />
    )

    // Check for heading (title shows just filename)
    const heading = screen.getByRole("heading", { name: /Button\.tsx/i })
    expect(heading).toBeInTheDocument()
  })

  it("should fetch and display file content with CodeEditor", async () => {
    const mockContent = "const App = () => { return <div>Hello</div> }"

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        content: mockContent,
        name: "App.tsx",
        is_binary: false,
      }),
    })

    render(
      <QuickViewPopup
        isOpen={true}
        onClose={vi.fn()}
        filePath="src/App.tsx"
        teamId="test-team"
      />
    )

    // Should show loading initially
    expect(screen.getByText(/loading/i)).toBeInTheDocument()

    // Wait for content to load
    await waitFor(() => {
      const editor = screen.getByTestId("code-editor")
      expect(editor).toBeInTheDocument()
      expect(editor).toHaveAttribute("data-filename", "App.tsx")
      expect(editor).toHaveTextContent(mockContent)
    })
  })

  it("should call onClose when ESC key pressed", async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()

    render(
      <QuickViewPopup
        isOpen={true}
        onClose={onClose}
        filePath="src/App.tsx"
        teamId="test-team"
      />
    )

    // Press ESC key
    await user.keyboard("{Escape}")

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it("should call onClose when overlay clicked", async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()

    render(
      <QuickViewPopup
        isOpen={true}
        onClose={onClose}
        filePath="src/App.tsx"
        teamId="test-team"
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

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        content: "test content",
        name: "App.tsx",
        is_binary: false,
      }),
    })

    render(
      <QuickViewPopup
        isOpen={true}
        onClose={onClose}
        filePath="src/App.tsx"
        teamId="test-team"
      />
    )

    await waitFor(() => screen.getByTestId("code-editor"))

    // Click inside content area
    const content = screen.getByTestId("popup-content")
    await user.click(content)

    expect(onClose).not.toHaveBeenCalled()
  })

  it("should show error message on fetch failure", async () => {
    ;(global.fetch as any).mockRejectedValueOnce(new Error("Network error"))

    render(
      <QuickViewPopup
        isOpen={true}
        onClose={vi.fn()}
        filePath="src/App.tsx"
        teamId="test-team"
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/failed to load file/i)).toBeInTheDocument()
    })
  })

  it("should show error for binary files", async () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        content: null,
        name: "image.png",
        is_binary: true,
      }),
    })

    render(
      <QuickViewPopup
        isOpen={true}
        onClose={vi.fn()}
        filePath="image.png"
        teamId="test-team"
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/binary file/i)).toBeInTheDocument()
    })
  })
})
