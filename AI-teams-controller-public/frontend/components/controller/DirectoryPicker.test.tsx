/**
 * DirectoryPicker Component Tests - TDD
 * Sprint 10: New Terminal with Directory Selection
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { DirectoryPicker } from "./DirectoryPicker"

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock auth headers
vi.mock("@/lib/auth-utils", () => ({
  getAuthHeaders: () => ({ Authorization: "Bearer test-token" }),
}))

// Mock toast
const mockToast = vi.fn()
vi.mock("@/hooks/use-toast", () => ({
  useToast: () => ({ toast: mockToast }),
}))

describe("DirectoryPicker", () => {
  const mockOnSelect = vi.fn()
  const mockOnCancel = vi.fn()

  const mockDirectories = [
    { name: "projects", path: "/home/user/projects", type: "directory", size: null },
    { name: "documents", path: "/home/user/documents", type: "directory", size: null },
    { name: ".config", path: "/home/user/.config", type: "directory", size: null },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        project_root: "/home/user",
        tree: mockDirectories,
      }),
    })
  })

  describe("rendering", () => {
    it("should render with title", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText("Select Directory")).toBeInTheDocument()
      })
    })

    it("should show loading state initially", () => {
      // Make fetch hang
      mockFetch.mockImplementation(() => new Promise(() => {}))

      const { container } = render(
        <DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />
      )

      expect(container.querySelector(".animate-spin")).toBeInTheDocument()
    })

    it("should render directory list after loading", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText("projects")).toBeInTheDocument()
        expect(screen.getByText("documents")).toBeInTheDocument()
      })
    })

    it("should only show directories, not files", async () => {
      // Include a file in the response
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          project_root: "/home/user",
          tree: [
            { name: "projects", path: "/home/user/projects", type: "directory", size: null },
            { name: "readme.txt", path: "/home/user/readme.txt", type: "file", size: 100 },
          ],
        }),
      })

      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText("projects")).toBeInTheDocument()
      })

      // File should NOT be visible
      expect(screen.queryByText("readme.txt")).not.toBeInTheDocument()
    })

    it("should show Cancel and Select buttons", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument()
        expect(screen.getByRole("button", { name: /select/i })).toBeInTheDocument()
      })
    })
  })

  describe("selection behavior", () => {
    it("should highlight selected directory when clicked", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText("projects")).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText("projects"))

      // Should show selected path
      await waitFor(() => {
        expect(screen.getByText("/home/user/projects")).toBeInTheDocument()
      })
    })

    it("should call onSelect with path when Select button clicked", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText("projects")).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText("projects"))
      fireEvent.click(screen.getByRole("button", { name: /select/i }))

      expect(mockOnSelect).toHaveBeenCalledWith("/home/user/projects")
    })

    it("should disable Select button when no directory selected", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /select/i })).toBeDisabled()
      })
    })

    it("should enable Select button when directory selected", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText("projects")).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText("projects"))

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /select/i })).not.toBeDisabled()
      })
    })
  })

  describe("cancel behavior", () => {
    it("should call onCancel when Cancel button clicked", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument()
      })

      fireEvent.click(screen.getByRole("button", { name: /cancel/i }))

      expect(mockOnCancel).toHaveBeenCalled()
    })
  })

  describe("directory expansion", () => {
    it("should expand directory and load children when clicked", async () => {
      // First call returns root directories
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          project_root: "/home/user",
          tree: mockDirectories,
        }),
      })

      // Second call returns subdirectories
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          project_root: "/home/user/projects",
          tree: [
            { name: "myapp", path: "/home/user/projects/myapp", type: "directory", size: null },
          ],
        }),
      })

      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText("projects")).toBeInTheDocument()
      })

      // Click to expand
      fireEvent.click(screen.getByText("projects"))

      // Should load and show children
      await waitFor(() => {
        expect(screen.getByText("myapp")).toBeInTheDocument()
      })
    })
  })

  describe("error handling", () => {
    it("should show error message on API failure", async () => {
      mockFetch.mockRejectedValue(new Error("Network error"))

      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText(/failed to load/i)).toBeInTheDocument()
      })
    })
  })

  describe("API calls", () => {
    it("should call directories API on mount", async () => {
      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          "/api/system/directories?path=~",
          expect.objectContaining({
            headers: { Authorization: "Bearer test-token" },
          })
        )
      })
    })

    it("should call directories API with path when expanding", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          project_root: "/home/user",
          tree: mockDirectories,
        }),
      })

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          project_root: "/home/user/projects",
          tree: [],
        }),
      })

      render(<DirectoryPicker onSelect={mockOnSelect} onCancel={mockOnCancel} />)

      await waitFor(() => {
        expect(screen.getByText("projects")).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText("projects"))

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          "/api/system/directories?path=%2Fhome%2Fuser%2Fprojects",
          expect.any(Object)
        )
      })
    })
  })
})
