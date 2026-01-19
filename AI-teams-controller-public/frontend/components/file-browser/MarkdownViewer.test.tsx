/**
 * MarkdownViewer Component Tests
 */

import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { MarkdownViewer } from "./MarkdownViewer"

describe("MarkdownViewer", () => {
  describe("basic markdown rendering", () => {
    it("should render plain text", () => {
      render(<MarkdownViewer content="Hello World" />)

      expect(screen.getByText("Hello World")).toBeInTheDocument()
    })

    it("should render heading", () => {
      // Single heading without newlines works better in test environment
      render(<MarkdownViewer content="# Main Title" />)

      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Main Title")
    })

    it("should render inline code", () => {
      render(<MarkdownViewer content="Use `npm install` to install" />)

      expect(screen.getByText("npm install")).toBeInTheDocument()
    })

    it("should render links", () => {
      render(<MarkdownViewer content="Visit [Google](https://google.com)" />)

      const link = screen.getByRole("link", { name: "Google" })
      expect(link).toHaveAttribute("href", "https://google.com")
      expect(link).toHaveAttribute("target", "_blank")
    })

    it("should render blockquotes", () => {
      render(<MarkdownViewer content="> This is a quote" />)

      expect(screen.getByText("This is a quote")).toBeInTheDocument()
    })
  })

  describe("text formatting", () => {
    it("should render bold text", () => {
      render(<MarkdownViewer content="This is **bold** text" />)

      // Check for the strong element
      const strong = screen.getByText("bold")
      expect(strong.tagName).toBe("STRONG")
    })

    it("should render italic text", () => {
      render(<MarkdownViewer content="This is *italic* text" />)

      // Check for the em element
      const em = screen.getByText("italic")
      expect(em.tagName).toBe("EM")
    })
  })

  describe("empty content", () => {
    it("should handle empty content gracefully", () => {
      const { container } = render(<MarkdownViewer content="" />)

      // Should render without crashing
      expect(container).toBeInTheDocument()
    })
  })

  describe("scroll area", () => {
    it("should wrap content in a scrollable area", () => {
      const { container } = render(<MarkdownViewer content="Some content" />)

      // Check for the scroll area data attribute
      expect(container.querySelector('[data-slot="scroll-area"]')).toBeInTheDocument()
    })
  })
})
