/**
 * FileTreeItem Component Tests
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { FileTreeItem } from "./FileTreeItem"
import type { FileNode } from "./types"

describe("FileTreeItem", () => {
  const mockOnFileSelect = vi.fn()
  const mockOnLoadChildren = vi.fn()
  const mockOnToggleExpanded = vi.fn()
  let expandedPaths: Set<string>

  beforeEach(() => {
    vi.clearAllMocks()
    expandedPaths = new Set()
  })

  describe("file rendering", () => {
    const fileNode: FileNode = {
      name: "test.ts",
      path: "src/test.ts",
      type: "file",
      size: 1234,
    }

    it("should render file name", () => {
      render(
        <FileTreeItem
          node={fileNode}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      expect(screen.getByText("test.ts")).toBeInTheDocument()
    })

    it("should call onFileSelect when clicked", () => {
      render(
        <FileTreeItem
          node={fileNode}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      fireEvent.click(screen.getByText("test.ts"))
      expect(mockOnFileSelect).toHaveBeenCalledWith("src/test.ts")
    })

    it("should show selected state", () => {
      render(
        <FileTreeItem
          node={fileNode}
          level={0}
          selectedPath="src/test.ts"
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      const item = screen.getByRole("treeitem")
      expect(item).toHaveAttribute("aria-selected", "true")
    })
  })

  describe("directory rendering", () => {
    const dirNode: FileNode = {
      name: "src",
      path: "src",
      type: "directory",
      size: null,
      children: [
        { name: "index.ts", path: "src/index.ts", type: "file", size: 100 },
      ],
    }

    it("should render directory name", () => {
      render(
        <FileTreeItem
          node={dirNode}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      expect(screen.getByText("src")).toBeInTheDocument()
    })

    it("should call onToggleExpanded when clicking directory", () => {
      render(
        <FileTreeItem
          node={dirNode}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      // Click to expand
      fireEvent.click(screen.getByText("src"))

      // Should call onToggleExpanded with the path
      expect(mockOnToggleExpanded).toHaveBeenCalledWith("src")
    })

    it("should show children when expanded via expandedPaths", () => {
      expandedPaths = new Set(["src"])

      render(
        <FileTreeItem
          node={dirNode}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      // Children should be visible when path is in expandedPaths
      expect(screen.getByText("index.ts")).toBeInTheDocument()
    })

    it("should have aria-expanded attribute based on expandedPaths", () => {
      const { rerender } = render(
        <FileTreeItem
          node={dirNode}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      const item = screen.getByRole("treeitem")
      expect(item).toHaveAttribute("aria-expanded", "false")

      // Rerender with path in expandedPaths
      expandedPaths = new Set(["src"])
      rerender(
        <FileTreeItem
          node={dirNode}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )
      expect(item).toHaveAttribute("aria-expanded", "true")
    })
  })

  describe("lazy loading", () => {
    const dirNodeWithoutChildren: FileNode = {
      name: "lazy-dir",
      path: "lazy-dir",
      type: "directory",
      size: null,
    }

    it("should call onLoadChildren when expanding directory without children", async () => {
      const loadedChildren: FileNode[] = [
        { name: "loaded.ts", path: "lazy-dir/loaded.ts", type: "file", size: 50 },
      ]
      mockOnLoadChildren.mockResolvedValue(loadedChildren)

      render(
        <FileTreeItem
          node={dirNodeWithoutChildren}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      fireEvent.click(screen.getByText("lazy-dir"))

      await waitFor(() => {
        expect(mockOnLoadChildren).toHaveBeenCalledWith("lazy-dir")
      })

      await waitFor(() => {
        expect(mockOnToggleExpanded).toHaveBeenCalledWith("lazy-dir")
      })
    })

    it("should auto-load children when expanded via localStorage restoration", async () => {
      const loadedChildren: FileNode[] = [
        { name: "loaded.ts", path: "lazy-dir/loaded.ts", type: "file", size: 50 },
      ]
      mockOnLoadChildren.mockResolvedValue(loadedChildren)

      // Simulate restored state where path is expanded but children not loaded
      expandedPaths = new Set(["lazy-dir"])

      render(
        <FileTreeItem
          node={dirNodeWithoutChildren}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      // Should auto-load children since it's expanded but hasLoadedChildren is false
      await waitFor(() => {
        expect(mockOnLoadChildren).toHaveBeenCalledWith("lazy-dir")
      })

      await waitFor(() => {
        expect(screen.getByText("loaded.ts")).toBeInTheDocument()
      })
    })
  })

  describe("empty directory", () => {
    const emptyDirNode: FileNode = {
      name: "empty",
      path: "empty",
      type: "directory",
      size: null,
      children: [],
    }

    it("should show empty directory message when expanded", () => {
      expandedPaths = new Set(["empty"])

      render(
        <FileTreeItem
          node={emptyDirNode}
          level={0}
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
          onLoadChildren={mockOnLoadChildren}
          teamId="test-team"
          expandedPaths={expandedPaths}
          onToggleExpanded={mockOnToggleExpanded}
        />
      )

      expect(screen.getByText("Empty directory")).toBeInTheDocument()
    })
  })
})
