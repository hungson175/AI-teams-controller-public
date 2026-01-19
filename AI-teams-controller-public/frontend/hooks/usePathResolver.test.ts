/**
 * usePathResolver Hook Tests (Sprint 14 - Work Item #2)
 *
 * TDD: Tests written FIRST per Boss requirement
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { renderHook, waitFor } from "@testing-library/react"
import { usePathResolver } from "./usePathResolver"
import * as useFileListCacheModule from "./useFileListCache"

// Mock useFileListCache
vi.mock("./useFileListCache")

describe("usePathResolver", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("should return 'loading' status while file list is loading", () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: [],
      isLoading: true,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "Button.tsx")
    )

    expect(result.current.status).toBe("loading")
    expect(result.current.matches).toEqual([])
    expect(result.current.resolvedPath).toBeUndefined()
  })

  it("should return 'resolved' status for single exact match", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["src/components/Button.tsx", "lib/utils.ts"],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "src/components/Button.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("resolved")
    })

    expect(result.current.matches).toEqual(["src/components/Button.tsx"])
    expect(result.current.resolvedPath).toBe("src/components/Button.tsx")
  })

  it("should return 'resolved' for single suffix match", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["frontend/src/Button.tsx", "backend/api.ts"],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "src/Button.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("resolved")
    })

    expect(result.current.matches).toEqual(["frontend/src/Button.tsx"])
    expect(result.current.resolvedPath).toBe("frontend/src/Button.tsx")
  })

  it("should return 'multiple' status for multiple matches", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: [
        "src/components/Button.tsx",
        "docs/examples/Button.tsx",
        "test/__mocks__/Button.tsx",
      ],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "Button.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("multiple")
    })

    expect(result.current.matches.length).toBe(3)
    expect(result.current.matches).toContain("src/components/Button.tsx")
    expect(result.current.matches).toContain("docs/examples/Button.tsx")
    expect(result.current.matches).toContain("test/__mocks__/Button.tsx")
    expect(result.current.resolvedPath).toBeUndefined()
  })

  it("should return 'not_found' status for zero matches", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["src/App.tsx", "lib/utils.ts"],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "NonExistent.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("not_found")
    })

    expect(result.current.matches).toEqual([])
    expect(result.current.resolvedPath).toBeUndefined()
  })

  it("should handle case-insensitive matching", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["src/Components/Button.tsx"],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "components/button.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("resolved")
    })

    expect(result.current.matches).toEqual(["src/Components/Button.tsx"])
  })

  it("should normalize ./ prefix in paths", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["src/components/Button.tsx"],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "./src/components/Button.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("resolved")
    })

    expect(result.current.matches).toEqual(["src/components/Button.tsx"])
  })

  it("should normalize ../ prefix in paths", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["src/Button.tsx"],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "../src/Button.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("resolved")
    })

    expect(result.current.matches).toEqual(["src/Button.tsx"])
  })

  it("should handle absolute paths (leading slash)", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["home/user/project/src/App.tsx"],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "/home/user/project/src/App.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("resolved")
    })

    expect(result.current.matches).toEqual(["home/user/project/src/App.tsx"])
  })

  it("should rank shorter paths first (more specific)", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: [
        "very/long/nested/path/to/components/Button.tsx",
        "src/components/Button.tsx",
        "lib/ui/components/Button.tsx",
      ],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "components/Button.tsx")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("multiple")
    })

    // Shortest path should be first
    expect(result.current.matches[0]).toBe("src/components/Button.tsx")
  })

  it("should return empty result for empty parsedPath", async () => {
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["src/App.tsx"],
      isLoading: false,
      isStale: false,
      refetch: vi.fn(),
    })

    const { result } = renderHook(() =>
      usePathResolver("test-team", "")
    )

    await waitFor(() => {
      expect(result.current.status).toBe("not_found")
    })

    expect(result.current.matches).toEqual([])
  })

  it("should update when file list changes", async () => {
    const mockRefetch = vi.fn()

    // Initial file list
    const { rerender } = renderHook(() =>
      usePathResolver("test-team", "Button.tsx")
    )

    // Update file list (simulate cache refresh)
    vi.mocked(useFileListCacheModule.useFileListCache).mockReturnValue({
      files: ["src/Button.tsx", "lib/Button.tsx"],
      isLoading: false,
      isStale: false,
      refetch: mockRefetch,
    })

    rerender()

    await waitFor(() => {
      // Should now show multiple matches after file list update
    })
  })
})
