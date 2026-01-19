/**
 * FileViewer Component Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { FileViewer } from "./FileViewer"
import type { FileContent } from "./types"

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock auth headers
vi.mock("@/lib/auth-utils", () => ({
  getAuthHeaders: () => ({ Authorization: "Bearer test-token" }),
}))

// Mock Monaco Editor
vi.mock("@monaco-editor/react", () => ({
  default: ({ value }: { value: string }) => (
    <div data-testid="monaco-editor">{value}</div>
  ),
}))

describe("FileViewer", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe("no file selected", () => {
    it("should show placeholder when no file is selected", () => {
      render(<FileViewer teamId="test-team" filePath={null} />)

      expect(screen.getByText("Select a file to view")).toBeInTheDocument()
    })
  })

  describe("loading state", () => {
    it("should show loading spinner while fetching", () => {
      // Never resolve the fetch
      mockFetch.mockImplementation(() => new Promise(() => {}))

      const { container } = render(<FileViewer teamId="test-team" filePath="src/index.ts" />)

      // Should show loading spinner (Loader2 component with animate-spin)
      expect(container.querySelector('.animate-spin')).toBeInTheDocument()
    })
  })

  describe("successful file load", () => {
    it("should render code content for TypeScript files", async () => {
      const fileContent: FileContent = {
        path: "src/index.ts",
        name: "index.ts",
        size: 100,
        mime_type: "text/plain",
        content: "const x = 1;",
        is_binary: false,
        is_truncated: false,
        error: null,
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(fileContent),
      })

      render(<FileViewer teamId="test-team" filePath="src/index.ts" />)

      await waitFor(() => {
        expect(screen.getByTestId("monaco-editor")).toHaveTextContent("const x = 1;")
      })
    })

    it("should render markdown for .md files", async () => {
      const fileContent: FileContent = {
        path: "README.md",
        name: "README.md",
        size: 50,
        mime_type: "text/plain",
        content: "# Hello World",
        is_binary: false,
        is_truncated: false,
        error: null,
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(fileContent),
      })

      render(<FileViewer teamId="test-team" filePath="README.md" />)

      await waitFor(() => {
        expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Hello World")
      })
    })
  })

  describe("binary files", () => {
    it("should show binary placeholder for binary files", async () => {
      const fileContent: FileContent = {
        path: "image.png",
        name: "image.png",
        size: 5000,
        mime_type: "image/png",
        content: null,
        is_binary: true,
        is_truncated: false,
        error: null,
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(fileContent),
      })

      render(<FileViewer teamId="test-team" filePath="image.png" />)

      await waitFor(() => {
        expect(screen.getByText("Binary files cannot be displayed")).toBeInTheDocument()
        // File name appears in both breadcrumb and placeholder
        expect(screen.getAllByText("image.png").length).toBeGreaterThan(0)
      })
    })
  })

  describe("truncated files", () => {
    it("should show placeholder for truncated files", async () => {
      const fileContent: FileContent = {
        path: "large.txt",
        name: "large.txt",
        size: 10000000,
        mime_type: "text/plain",
        content: null,
        is_binary: false,
        is_truncated: true,
        error: "File too large",
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(fileContent),
      })

      render(<FileViewer teamId="test-team" filePath="large.txt" />)

      await waitFor(() => {
        expect(screen.getByText("File too large")).toBeInTheDocument()
      })
    })
  })

  describe("error handling", () => {
    it("should show error message on 404", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
      })

      render(<FileViewer teamId="test-team" filePath="missing.ts" />)

      await waitFor(() => {
        expect(screen.getByText("File not found")).toBeInTheDocument()
      })
    })

    it("should show error message on network error", async () => {
      mockFetch.mockRejectedValue(new Error("Network error"))

      render(<FileViewer teamId="test-team" filePath="test.ts" />)

      await waitFor(() => {
        expect(screen.getByText("Failed to load file content")).toBeInTheDocument()
      })
    })

    it("should show error message on other HTTP errors", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
      })

      render(<FileViewer teamId="test-team" filePath="test.ts" />)

      await waitFor(() => {
        expect(screen.getByText("Failed to load file: 500")).toBeInTheDocument()
      })
    })

    it("should show file with error from API response", async () => {
      const fileContent: FileContent = {
        path: "blacklisted.env",
        name: "blacklisted.env",
        size: 100,
        mime_type: "text/plain",
        content: null,
        is_binary: false,
        is_truncated: false,
        error: "File type not allowed",
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(fileContent),
      })

      render(<FileViewer teamId="test-team" filePath="blacklisted.env" />)

      await waitFor(() => {
        expect(screen.getByText("File type not allowed")).toBeInTheDocument()
      })
    })
  })

  describe("API calls", () => {
    it("should call API with correct parameters", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          path: "test.ts",
          name: "test.ts",
          size: 50,
          mime_type: "text/plain",
          content: "code",
          is_binary: false,
          is_truncated: false,
          error: null,
        }),
      })

      render(<FileViewer teamId="my-team" filePath="src/file.ts" />)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          "/api/files/my-team/content?path=src%2Ffile.ts",
          expect.objectContaining({
            headers: { Authorization: "Bearer test-token" },
          })
        )
      })
    })

    it("should encode special characters in path", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          path: "dir/file name.ts",
          name: "file name.ts",
          size: 50,
          mime_type: "text/plain",
          content: "code",
          is_binary: false,
          is_truncated: false,
          error: null,
        }),
      })

      render(<FileViewer teamId="team" filePath="dir/file name.ts" />)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          "/api/files/team/content?path=dir%2Ffile%20name.ts",
          expect.any(Object)
        )
      })
    })
  })
})
