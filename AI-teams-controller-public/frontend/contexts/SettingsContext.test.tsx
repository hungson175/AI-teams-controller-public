/**
 * SettingsContext Tests
 *
 * Tests for the settings context provider.
 * Sprint 25: Frontend Settings Migration
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: () => {
      store = {}
    },
  }
})()

vi.stubGlobal("localStorage", localStorageMock)

// Mock fetch
const mockFetch = vi.fn()
vi.stubGlobal("fetch", mockFetch)

// Mock useAuth
const mockUseAuth = vi.fn()
vi.mock("./AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}))

// Mock getToken
vi.mock("@/lib/auth", () => ({
  getToken: () => localStorageMock.getItem("auth_access_token"),
}))

// Import after mocks
import {
  SettingsProvider,
  useSettings,
  DEFAULT_SETTINGS,
  type Settings,
  type SettingsResponse,
} from "./SettingsContext"

// Test data
const mockSettings: Settings = {
  detection_mode: "stopword",
  stop_word: "custom word",
  noise_filter_level: "high",
  theme: "dark",
}

const mockSettingsResponse: SettingsResponse = {
  ...mockSettings,
  updated_at: "2025-01-01T00:00:00Z",
}

// Helper wrapper
function createWrapper() {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <SettingsProvider>{children}</SettingsProvider>
  }
}

describe("SettingsContext", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
    // Default: not authenticated
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ===========================================
  // Provider Tests
  // ===========================================

  describe("SettingsProvider", () => {
    it("should throw error when useSettings is used outside provider", () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {})

      expect(() => {
        renderHook(() => useSettings())
      }).toThrow("useSettings must be used within SettingsProvider")

      consoleSpy.mockRestore()
    })

    it("should initialize with defaults when no localStorage and not authenticated", async () => {
      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      expect(result.current.settings).toEqual(DEFAULT_SETTINGS)
      expect(result.current.hasUnsavedChanges).toBe(false)
    })

    it("should load from localStorage when not authenticated", async () => {
      // Set legacy localStorage keys
      localStorageMock.setItem("voice-detection-mode", "stopword")
      localStorageMock.setItem("voice-stop-word", "test word")
      localStorageMock.setItem("voice-noise-filter", "high")

      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      expect(result.current.settings.detection_mode).toBe("stopword")
      expect(result.current.settings.stop_word).toBe("test word")
      expect(result.current.settings.noise_filter_level).toBe("high")
    })

    it("should load from server when authenticated", async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
      })
      localStorageMock.setItem("auth_access_token", "valid-token")

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockSettingsResponse),
      })

      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      expect(result.current.settings).toEqual(mockSettings)
      expect(result.current.lastSynced).not.toBeNull()
    })
  })

  // ===========================================
  // Migration Tests
  // ===========================================

  describe("localStorage migration", () => {
    it("should migrate localStorage to server on first login", async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
      })
      localStorageMock.setItem("auth_access_token", "valid-token")

      // Set legacy localStorage
      localStorageMock.setItem("voice-detection-mode", "stopword")
      localStorageMock.setItem("voice-stop-word", "migrate me")
      localStorageMock.setItem("voice-noise-filter", "low")

      // Server returns 404 or empty (no settings yet)
      mockFetch
        .mockResolvedValueOnce({
          ok: false,
          status: 404,
        })
        // Then save succeeds
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: () => Promise.resolve({}),
        })

      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      // Should have migrated localStorage values
      expect(result.current.settings.detection_mode).toBe("stopword")
      expect(result.current.settings.stop_word).toBe("migrate me")
      expect(result.current.settings.noise_filter_level).toBe("low")

      // Should have called PUT to save
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/settings"),
        expect.objectContaining({ method: "PUT" })
      )
    })

    it("should migrate deprecated 'go go go' stopword to 'thank you'", async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
      })
      localStorageMock.setItem("auth_access_token", "valid-token")

      // Server returns settings with deprecated stopword
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: () => Promise.resolve({
            detection_mode: "stopword",
            stop_word: "go go go",  // Deprecated value
            noise_filter_level: "medium",
            theme: "system",
            updated_at: "2025-01-01T00:00:00Z",
          }),
        })
        // Then save succeeds (migration persisted)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: () => Promise.resolve({}),
        })

      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      // Should have migrated to "thank you"
      expect(result.current.settings.stop_word).toBe("thank you")

      // Should have called PUT to persist migration
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/settings"),
        expect.objectContaining({ method: "PUT" })
      )
    })
  })

  // ===========================================
  // Update Tests
  // ===========================================

  describe("updateSetting", () => {
    it("should update single setting and save to localStorage", async () => {
      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      act(() => {
        result.current.updateSetting("theme", "dark")
      })

      expect(result.current.settings.theme).toBe("dark")
      expect(result.current.hasUnsavedChanges).toBe(true)
      expect(localStorageMock.setItem).toHaveBeenCalled()
    })

    it("should update detection_mode", async () => {
      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      act(() => {
        result.current.updateSetting("detection_mode", "stopword")
      })

      expect(result.current.settings.detection_mode).toBe("stopword")
    })
  })

  describe("updateSettings", () => {
    it("should update multiple settings at once", async () => {
      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      act(() => {
        result.current.updateSettings({
          theme: "light",
          stop_word: "new word",
        })
      })

      expect(result.current.settings.theme).toBe("light")
      expect(result.current.settings.stop_word).toBe("new word")
      expect(result.current.hasUnsavedChanges).toBe(true)
    })
  })

  // ===========================================
  // Sync Tests
  // ===========================================

  describe("syncToServer", () => {
    it("should sync settings to server when authenticated", async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
      })
      localStorageMock.setItem("auth_access_token", "valid-token")

      // Initial load
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockSettingsResponse),
      })

      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      // Update setting
      act(() => {
        result.current.updateSetting("theme", "light")
      })

      expect(result.current.hasUnsavedChanges).toBe(true)

      // Mock sync response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
      })

      // Manually sync
      await act(async () => {
        const success = await result.current.syncToServer()
        expect(success).toBe(true)
      })

      expect(result.current.hasUnsavedChanges).toBe(false)
      expect(result.current.lastSynced).not.toBeNull()
    })

    it("should return false when not authenticated", async () => {
      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      await act(async () => {
        const success = await result.current.syncToServer()
        expect(success).toBe(false)
      })

      expect(result.current.error).toBe("Not authenticated")
    })

    it("should set error on sync failure", async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
      })
      localStorageMock.setItem("auth_access_token", "valid-token")

      // Initial load fails
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      // Update and try to sync
      act(() => {
        result.current.updateSetting("theme", "dark")
      })

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      await act(async () => {
        const success = await result.current.syncToServer()
        expect(success).toBe(false)
      })

      expect(result.current.error).toBe("Failed to save settings")
    })
  })

  // ===========================================
  // Reset Tests
  // ===========================================

  describe("resetToDefaults", () => {
    it("should reset all settings to defaults", async () => {
      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      // Change some settings
      act(() => {
        result.current.updateSettings({
          theme: "dark",
          stop_word: "custom",
          detection_mode: "stopword",
        })
      })

      expect(result.current.settings.theme).toBe("dark")

      // Reset
      act(() => {
        result.current.resetToDefaults()
      })

      expect(result.current.settings).toEqual(DEFAULT_SETTINGS)
      expect(result.current.hasUnsavedChanges).toBe(true)
    })
  })

  // ===========================================
  // Legacy Key Compatibility Tests
  // ===========================================

  describe("legacy localStorage keys", () => {
    it("should update legacy keys when settings change", async () => {
      const { result } = renderHook(() => useSettings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      act(() => {
        result.current.updateSetting("stop_word", "new phrase")
      })

      // Check legacy key was updated
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "voice-stop-word",
        "new phrase"
      )
    })
  })
})
