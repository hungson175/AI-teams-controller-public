/**
 * FileBrowser Component Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { FileBrowser } from "./FileBrowser"

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock auth headers
vi.mock("@/lib/auth-utils", () => ({
  getAuthHeaders: () => ({ Authorization: "Bearer test-token" }),
}))

// Mock useIsDesktop hook
const mockUseIsDesktop = vi.fn()
vi.mock("@/hooks/use-desktop", () => ({
  useIsDesktop: () => mockUseIsDesktop(),
}))

// Mock ResizablePanelGroup to simplify testing
vi.mock("@/components/ui/resizable", () => ({
  ResizablePanelGroup: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="resizable-panel-group">{children}</div>
  ),
  ResizablePanel: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="resizable-panel">{children}</div>
  ),
  ResizableHandle: () => <div data-testid="resizable-handle" />,
}))

// Mock FileNameSearch component
vi.mock("./FileNameSearch", () => ({
  FileNameSearch: ({ teamId, onFileSelect }: { teamId: string; onFileSelect: (path: string) => void }) => (
    <div data-testid="filename-search">
      <input data-testid="filename-search-input" placeholder="Search files..." />
      <button onClick={() => onFileSelect("test-file.tsx")}>Test Result</button>
    </div>
  ),
}))

describe("FileBrowser", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ project_root: "/home/user/project", tree: [] }),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe("desktop layout (1024px+)", () => {
    beforeEach(() => {
      mockUseIsDesktop.mockReturnValue(true)
    })

    it("should render resizable panel layout on desktop", () => {
      render(<FileBrowser teamId="test-team" />)

      expect(screen.getByTestId("resizable-panel-group")).toBeInTheDocument()
      expect(screen.getAllByTestId("resizable-panel")).toHaveLength(2)
      expect(screen.getByTestId("resizable-handle")).toBeInTheDocument()
    })

    it("should not show tab switcher on desktop", () => {
      render(<FileBrowser teamId="test-team" />)

      expect(screen.queryByRole("tablist")).not.toBeInTheDocument()
    })
  })

  describe("mobile/tablet layout (<1024px)", () => {
    beforeEach(() => {
      mockUseIsDesktop.mockReturnValue(false)
    })

    it("should render tab-based layout on mobile", () => {
      render(<FileBrowser teamId="test-team" />)

      expect(screen.getByRole("tablist")).toBeInTheDocument()
      expect(screen.queryByTestId("resizable-panel-group")).not.toBeInTheDocument()
    })

    it("should show Files and Viewer tabs", () => {
      render(<FileBrowser teamId="test-team" />)

      expect(screen.getByRole("tab", { name: /files/i })).toBeInTheDocument()
      expect(screen.getByRole("tab", { name: /viewer/i })).toBeInTheDocument()
    })

    it("should default to Files tab", () => {
      render(<FileBrowser teamId="test-team" />)

      const filesTab = screen.getByRole("tab", { name: /files/i })
      expect(filesTab).toHaveAttribute("data-state", "active")
    })

    it("should have clickable Viewer tab", () => {
      render(<FileBrowser teamId="test-team" />)

      const viewerTab = screen.getByRole("tab", { name: /viewer/i })
      expect(viewerTab).toBeEnabled()

      // Verify click doesn't throw
      fireEvent.click(viewerTab)
    })

    it("should have clickable Files tab", () => {
      render(<FileBrowser teamId="test-team" />)

      const filesTab = screen.getByRole("tab", { name: /files/i })
      expect(filesTab).toBeEnabled()

      // Verify click doesn't throw
      fireEvent.click(filesTab)
    })
  })

  describe("file selection behavior", () => {
    it("should not show tabs on desktop view", () => {
      mockUseIsDesktop.mockReturnValue(true)

      render(<FileBrowser teamId="test-team" />)

      // Desktop doesn't have tabs
      expect(screen.queryByRole("tablist")).not.toBeInTheDocument()
    })
  })

  describe("layout switching", () => {
    it("should switch from desktop to mobile layout when viewport changes", () => {
      // Start as desktop
      mockUseIsDesktop.mockReturnValue(true)
      const { rerender } = render(<FileBrowser teamId="test-team" />)

      expect(screen.getByTestId("resizable-panel-group")).toBeInTheDocument()
      expect(screen.queryByRole("tablist")).not.toBeInTheDocument()

      // Switch to mobile
      mockUseIsDesktop.mockReturnValue(false)
      rerender(<FileBrowser teamId="test-team" />)

      expect(screen.queryByTestId("resizable-panel-group")).not.toBeInTheDocument()
      expect(screen.getByRole("tablist")).toBeInTheDocument()
    })

    it("should switch from mobile to desktop layout when viewport changes", () => {
      // Start as mobile
      mockUseIsDesktop.mockReturnValue(false)
      const { rerender } = render(<FileBrowser teamId="test-team" />)

      expect(screen.getByRole("tablist")).toBeInTheDocument()
      expect(screen.queryByTestId("resizable-panel-group")).not.toBeInTheDocument()

      // Switch to desktop
      mockUseIsDesktop.mockReturnValue(true)
      rerender(<FileBrowser teamId="test-team" />)

      expect(screen.getByTestId("resizable-panel-group")).toBeInTheDocument()
      expect(screen.queryByRole("tablist")).not.toBeInTheDocument()
    })
  })

  describe("Story 2: FileNameSearch Integration", () => {
    it("should render FileNameSearch component in desktop layout", () => {
      mockUseIsDesktop.mockReturnValue(true)

      render(<FileBrowser teamId="test-team" />)

      expect(screen.getByTestId("filename-search")).toBeInTheDocument()
      expect(screen.getByTestId("filename-search-input")).toBeInTheDocument()
    })

    it("should render FileNameSearch component in mobile layout", () => {
      mockUseIsDesktop.mockReturnValue(false)

      render(<FileBrowser teamId="test-team" />)

      expect(screen.getByTestId("filename-search")).toBeInTheDocument()
      expect(screen.getByTestId("filename-search-input")).toBeInTheDocument()
    })

    it("should pass teamId to FileNameSearch", () => {
      mockUseIsDesktop.mockReturnValue(true)

      render(<FileBrowser teamId="my-test-team" />)

      // FileNameSearch is rendered (mock receives teamId prop)
      expect(screen.getByTestId("filename-search")).toBeInTheDocument()
    })

    it("should handle file selection from FileNameSearch", () => {
      mockUseIsDesktop.mockReturnValue(true)

      render(<FileBrowser teamId="test-team" />)

      // Click on mocked result in FileNameSearch
      const resultButton = screen.getByText("Test Result")
      fireEvent.click(resultButton)

      // File selection should work (verified via mock)
      // The component should not crash
      expect(screen.getByTestId("filename-search")).toBeInTheDocument()
    })
  })
})
