/**
 * Mock fetch for testing
 *
 * Provides configurable fetch mock with:
 * - Route-based response mapping
 * - Request tracking for assertions
 * - Easy setup for common patterns
 */

import { vi } from "vitest"

export interface MockResponse {
  ok: boolean
  status: number
  statusText?: string
  json?: () => Promise<unknown>
  text?: () => Promise<string>
  body?: ReadableStream<Uint8Array> | null
  headers?: Headers
}

export interface FetchCall {
  url: string
  options?: RequestInit
  timestamp: number
}

// Track all fetch calls
let fetchCalls: FetchCall[] = []

// Route handlers
let routeHandlers: Map<string, (url: string, options?: RequestInit) => MockResponse> =
  new Map()

// Default response
let defaultResponse: MockResponse = {
  ok: true,
  status: 200,
  json: () => Promise.resolve({}),
  text: () => Promise.resolve(""),
}

/**
 * Create a mock fetch function
 */
export function createMockFetch() {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.toString()

    fetchCalls.push({ url, options: init, timestamp: Date.now() })

    // Check for matching route handler
    for (const [pattern, handler] of routeHandlers) {
      if (url.includes(pattern)) {
        return handler(url, init)
      }
    }

    return defaultResponse
  })
}

/**
 * Set up a route handler
 */
export function mockFetchRoute(
  urlPattern: string,
  response: Partial<MockResponse> | ((url: string, options?: RequestInit) => MockResponse)
): void {
  if (typeof response === "function") {
    routeHandlers.set(urlPattern, response)
  } else {
    routeHandlers.set(urlPattern, () => ({
      ok: response.ok ?? true,
      status: response.status ?? 200,
      statusText: response.statusText ?? "OK",
      json: response.json ?? (() => Promise.resolve({})),
      text: response.text ?? (() => Promise.resolve("")),
      body: response.body ?? null,
      headers: response.headers ?? new Headers(),
    }))
  }
}

/**
 * Set default response for unmatched routes
 */
export function setDefaultFetchResponse(response: Partial<MockResponse>): void {
  defaultResponse = {
    ...defaultResponse,
    ...response,
  }
}

/**
 * Get all fetch calls for assertions
 */
export function getFetchCalls(): FetchCall[] {
  return [...fetchCalls]
}

/**
 * Get the last fetch call
 */
export function getLastFetchCall(): FetchCall | undefined {
  return fetchCalls[fetchCalls.length - 1]
}

/**
 * Clear fetch call history and route handlers
 */
export function clearFetchMocks(): void {
  fetchCalls = []
  routeHandlers.clear()
  defaultResponse = {
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(""),
  }
}

/**
 * Install mock fetch globally
 */
export function installFetchMock(): void {
  clearFetchMocks()
  global.fetch = createMockFetch() as unknown as typeof fetch
}

/**
 * Common mock responses for this project
 */
export const mockResponses = {
  // Voice token endpoint
  voiceToken: (token = "mock-token-123") => ({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ api_key: token }),
  }),

  // Voice command endpoint with streaming
  voiceCommand: (correctedCommand = "corrected command") => ({
    ok: true,
    status: 200,
    body: new ReadableStream({
      start(controller) {
        const encoder = new TextEncoder()
        controller.enqueue(
          encoder.encode(
            JSON.stringify({ type: "llm_token", token: correctedCommand }) + "\n"
          )
        )
        controller.enqueue(
          encoder.encode(
            JSON.stringify({
              type: "command_sent",
              corrected_command: correctedCommand,
            }) + "\n"
          )
        )
        controller.close()
      },
    }),
  }),

  // Teams endpoint
  teams: (teams = [{ id: "team1", name: "Team 1" }]) => ({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ teams }),
  }),

  // Roles endpoint
  roles: (roles = [{ id: "pm", name: "PM" }]) => ({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ roles }),
  }),

  // Auth login
  authLogin: (token = "auth-token-xyz") => ({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ token }),
  }),

  // 401 Unauthorized
  unauthorized: () => ({
    ok: false,
    status: 401,
    json: () => Promise.resolve({ detail: "Unauthorized" }),
  }),

  // 500 Server Error
  serverError: () => ({
    ok: false,
    status: 500,
    json: () => Promise.resolve({ detail: "Internal server error" }),
  }),
}
