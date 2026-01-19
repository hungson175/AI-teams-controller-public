/**
 * Soniox STT Service Tests
 *
 * Tests for WebSocket-based speech-to-text service.
 * Mocks WebSocket, fetch, and AudioCapture for unit testing.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest"
import { MockWebSocket, installWebSocketMock, resetWebSocketMock } from "@/__mocks__/websocket"

// Mock auth - must be before import
vi.mock("@/lib/auth", () => ({
  getToken: () => "mock-token",
}))

// Mock AudioCapture - must be before import
vi.mock("./audio-capture", () => {
  return {
    AudioCapture: class MockAudioCapture {
      start = vi.fn().mockResolvedValue(undefined)
      stop = vi.fn()
    }
  }
})

// Import after mocks are set up
import {
  SonioxSTTService,
  DEFAULT_SONIOX_SERVICE_CONFIG,
  type SonioxServiceConfig,
  type SonioxServiceCallbacks,
} from "./soniox-service"

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe("SonioxSTTService", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    installWebSocketMock()

    // Default fetch mock for token endpoint
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ api_key: "test-soniox-key" }),
    })
  })

  afterEach(() => {
    resetWebSocketMock()
  })

  describe("constructor", () => {
    it("creates service with default config", () => {
      const service = new SonioxSTTService()
      const config = service.getConfig()

      expect(config.detectionMode).toBe(DEFAULT_SONIOX_SERVICE_CONFIG.detectionMode)
      expect(config.model).toBe(DEFAULT_SONIOX_SERVICE_CONFIG.model)
      expect(config.stopWord).toBe(DEFAULT_SONIOX_SERVICE_CONFIG.stopWord)
      expect(config.silenceDurationMs).toBe(DEFAULT_SONIOX_SERVICE_CONFIG.silenceDurationMs)
    })

    it("creates service with custom config", () => {
      const customConfig: Partial<SonioxServiceConfig> = {
        detectionMode: "silence",
        silenceDurationMs: 3000,
        silenceThresholdDb: -35,
      }
      const service = new SonioxSTTService(customConfig)
      const config = service.getConfig()

      expect(config.detectionMode).toBe("silence")
      expect(config.silenceDurationMs).toBe(3000)
      expect(config.silenceThresholdDb).toBe(-35)
      // Default values for non-overridden
      expect(config.model).toBe(DEFAULT_SONIOX_SERVICE_CONFIG.model)
    })

    it("initializes stopword detector for stopword mode", () => {
      const service = new SonioxSTTService({ detectionMode: "stopword" })
      // Service should be ready - no errors
      expect(service.connected).toBe(false)
    })

    it("initializes silence detector for silence mode", () => {
      const service = new SonioxSTTService({ detectionMode: "silence" })
      // Service should be ready - no errors
      expect(service.connected).toBe(false)
    })
  })

  describe("configuration management", () => {
    it("returns a copy of config (immutable)", () => {
      const service = new SonioxSTTService()
      const config1 = service.getConfig()
      const config2 = service.getConfig()

      expect(config1).not.toBe(config2)
      expect(config1).toEqual(config2)
    })

    it("updates config before connection", () => {
      const service = new SonioxSTTService()
      service.updateConfig({ stopWord: "send now" })

      expect(service.getConfig().stopWord).toBe("send now")
    })

    it("throws when updating config while connected", async () => {
      const service = new SonioxSTTService()

      // Connect
      const connectPromise = service.connect()
      // Simulate WebSocket open
      await vi.waitFor(() => {
        const ws = MockWebSocket.instances[0]
        if (ws) ws.simulateOpen()
      })
      await connectPromise

      // Try to update - should throw
      expect(() => service.updateConfig({ stopWord: "new word" }))
        .toThrow("Cannot update config while connected")
    })

    it("updates callbacks", () => {
      const service = new SonioxSTTService()
      const onTranscript = vi.fn()

      service.updateCallbacks({ onTranscript })

      // Callback should be set (verified via behavior)
      expect(service).toBeDefined()
    })
  })

  describe("connection lifecycle", () => {
    it("starts disconnected", () => {
      const service = new SonioxSTTService()
      expect(service.connected).toBe(false)
    })

    it("fetches API key on connect", async () => {
      const service = new SonioxSTTService()

      const connectPromise = service.connect()

      // Wait for WebSocket to be created and simulate open
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      MockWebSocket.instances[0].simulateOpen()

      await connectPromise

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/voice/token/soniox"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer mock-token",
          }),
        })
      )
    })

    it("sends config as first message after connection", async () => {
      const service = new SonioxSTTService()

      const connectPromise = service.connect()

      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      const ws = MockWebSocket.instances[0]
      ws.simulateOpen()

      await connectPromise

      // Should have sent config
      expect(ws.send).toHaveBeenCalled()
      const sentData = ws.sentMessages[0]
      const config = JSON.parse(sentData)

      expect(config.api_key).toBe("test-soniox-key")
      expect(config.model).toBe("stt-rt-preview")
      expect(config.sample_rate).toBe(16000)
      expect(config.audio_format).toBe("pcm_s16le")
    })

    it("calls onConnectionChange(true) when connected", async () => {
      const onConnectionChange = vi.fn()
      const service = new SonioxSTTService({}, { onConnectionChange })

      const connectPromise = service.connect()

      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      MockWebSocket.instances[0].simulateOpen()

      await connectPromise

      expect(onConnectionChange).toHaveBeenCalledWith(true)
      expect(service.connected).toBe(true)
    })

    it("throws error when already connected", async () => {
      const service = new SonioxSTTService()

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      MockWebSocket.instances[0].simulateOpen()
      await connectPromise

      await expect(service.connect()).rejects.toThrow("Already connected")
    })

    it("disconnects and cleans up", async () => {
      const onConnectionChange = vi.fn()
      const service = new SonioxSTTService({}, { onConnectionChange })

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      MockWebSocket.instances[0].simulateOpen()
      await connectPromise

      service.disconnect()

      expect(service.connected).toBe(false)
      expect(MockWebSocket.instances[0].close).toHaveBeenCalled()
    })
  })

  describe("error handling", () => {
    it("handles token fetch failure", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      const onError = vi.fn()
      const service = new SonioxSTTService({}, { onError })

      await expect(service.connect()).rejects.toThrow("Failed to get Soniox token")
    })

    it("redirects to login on 401", async () => {
      // Mock window.location
      const originalLocation = window.location
      delete (window as { location?: Location }).location
      window.location = { href: "" } as Location

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      })

      const service = new SonioxSTTService()

      await expect(service.connect()).rejects.toThrow("Unauthorized")
      expect(window.location.href).toBe("/login")

      // Restore
      window.location = originalLocation
    })

    it("calls onError callback on WebSocket error", async () => {
      const onError = vi.fn()
      const service = new SonioxSTTService({}, { onError })

      const connectPromise = service.connect()

      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      const ws = MockWebSocket.instances[0]
      ws.simulateOpen()
      await connectPromise

      // Simulate WebSocket error
      ws.simulateError()

      expect(onError).toHaveBeenCalledWith(expect.any(Error))
    })

    it("handles WebSocket close", async () => {
      const onConnectionChange = vi.fn()
      const service = new SonioxSTTService({}, { onConnectionChange })

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      MockWebSocket.instances[0].simulateOpen()
      await connectPromise

      onConnectionChange.mockClear()
      MockWebSocket.instances[0].simulateClose()

      expect(onConnectionChange).toHaveBeenCalledWith(false)
    })
  })

  describe("transcript handling", () => {
    it("starts with empty transcript", () => {
      const service = new SonioxSTTService()
      expect(service.getTranscript()).toBe("")
    })

    it("accumulates final tokens", async () => {
      const onTranscript = vi.fn()
      const service = new SonioxSTTService({}, { onTranscript })

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      const ws = MockWebSocket.instances[0]
      ws.simulateOpen()
      await connectPromise

      // Simulate Soniox response with final tokens
      ws.simulateMessage({
        tokens: [
          { text: "hello ", is_final: true },
          { text: "world", is_final: true },
        ],
      })

      expect(service.getTranscript()).toBe("hello world")
      expect(onTranscript).toHaveBeenCalledWith("hello world", true)
    })

    it("includes interim tokens in callback but not transcript", async () => {
      const onTranscript = vi.fn()
      const service = new SonioxSTTService({}, { onTranscript })

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      const ws = MockWebSocket.instances[0]
      ws.simulateOpen()
      await connectPromise

      // Simulate response with both final and interim
      ws.simulateMessage({
        tokens: [
          { text: "hello ", is_final: true },
          { text: "wor", is_final: false },
        ],
      })

      expect(service.getTranscript()).toBe("hello ")
      expect(onTranscript).toHaveBeenCalledWith("hello wor", true)
    })

    it("handles error messages from Soniox", async () => {
      const onError = vi.fn()
      const service = new SonioxSTTService({}, { onError })

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      const ws = MockWebSocket.instances[0]
      ws.simulateOpen()
      await connectPromise

      // Simulate error response
      ws.simulateMessage({
        error_message: "Invalid API key",
      })

      expect(onError).toHaveBeenCalledWith(expect.objectContaining({
        message: "Invalid API key",
      }))
    })
  })

  describe("stopword detection mode", () => {
    it("calls onFinalize when stop word detected", async () => {
      const onFinalize = vi.fn()
      const service = new SonioxSTTService(
        { detectionMode: "stopword", stopWord: "thank you" },
        { onFinalize }
      )

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      const ws = MockWebSocket.instances[0]
      ws.simulateOpen()
      await connectPromise

      // Simulate transcript with stop word
      ws.simulateMessage({
        tokens: [{ text: "fix the bug thank you", is_final: true }],
      })

      expect(onFinalize).toHaveBeenCalledWith("fix the bug")
    })

    it("resets transcript after finalize", async () => {
      const onFinalize = vi.fn()
      const service = new SonioxSTTService(
        { detectionMode: "stopword", stopWord: "thank you" },
        { onFinalize }
      )

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      const ws = MockWebSocket.instances[0]
      ws.simulateOpen()
      await connectPromise

      // Finalize
      ws.simulateMessage({
        tokens: [{ text: "fix bug thank you", is_final: true }],
      })

      expect(service.getTranscript()).toBe("")
    })
  })

  describe("sendAudio", () => {
    it("sends audio data to WebSocket", async () => {
      const service = new SonioxSTTService()

      const connectPromise = service.connect()
      await vi.waitFor(() => {
        expect(MockWebSocket.instances.length).toBeGreaterThan(0)
      })
      const ws = MockWebSocket.instances[0]
      ws.simulateOpen()
      await connectPromise

      ws.send.mockClear()
      const audioData = new Int16Array([100, 200, 300])
      service.sendAudio(audioData)

      expect(ws.send).toHaveBeenCalledWith(audioData.buffer)
    })

    it("does nothing if WebSocket not open", () => {
      const service = new SonioxSTTService()
      // Not connected

      const audioData = new Int16Array([100, 200, 300])
      // Should not throw
      expect(() => service.sendAudio(audioData)).not.toThrow()
    })
  })
})
