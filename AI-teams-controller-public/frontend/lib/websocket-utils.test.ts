/**
 * WebSocket Utils Tests
 *
 * Tests for WebSocket URL resolution logic.
 * Written BEFORE extracting utility (TDD approach).
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest"
import { getWebSocketBaseUrl } from "./websocket-utils"

describe("getWebSocketBaseUrl", () => {
  let originalWindow: typeof window

  beforeEach(() => {
    originalWindow = global.window
  })

  afterEach(() => {
    global.window = originalWindow
  })

  describe("SSR environment", () => {
    it("should return ws://localhost:17061 when window is undefined", () => {
      // Simulate SSR (no window)
      // @ts-expect-error - intentionally setting window to undefined for SSR test
      global.window = undefined

      const result = getWebSocketBaseUrl()
      expect(result).toBe("ws://localhost:17061")
    })
  })

  describe("production environment", () => {
    it("should return wss://voice-backend.hungson175.com for production hostname", () => {
      // Mock production hostname
      global.window = {
        ...originalWindow,
        location: {
          ...originalWindow.location,
          hostname: "voice-ui.hungson175.com",
        },
      } as Window & typeof globalThis

      const result = getWebSocketBaseUrl()
      expect(result).toBe("wss://voice-backend.hungson175.com")
    })

    it("should use secure WebSocket (wss) for production", () => {
      global.window = {
        ...originalWindow,
        location: {
          ...originalWindow.location,
          hostname: "voice-ui.hungson175.com",
        },
      } as Window & typeof globalThis

      const result = getWebSocketBaseUrl()
      expect(result).toMatch(/^wss:/)
    })
  })

  describe("localhost environment", () => {
    it("should return ws://localhost:17061 for localhost", () => {
      global.window = {
        ...originalWindow,
        location: {
          ...originalWindow.location,
          hostname: "localhost",
        },
      } as Window & typeof globalThis

      const result = getWebSocketBaseUrl()
      expect(result).toBe("ws://localhost:17061")
    })

    it("should return ws://localhost:17061 for 127.0.0.1", () => {
      global.window = {
        ...originalWindow,
        location: {
          ...originalWindow.location,
          hostname: "127.0.0.1",
        },
      } as Window & typeof globalThis

      const result = getWebSocketBaseUrl()
      expect(result).toBe("ws://localhost:17061")
    })
  })

  describe("unknown hostname", () => {
    it("should default to ws://localhost:17061 for unknown hostnames", () => {
      global.window = {
        ...originalWindow,
        location: {
          ...originalWindow.location,
          hostname: "some-random-host.com",
        },
      } as Window & typeof globalThis

      const result = getWebSocketBaseUrl()
      expect(result).toBe("ws://localhost:17061")
    })

    it("should use insecure WebSocket (ws) for non-production hostnames", () => {
      global.window = {
        ...originalWindow,
        location: {
          ...originalWindow.location,
          hostname: "staging.example.com",
        },
      } as Window & typeof globalThis

      const result = getWebSocketBaseUrl()
      expect(result).toMatch(/^ws:/)
      expect(result).not.toMatch(/^wss:/)
    })
  })

  describe("edge cases", () => {
    it("should handle empty hostname gracefully", () => {
      global.window = {
        ...originalWindow,
        location: {
          ...originalWindow.location,
          hostname: "",
        },
      } as Window & typeof globalThis

      const result = getWebSocketBaseUrl()
      expect(result).toBe("ws://localhost:17061")
    })
  })
})
