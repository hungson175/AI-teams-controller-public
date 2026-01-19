/**
 * PathBreadcrumb Component Tests
 */

import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import { PathBreadcrumb } from "./PathBreadcrumb"

describe("PathBreadcrumb", () => {
  const mockOnNavigate = vi.fn()

  describe("basic rendering", () => {
    it("should render project name as first segment", () => {
      render(
        <PathBreadcrumb
          filePath="src/index.ts"
          projectName="my-project"
          onNavigate={mockOnNavigate}
        />
      )

      expect(screen.getByText("my-project")).toBeInTheDocument()
    })

    it("should render file path segments", () => {
      render(
        <PathBreadcrumb
          filePath="src/index.ts"
          projectName="project"
          onNavigate={mockOnNavigate}
        />
      )

      expect(screen.getByText("src")).toBeInTheDocument()
      expect(screen.getByText("index.ts")).toBeInTheDocument()
    })
  })

  describe("short paths", () => {
    it("should render all segments for short paths", () => {
      render(
        <PathBreadcrumb
          filePath="src/components/Button.tsx"
          projectName="project"
          onNavigate={mockOnNavigate}
          maxSegments={4}
        />
      )

      expect(screen.getByText("project")).toBeInTheDocument()
      expect(screen.getByText("src")).toBeInTheDocument()
      expect(screen.getByText("components")).toBeInTheDocument()
      expect(screen.getByText("Button.tsx")).toBeInTheDocument()
    })
  })

  describe("long paths with truncation", () => {
    it("should show ellipsis trigger for long paths", () => {
      const { container } = render(
        <PathBreadcrumb
          filePath="src/components/ui/buttons/primary/Button.tsx"
          projectName="project"
          onNavigate={mockOnNavigate}
          maxSegments={3}
        />
      )

      // Should have project and file
      expect(screen.getByText("project")).toBeInTheDocument()
      expect(screen.getByText("Button.tsx")).toBeInTheDocument()
      // Ellipsis should be present as an SVG (BreadcrumbEllipsis component)
      // It renders as an SVG with sr-only "More" text
      expect(container.querySelector('[data-slot="breadcrumb-ellipsis"]') ||
             screen.getByText("More") ||
             container.querySelector('button')).toBeInTheDocument()
    })
  })

  describe("edge cases", () => {
    it("should handle root-level file", () => {
      render(
        <PathBreadcrumb
          filePath="README.md"
          projectName="project"
          onNavigate={mockOnNavigate}
        />
      )

      expect(screen.getByText("project")).toBeInTheDocument()
      expect(screen.getByText("README.md")).toBeInTheDocument()
    })

    it("should handle empty file path", () => {
      render(
        <PathBreadcrumb
          filePath=""
          projectName="project"
          onNavigate={mockOnNavigate}
        />
      )

      expect(screen.getByText("project")).toBeInTheDocument()
    })
  })
})
