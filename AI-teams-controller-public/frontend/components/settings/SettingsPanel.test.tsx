/**
 * SettingsPanel Tests
 *
 * Tests for the settings panel component with Apply button.
 * Sprint 25: Settings Apply Button
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"

// Mock useSettings
const mockUpdateSettings = vi.fn()
const mockSyncToServer = vi.fn()
const mockResetToDefaults = vi.fn()
const mockUseSettings = vi.fn()

vi.mock("@/contexts/SettingsContext", () => ({
  useSettings: () => mockUseSettings(),
  DEFAULT_SETTINGS: {
    detection_mode: "stopword",
    stop_word: "thank you",
    noise_filter_level: "medium",
    theme: "system",
    speech_speed: 0.58,
  },
}))

// Mock useAuth
const mockUseAuth = vi.fn()
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}))

// Import after mocks
import { SettingsPanel } from "./SettingsPanel"
import type { Settings } from "@/contexts/SettingsContext"

// Test data
const defaultSettings: Settings = {
  detection_mode: "stopword",
  stop_word: "thank you",
  noise_filter_level: "medium",
  theme: "system",
  speech_speed: 0.58,
}

describe("SettingsPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks()

    // Default mocks
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
    })

    mockUseSettings.mockReturnValue({
      settings: defaultSettings,
      isLoading: false,
      isSyncing: false,
      hasUnsavedChanges: false,
      error: null,
      updateSettings: mockUpdateSettings,
      syncToServer: mockSyncToServer.mockResolvedValue(true),
      resetToDefaults: mockResetToDefaults,
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ===========================================
  // Render Tests
  // ===========================================

  describe("rendering", () => {
    it("should render settings panel with all fields", () => {
      render(<SettingsPanel />)

      expect(screen.getByText("Voice Settings")).toBeInTheDocument()
      expect(screen.getByLabelText("Stop Word")).toBeInTheDocument()
      expect(screen.getByLabelText("Noise Filter Level")).toBeInTheDocument()
      expect(screen.getByLabelText("Theme")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /apply settings/i })).toBeInTheDocument()
    })

    it("should show loading state", () => {
      mockUseSettings.mockReturnValue({
        ...mockUseSettings(),
        isLoading: true,
      })

      render(<SettingsPanel />)

      // Should show loading spinner (Loader2 component)
      expect(screen.queryByText("Voice Settings")).not.toBeInTheDocument()
    })

    it("should show error message", () => {
      mockUseSettings.mockReturnValue({
        ...mockUseSettings(),
        settings: defaultSettings,
        isLoading: false,
        error: "Failed to save settings",
      })

      render(<SettingsPanel />)

      expect(screen.getByText("Failed to save settings")).toBeInTheDocument()
    })

    it("should show stop word field", () => {
      render(<SettingsPanel />)

      expect(screen.getByLabelText("Stop Word")).toBeInTheDocument()
    })

    it("should show unsaved changes indicator", async () => {
      render(<SettingsPanel />)

      // Change a setting via the select trigger
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      // Wait for dropdown and click option
      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      expect(screen.getByText("Unsaved changes")).toBeInTheDocument()
    })
  })

  // ===========================================
  // Apply Button Tests
  // ===========================================

  describe("apply button", () => {
    it("should be disabled when no changes", () => {
      render(<SettingsPanel />)

      const applyButton = screen.getByRole("button", { name: /apply settings/i })
      expect(applyButton).toBeDisabled()
    })

    it("should be enabled when there are changes", async () => {
      render(<SettingsPanel />)

      // Change a setting
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      const applyButton = screen.getByRole("button", { name: /apply settings/i })
      expect(applyButton).not.toBeDisabled()
    })

    it("should call updateSettings and syncToServer on apply", async () => {
      render(<SettingsPanel />)

      // Change a setting
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      // Click apply
      const applyButton = screen.getByRole("button", { name: /apply settings/i })
      fireEvent.click(applyButton)

      await waitFor(() => {
        expect(mockUpdateSettings).toHaveBeenCalled()
        expect(mockSyncToServer).toHaveBeenCalled()
      })
    })

    it("should dispatch settings-updated event on successful apply", async () => {
      const eventHandler = vi.fn()
      window.addEventListener("settings-updated", eventHandler)

      render(<SettingsPanel />)

      // Change a setting
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      // Click apply
      const applyButton = screen.getByRole("button", { name: /apply settings/i })
      fireEvent.click(applyButton)

      await waitFor(() => {
        expect(eventHandler).toHaveBeenCalled()
      })

      const event = eventHandler.mock.calls[0][0] as CustomEvent
      expect(event.detail.settings.theme).toBe("dark")

      window.removeEventListener("settings-updated", eventHandler)
    })

    it("should show success message after apply", async () => {
      render(<SettingsPanel />)

      // Change a setting
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      // Click apply
      const applyButton = screen.getByRole("button", { name: /apply settings/i })
      fireEvent.click(applyButton)

      await waitFor(() => {
        expect(screen.getByText("Settings applied")).toBeInTheDocument()
      })
    })

    it("should show saving state while syncing", async () => {
      mockSyncToServer.mockImplementation(() => new Promise(() => {})) // Never resolves

      render(<SettingsPanel />)

      // Change and apply
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      const applyButton = screen.getByRole("button", { name: /apply settings/i })
      fireEvent.click(applyButton)

      // Should update to show syncing state via context
      expect(mockSyncToServer).toHaveBeenCalled()
    })
  })

  // ===========================================
  // Cancel/Reset Tests
  // ===========================================

  describe("cancel and reset", () => {
    it("should show cancel button when there are changes", async () => {
      render(<SettingsPanel />)

      // Initially no cancel button
      expect(screen.queryByRole("button", { name: /cancel/i })).not.toBeInTheDocument()

      // Change a setting
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      // Cancel button should appear
      expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument()
    })

    it("should revert changes on cancel", async () => {
      render(<SettingsPanel />)

      // Change a setting
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      // Click cancel
      const cancelButton = screen.getByRole("button", { name: /cancel/i })
      fireEvent.click(cancelButton)

      // Should no longer show unsaved changes
      expect(screen.queryByText("Unsaved changes")).not.toBeInTheDocument()
    })

    it("should reset to defaults on reset button click", async () => {
      mockUseSettings.mockReturnValue({
        ...mockUseSettings(),
        settings: { ...defaultSettings, theme: "dark", stop_word: "custom" },
        isLoading: false,
      })

      render(<SettingsPanel />)

      // Click reset button (icon button with title)
      const resetButton = screen.getByTitle("Reset to defaults")
      fireEvent.click(resetButton)

      // Should show unsaved changes (local state reset to defaults)
      expect(screen.getByText("Unsaved changes")).toBeInTheDocument()
    })
  })

  // ===========================================
  // Auth State Tests
  // ===========================================

  describe("authentication state", () => {
    it("should show sign-in prompt when not authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
      })

      render(<SettingsPanel />)

      expect(screen.getByText(/sign in to sync settings/i)).toBeInTheDocument()
    })

    it("should still apply locally when not authenticated", async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
      })

      const eventHandler = vi.fn()
      window.addEventListener("settings-updated", eventHandler)

      render(<SettingsPanel />)

      // Change and apply
      const themeSelect = screen.getByLabelText("Theme")
      fireEvent.click(themeSelect)

      await waitFor(() => {
        const darkOption = screen.getByRole("option", { name: "Dark" })
        fireEvent.click(darkOption)
      })

      const applyButton = screen.getByRole("button", { name: /apply settings/i })
      fireEvent.click(applyButton)

      // Should still dispatch event
      await waitFor(() => {
        expect(eventHandler).toHaveBeenCalled()
      })

      // Should update settings (locally)
      expect(mockUpdateSettings).toHaveBeenCalled()

      window.removeEventListener("settings-updated", eventHandler)
    })
  })

  // ===========================================
  // Compact Mode Tests
  // ===========================================

  describe("compact mode", () => {
    it("should render in compact mode", () => {
      render(<SettingsPanel compact />)

      expect(screen.getByText("Voice Settings")).toBeInTheDocument()
      // Description should not be shown in compact mode
      expect(screen.queryByText(/configure voice detection/i)).not.toBeInTheDocument()
    })
  })
})
