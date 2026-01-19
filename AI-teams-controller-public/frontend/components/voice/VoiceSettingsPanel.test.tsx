import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { VoiceSettingsPanel } from "./VoiceSettingsPanel"

// Mock ResizeObserver (required by Radix UI Slider)
class ResizeObserverMock {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
}
global.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    clear: () => {
      store = {}
    },
  }
})()

vi.stubGlobal("localStorage", localStorageMock)

describe("VoiceSettingsPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ===========================================
  // Render Tests
  // ===========================================

  describe("rendering", () => {
    it("should render settings panel with header", () => {
      render(<VoiceSettingsPanel />)
      expect(screen.getByText("Voice Settings")).toBeInTheDocument()
    })

    it("should start collapsed by default", () => {
      render(<VoiceSettingsPanel />)
      expect(screen.queryByLabelText("Noise filter level")).not.toBeInTheDocument()
    })

    it("should start expanded when defaultExpanded is true", () => {
      render(<VoiceSettingsPanel defaultExpanded />)
      expect(screen.getByLabelText("Noise filter level")).toBeInTheDocument()
    })

    it("should show current noise level in header", () => {
      render(<VoiceSettingsPanel />)
      expect(screen.getByText(/Noise: Medium/)).toBeInTheDocument()
    })

    it("should show compact mode toggle button", () => {
      render(<VoiceSettingsPanel compact />)
      expect(screen.getByLabelText("Open voice settings")).toBeInTheDocument()
    })
  })

  // ===========================================
  // Expand/Collapse Tests
  // ===========================================

  describe("expand and collapse", () => {
    it("should expand when header is clicked", () => {
      render(<VoiceSettingsPanel />)

      const header = screen.getByRole("button", { expanded: false })
      fireEvent.click(header)

      expect(screen.getByLabelText("Noise filter level")).toBeInTheDocument()
    })

    it("should collapse when header is clicked while expanded", () => {
      render(<VoiceSettingsPanel defaultExpanded />)

      const header = screen.getByRole("button", { expanded: true })
      fireEvent.click(header)

      expect(screen.queryByLabelText("Noise filter level")).not.toBeInTheDocument()
    })

    it("should show chevron down when collapsed", () => {
      render(<VoiceSettingsPanel />)
      // Check for the collapsed state by looking for aria-expanded=false
      expect(screen.getByRole("button", { expanded: false })).toBeInTheDocument()
    })

    it("should show chevron up when expanded", () => {
      render(<VoiceSettingsPanel defaultExpanded />)
      expect(screen.getByRole("button", { expanded: true })).toBeInTheDocument()
    })
  })

  // ===========================================
  // Noise Filter Slider Tests
  // ===========================================

  describe("noise filter slider", () => {
    it("should show noise filter label when expanded", () => {
      render(<VoiceSettingsPanel defaultExpanded />)
      expect(screen.getByText("Noise Filter")).toBeInTheDocument()
    })

    it("should show level description when expanded", () => {
      render(<VoiceSettingsPanel defaultExpanded />)
      expect(screen.getByText(/Balanced - normal environments/)).toBeInTheDocument()
    })

    it("should show Very Low and Very High labels", () => {
      render(<VoiceSettingsPanel defaultExpanded />)
      expect(screen.getByText("Very Low")).toBeInTheDocument()
      expect(screen.getByText("Very High")).toBeInTheDocument()
    })

    it("should load level from localStorage on mount", () => {
      localStorageMock.setItem("voice-noise-filter", "high")
      render(<VoiceSettingsPanel defaultExpanded />)
      expect(screen.getByText(/Noise: High/)).toBeInTheDocument()
    })
  })

  // ===========================================
  // Event Dispatch Tests
  // ===========================================

  describe("event dispatch", () => {
    it("should dispatch noise-filter-changed event when slider changes", async () => {
      const eventHandler = vi.fn()
      window.addEventListener("noise-filter-changed", eventHandler)

      render(<VoiceSettingsPanel defaultExpanded />)

      const slider = screen.getByRole("slider")
      // Move slider to position 4 (very-high)
      fireEvent.keyDown(slider, { key: "ArrowRight" })
      fireEvent.keyDown(slider, { key: "ArrowRight" })

      await waitFor(() => {
        expect(eventHandler).toHaveBeenCalled()
      })

      window.removeEventListener("noise-filter-changed", eventHandler)
    })

    it("should save to localStorage when slider changes", async () => {
      render(<VoiceSettingsPanel defaultExpanded />)

      const slider = screen.getByRole("slider")
      // Move slider to the right (higher level)
      fireEvent.keyDown(slider, { key: "ArrowRight" })

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          "voice-noise-filter",
          expect.any(String)
        )
      })
    })

    it("should call onSettingsChange callback when slider changes", async () => {
      const onSettingsChange = vi.fn()
      render(<VoiceSettingsPanel defaultExpanded onSettingsChange={onSettingsChange} />)

      const slider = screen.getByRole("slider")
      fireEvent.keyDown(slider, { key: "ArrowRight" })

      await waitFor(() => {
        expect(onSettingsChange).toHaveBeenCalled()
      })
    })
  })

  // ===========================================
  // Settings Integration Tests
  // ===========================================

  describe("settings integration", () => {
    it("should update level when settings-updated event is received", async () => {
      render(<VoiceSettingsPanel defaultExpanded />)

      // Initially medium
      expect(screen.getByText(/Noise: Medium/)).toBeInTheDocument()

      // Dispatch settings-updated event with new level
      window.dispatchEvent(new CustomEvent("settings-updated", {
        detail: { settings: { noise_filter_level: "high" } },
      }))

      await waitFor(() => {
        expect(screen.getByText(/Noise: High/)).toBeInTheDocument()
      })
    })

    it("should dispatch noise-filter-changed when settings-updated is received", async () => {
      const eventHandler = vi.fn()
      window.addEventListener("noise-filter-changed", eventHandler)

      render(<VoiceSettingsPanel defaultExpanded />)

      // Dispatch settings-updated event
      window.dispatchEvent(new CustomEvent("settings-updated", {
        detail: { settings: { noise_filter_level: "very-high" } },
      }))

      await waitFor(() => {
        expect(eventHandler).toHaveBeenCalled()
      })

      const event = eventHandler.mock.calls[0][0] as CustomEvent
      expect(event.detail.level).toBe("very-high")
      expect(event.detail.dbThreshold).toBe(-30)

      window.removeEventListener("noise-filter-changed", eventHandler)
    })
  })

  // ===========================================
  // Compact Mode Tests
  // ===========================================

  describe("compact mode", () => {
    it("should show only toggle button in compact mode", () => {
      render(<VoiceSettingsPanel compact />)
      expect(screen.getByLabelText("Open voice settings")).toBeInTheDocument()
      expect(screen.queryByText("Voice Settings")).not.toBeInTheDocument()
    })

    it("should show current level in compact button", () => {
      render(<VoiceSettingsPanel compact />)
      expect(screen.getByText("Medium")).toBeInTheDocument()
    })

    it("should expand when compact button is clicked", () => {
      render(<VoiceSettingsPanel compact />)

      const button = screen.getByLabelText("Open voice settings")
      fireEvent.click(button)

      expect(screen.getByText("Voice Settings")).toBeInTheDocument()
    })
  })
})
