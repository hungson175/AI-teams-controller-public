/**
 * Auth Utils Tests
 *
 * Tests for authentication header construction.
 * Written BEFORE extracting utility (TDD approach).
 */

import { describe, it, expect, vi, beforeEach } from "vitest"

// Mock getToken from @/lib/auth
const mockGetToken = vi.fn()
vi.mock("@/lib/auth", () => ({
  getToken: () => mockGetToken(),
}))

// Import after mock
import { getAuthHeaders } from "./auth-utils"

describe("getAuthHeaders", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("with valid token", () => {
    it("should return headers with Bearer token when token exists", () => {
      mockGetToken.mockReturnValue("test-token-123")

      const headers = getAuthHeaders()

      expect(headers).toEqual({
        "Authorization": "Bearer test-token-123",
        "Content-Type": "application/json",
      })
    })

    it("should include Authorization header", () => {
      mockGetToken.mockReturnValue("my-token")

      const headers = getAuthHeaders()

      expect(headers).toHaveProperty("Authorization")
      expect(headers.Authorization).toMatch(/^Bearer /)
    })

    it("should include Content-Type header", () => {
      mockGetToken.mockReturnValue("my-token")

      const headers = getAuthHeaders()

      expect(headers).toHaveProperty("Content-Type")
      expect(headers["Content-Type"]).toBe("application/json")
    })

    it("should handle long tokens", () => {
      const longToken = "a".repeat(500)
      mockGetToken.mockReturnValue(longToken)

      const headers = getAuthHeaders()

      expect(headers.Authorization).toBe(`Bearer ${longToken}`)
    })
  })

  describe("with missing or empty token", () => {
    it("should handle null token", () => {
      mockGetToken.mockReturnValue(null)

      const headers = getAuthHeaders()

      expect(headers.Authorization).toBe("Bearer null")
      expect(headers["Content-Type"]).toBe("application/json")
    })

    it("should handle undefined token", () => {
      mockGetToken.mockReturnValue(undefined)

      const headers = getAuthHeaders()

      expect(headers.Authorization).toBe("Bearer undefined")
      expect(headers["Content-Type"]).toBe("application/json")
    })

    it("should handle empty string token", () => {
      mockGetToken.mockReturnValue("")

      const headers = getAuthHeaders()

      expect(headers.Authorization).toBe("Bearer ")
      expect(headers["Content-Type"]).toBe("application/json")
    })
  })

  describe("return value structure", () => {
    it("should return an object with exactly 2 properties", () => {
      mockGetToken.mockReturnValue("token")

      const headers = getAuthHeaders()

      expect(Object.keys(headers)).toHaveLength(2)
    })

    it("should return a new object on each call (not cached)", () => {
      mockGetToken.mockReturnValue("token")

      const headers1 = getAuthHeaders()
      const headers2 = getAuthHeaders()

      // Should be different objects
      expect(headers1).not.toBe(headers2)
      // But equal values
      expect(headers1).toEqual(headers2)
    })

    it("should return Record<string, string> type", () => {
      mockGetToken.mockReturnValue("token")

      const headers = getAuthHeaders()

      // All values should be strings
      Object.values(headers).forEach((value) => {
        expect(typeof value).toBe("string")
      })
    })
  })

  describe("token changes", () => {
    it("should reflect token changes across calls", () => {
      mockGetToken.mockReturnValue("token1")
      const headers1 = getAuthHeaders()
      expect(headers1.Authorization).toBe("Bearer token1")

      mockGetToken.mockReturnValue("token2")
      const headers2 = getAuthHeaders()
      expect(headers2.Authorization).toBe("Bearer token2")
    })
  })
})
