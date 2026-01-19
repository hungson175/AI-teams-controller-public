/**
 * Mock WebSocket for testing
 *
 * Provides a controllable WebSocket mock that:
 * - Tracks sent messages
 * - Allows triggering events (open, message, close, error)
 * - Simulates connection lifecycle
 */

import { vi } from "vitest"

export class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  // Track all instances for test assertions
  static instances: MockWebSocket[] = []

  url: string
  readyState: number = MockWebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  // Track sent messages for assertions
  sentMessages: (string | ArrayBuffer)[] = []

  // Mock functions for spying
  send = vi.fn((data: string | ArrayBuffer) => {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error("WebSocket is not open")
    }
    this.sentMessages.push(data)
  })

  close = vi.fn((code?: number, reason?: string) => {
    this.readyState = MockWebSocket.CLOSING
    setTimeout(() => {
      this.readyState = MockWebSocket.CLOSED
      this.onclose?.(new CloseEvent("close", { code: code || 1000, reason }))
    }, 0)
  })

  constructor(url: string) {
    this.url = url
    // Auto-open after a tick (simulates connection)
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      this.onopen?.(new Event("open"))
    }, 0)
  }

  // Helper methods for tests to trigger events
  simulateOpen(): void {
    this.readyState = MockWebSocket.OPEN
    this.onopen?.(new Event("open"))
  }

  simulateMessage(data: string | object): void {
    const messageData = typeof data === "object" ? JSON.stringify(data) : data
    this.onmessage?.(new MessageEvent("message", { data: messageData }))
  }

  simulateClose(code = 1000, reason = ""): void {
    this.readyState = MockWebSocket.CLOSED
    this.onclose?.(new CloseEvent("close", { code, reason }))
  }

  simulateError(): void {
    this.onerror?.(new Event("error"))
  }
}

// Instance tracking for test assertions
let wsInstances: MockWebSocket[] = []

export function getMockWebSocketInstances(): MockWebSocket[] {
  return wsInstances
}

export function getLastMockWebSocket(): MockWebSocket | undefined {
  return wsInstances[wsInstances.length - 1]
}

export function clearMockWebSocketInstances(): void {
  wsInstances = []
}

// Factory that tracks instances
export function createMockWebSocket(url: string): MockWebSocket {
  const ws = new MockWebSocket(url)
  wsInstances.push(ws)
  return ws
}

// Install mock globally
export function installWebSocketMock(): void {
  clearMockWebSocketInstances()
  MockWebSocket.instances = []
  ;(global as unknown as { WebSocket: typeof MockWebSocket }).WebSocket =
    class extends MockWebSocket {
      constructor(url: string) {
        super(url)
        wsInstances.push(this)
        MockWebSocket.instances.push(this)
      }
    }
}

// Restore original
export function uninstallWebSocketMock(): void {
  clearMockWebSocketInstances()
}

// Alias for resetWebSocketMock
export function resetWebSocketMock(): void {
  MockWebSocket.instances = []
  clearMockWebSocketInstances()
}
