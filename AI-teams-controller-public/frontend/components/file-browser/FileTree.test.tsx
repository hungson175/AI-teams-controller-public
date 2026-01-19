/**
 * FileTree Component Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { FileTree } from "./FileTree"
import type { TreeResponse } from "./types"

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock auth headers
vi.mock("@/lib/auth-utils", () => ({
  getAuthHeaders: () => ({ Authorization: "Bearer test-token" }),
}))

describe("FileTree", () => {
  const mockOnFileSelect = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe("loading state", () => {
    it("should show loading skeleton initially", () => {
      // Never resolve the fetch
      mockFetch.mockImplementation(() => new Promise(() => {}))

      const { container } = render(
        <FileTree
          teamId="test-team"
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
        />
      )

      // Should show loading skeleton (FileTreeSkeleton with animate-pulse elements)
      expect(container.querySelector('[class*="animate-pulse"]')).toBeInTheDocument()
    })
  })

  describe("successful load", () => {
    const mockTreeResponse: TreeResponse = {
      project_root: "/home/user/project",
      tree: [
        { name: "src", path: "src", type: "directory", size: null },
        { name: "README.md", path: "README.md", type: "file", size: 1234 },
      ],
    }

    it("should render tree items after loading", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockTreeResponse),
      })

      render(
        <FileTree
          teamId="test-team"
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
        />
      )

      await waitFor(() => {
        expect(screen.getByText("src")).toBeInTheDocument()
        expect(screen.getByText("README.md")).toBeInTheDocument()
      })
    })

    it("should display project root in header", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockTreeResponse),
      })

      render(
        <FileTree
          teamId="test-team"
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
        />
      )

      await waitFor(() => {
        expect(screen.getByText("project")).toBeInTheDocument()
      })
    })
  })

  describe("error handling", () => {
    it("should show error message on 404", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
      })

      render(
        <FileTree
          teamId="test-team"
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
        />
      )

      await waitFor(() => {
        expect(screen.getByText("Project not found for this team")).toBeInTheDocument()
      })
    })

    it("should show error message on network error", async () => {
      mockFetch.mockRejectedValue(new Error("Network error"))

      render(
        <FileTree
          teamId="test-team"
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
        />
      )

      await waitFor(() => {
        expect(screen.getByText("Failed to load file tree")).toBeInTheDocument()
      })
    })

    it("should show retry button on error", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
      })

      render(
        <FileTree
          teamId="test-team"
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
        />
      )

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument()
      })
    })
  })

  describe("empty tree", () => {
    it("should show message when tree is empty", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ project_root: "/home/user/project", tree: [] }),
      })

      render(
        <FileTree
          teamId="test-team"
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
        />
      )

      await waitFor(() => {
        expect(screen.getByText("No files found")).toBeInTheDocument()
      })
    })
  })

  describe("API calls", () => {
    it("should call API with correct parameters", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ project_root: "/home/user/project", tree: [] }),
      })

      render(
        <FileTree
          teamId="my-team"
          selectedPath={null}
          onFileSelect={mockOnFileSelect}
        />
      )

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          "/api/files/my-team/tree?path=&depth=1&show_hidden=true",
          expect.objectContaining({
            headers: { Authorization: "Bearer test-token" },
          })
        )
      })
    })
  })
})
