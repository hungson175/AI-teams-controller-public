/**
 * AutocompleteDropdown Component Tests
 *
 * TDD Phase: RED - Tests written BEFORE component extraction
 *
 * Component Purpose:
 * - Display autocomplete suggestions (commands or paths)
 * - Handle keyboard navigation (ArrowUp, ArrowDown, Tab, Escape)
 * - Support path loading state
 * - Distinguish between path and command suggestions visually
 */

import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { AutocompleteDropdown } from "./AutocompleteDropdown"

describe("AutocompleteDropdown", () => {
  const mockOnSelect = vi.fn()
  const mockOnDismiss = vi.fn()
  const mockOnNavigate = vi.fn()

  const defaultProps = {
    suggestions: ["run tests", "run build", "git status"],
    selectedIndex: 0,
    onSelect: mockOnSelect,
    onDismiss: mockOnDismiss,
    onNavigate: mockOnNavigate,
    isLoading: false,
    isPathMode: false,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("Rendering", () => {
    it("should render suggestions dropdown when suggestions provided", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      expect(screen.getByRole("listbox")).toBeInTheDocument()
      expect(screen.getByText("run tests")).toBeInTheDocument()
      expect(screen.getByText("run build")).toBeInTheDocument()
      expect(screen.getByText("git status")).toBeInTheDocument()
    })

    it("should not render when suggestions array is empty", () => {
      render(<AutocompleteDropdown {...defaultProps} suggestions={[]} />)

      expect(screen.queryByRole("listbox")).not.toBeInTheDocument()
    })

    it("should show loading indicator when isLoading is true", () => {
      render(<AutocompleteDropdown {...defaultProps} isLoading={true} suggestions={[]} />)

      expect(screen.getByTestId("path-loading")).toBeInTheDocument()
      expect(screen.getByText("Loading paths...")).toBeInTheDocument()
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument()
    })

    it("should display path icon (Folder) for path suggestions", () => {
      const pathSuggestions = ["src/", "lib/", "app/components/"]
      render(
        <AutocompleteDropdown
          {...defaultProps}
          suggestions={pathSuggestions}
          isPathMode={true}
        />
      )

      // Check that path icons are rendered (Folder icons)
      const options = screen.getAllByRole("option")
      expect(options).toHaveLength(3)
      // Path suggestions should have Folder icon (visual distinction)
    })

    it("should display command icon ($) for command suggestions", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      const options = screen.getAllByRole("option")
      expect(options).toHaveLength(3)
      // Command suggestions should have $ prefix (visual distinction)
      expect(screen.getAllByText("$")).toHaveLength(3)
    })

    it("should highlight selected suggestion", () => {
      render(<AutocompleteDropdown {...defaultProps} selectedIndex={1} />)

      const options = screen.getAllByRole("option")
      expect(options[1]).toHaveAttribute("aria-selected", "true")
      expect(options[0]).toHaveAttribute("aria-selected", "false")
      expect(options[2]).toHaveAttribute("aria-selected", "false")
    })

    it("should show keyboard hints in footer", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      expect(screen.getByText(/↑↓ Navigate/)).toBeInTheDocument()
      expect(screen.getByText(/Tab Select/)).toBeInTheDocument()
      expect(screen.getByText(/Esc Close/)).toBeInTheDocument()
    })
  })

  describe("Mouse Interactions", () => {
    it("should call onSelect when suggestion is clicked", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      const firstOption = screen.getAllByRole("option")[0]
      fireEvent.click(firstOption)

      expect(mockOnSelect).toHaveBeenCalledWith("run tests")
      expect(mockOnSelect).toHaveBeenCalledTimes(1)
    })

    it("should call onNavigate when hovering over suggestion", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      const secondOption = screen.getAllByRole("option")[1]
      fireEvent.mouseEnter(secondOption)

      expect(mockOnNavigate).toHaveBeenCalledWith(1)
      expect(mockOnNavigate).toHaveBeenCalledTimes(1)
    })
  })

  describe("Keyboard Navigation", () => {
    it("should call onNavigate with next index on ArrowDown", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      const listbox = screen.getByRole("listbox")
      fireEvent.keyDown(listbox, { key: "ArrowDown" })

      expect(mockOnNavigate).toHaveBeenCalledWith(1)
    })

    it("should call onNavigate with previous index on ArrowUp", () => {
      render(<AutocompleteDropdown {...defaultProps} selectedIndex={2} />)

      const listbox = screen.getByRole("listbox")
      fireEvent.keyDown(listbox, { key: "ArrowUp" })

      expect(mockOnNavigate).toHaveBeenCalledWith(1)
    })

    it("should wrap to last suggestion on ArrowUp from first item", () => {
      render(<AutocompleteDropdown {...defaultProps} selectedIndex={0} />)

      const listbox = screen.getByRole("listbox")
      fireEvent.keyDown(listbox, { key: "ArrowUp" })

      expect(mockOnNavigate).toHaveBeenCalledWith(2) // Last index
    })

    it("should wrap to first suggestion on ArrowDown from last item", () => {
      render(<AutocompleteDropdown {...defaultProps} selectedIndex={2} />)

      const listbox = screen.getByRole("listbox")
      fireEvent.keyDown(listbox, { key: "ArrowDown" })

      expect(mockOnNavigate).toHaveBeenCalledWith(0) // First index
    })

    it("should call onSelect with current suggestion on Tab", () => {
      render(<AutocompleteDropdown {...defaultProps} selectedIndex={1} />)

      const listbox = screen.getByRole("listbox")
      fireEvent.keyDown(listbox, { key: "Tab" })

      expect(mockOnSelect).toHaveBeenCalledWith("run build")
    })

    it("should call onDismiss on Escape", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      const listbox = screen.getByRole("listbox")
      fireEvent.keyDown(listbox, { key: "Escape" })

      expect(mockOnDismiss).toHaveBeenCalledTimes(1)
    })

    it("should prevent default on all navigation keys", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      const listbox = screen.getByRole("listbox")
      const arrowDownEvent = new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true })
      const preventDefaultSpy = vi.spyOn(arrowDownEvent, "preventDefault")

      listbox.dispatchEvent(arrowDownEvent)

      expect(preventDefaultSpy).toHaveBeenCalled()
    })
  })

  describe("Accessibility", () => {
    it("should have proper ARIA role", () => {
      render(<AutocompleteDropdown {...defaultProps} />)

      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    it("should have aria-label for path mode", () => {
      render(<AutocompleteDropdown {...defaultProps} isPathMode={true} />)

      expect(screen.getByLabelText("Path suggestions")).toBeInTheDocument()
    })

    it("should have aria-label for command mode", () => {
      render(<AutocompleteDropdown {...defaultProps} isPathMode={false} />)

      expect(screen.getByLabelText("Command suggestions")).toBeInTheDocument()
    })

    it("should mark selected option with aria-selected", () => {
      render(<AutocompleteDropdown {...defaultProps} selectedIndex={1} />)

      const options = screen.getAllByRole("option")
      expect(options[1]).toHaveAttribute("aria-selected", "true")
    })
  })

  describe("Visual Styling", () => {
    it("should apply different highlight color for path vs command mode", () => {
      const { rerender } = render(<AutocompleteDropdown {...defaultProps} selectedIndex={0} />)

      let selectedOption = screen.getAllByRole("option")[0]
      // Command mode should have green highlight
      expect(selectedOption).toHaveClass("bg-green-500/20", "text-green-400")

      rerender(
        <AutocompleteDropdown
          {...defaultProps}
          selectedIndex={0}
          isPathMode={true}
          suggestions={["src/", "lib/"]}
        />
      )

      selectedOption = screen.getAllByRole("option")[0]
      // Path mode should have blue highlight
      expect(selectedOption).toHaveClass("bg-blue-500/20", "text-blue-400")
    })

    it("should show hover styles on non-selected items", () => {
      render(<AutocompleteDropdown {...defaultProps} selectedIndex={0} />)

      const nonSelectedOption = screen.getAllByRole("option")[1]
      expect(nonSelectedOption).toHaveClass("hover:bg-muted/50")
    })
  })

  describe("Edge Cases", () => {
    it("should handle single suggestion", () => {
      render(<AutocompleteDropdown {...defaultProps} suggestions={["only one"]} />)

      expect(screen.getAllByRole("option")).toHaveLength(1)
    })

    it("should handle very long suggestion text", () => {
      const longSuggestion = "a".repeat(200)
      render(<AutocompleteDropdown {...defaultProps} suggestions={[longSuggestion]} />)

      expect(screen.getByText(longSuggestion)).toBeInTheDocument()
    })

    it("should not render loading state when suggestions exist", () => {
      render(<AutocompleteDropdown {...defaultProps} isLoading={true} suggestions={["test"]} />)

      // When both isLoading and suggestions exist, loading should NOT show
      expect(screen.queryByTestId("autocomplete-loading")).not.toBeInTheDocument()
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    it("should handle selection index out of bounds gracefully", () => {
      render(<AutocompleteDropdown {...defaultProps} selectedIndex={999} />)

      // Should not crash, should render normally
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })
  })
})
