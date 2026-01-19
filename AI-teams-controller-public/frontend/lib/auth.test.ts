/**
 * Auth Library Tests
 *
 * Tests for token storage and API functions in lib/auth.ts
 * Sprint 25: Frontend Auth Migration
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"

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

// Import after mocks
import {
  getToken,
  getRefreshToken,
  setToken,
  setTokens,
  removeToken,
  removeTokens,
  isAuthenticated,
  login,
  register,
  refreshTokens,
  getMe,
  logout,
  tryRefreshTokens,
  type User,
  type AuthTokens,
  type LoginResponse,
  type RegisterResponse,
  type RefreshResponse,
  type MeResponse,
} from "./auth"

describe("lib/auth", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ===========================================
  // Token Storage Tests
  // ===========================================

  describe("token storage", () => {
    describe("getToken", () => {
      it("should return null when no token stored", () => {
        expect(getToken()).toBeNull()
      })

      it("should return stored access token", () => {
        localStorageMock.setItem("auth_access_token", "test-token")
        expect(getToken()).toBe("test-token")
      })
    })

    describe("getRefreshToken", () => {
      it("should return null when no refresh token stored", () => {
        expect(getRefreshToken()).toBeNull()
      })

      it("should return stored refresh token", () => {
        localStorageMock.setItem("auth_refresh_token", "refresh-token")
        expect(getRefreshToken()).toBe("refresh-token")
      })
    })

    describe("setToken", () => {
      it("should store access token in localStorage", () => {
        setToken("my-token")
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          "auth_access_token",
          "my-token"
        )
      })
    })

    describe("setTokens", () => {
      it("should store both tokens in localStorage", () => {
        const tokens: AuthTokens = {
          access_token: "access-123",
          refresh_token: "refresh-456",
          token_type: "bearer",
        }
        setTokens(tokens)
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          "auth_access_token",
          "access-123"
        )
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          "auth_refresh_token",
          "refresh-456"
        )
      })
    })

    describe("removeToken", () => {
      it("should remove all tokens from localStorage", () => {
        removeToken()
        expect(localStorageMock.removeItem).toHaveBeenCalledWith(
          "auth_access_token"
        )
        expect(localStorageMock.removeItem).toHaveBeenCalledWith(
          "auth_refresh_token"
        )
      })
    })

    describe("removeTokens", () => {
      it("should remove both tokens from localStorage", () => {
        removeTokens()
        expect(localStorageMock.removeItem).toHaveBeenCalledWith(
          "auth_access_token"
        )
        expect(localStorageMock.removeItem).toHaveBeenCalledWith(
          "auth_refresh_token"
        )
      })
    })

    describe("isAuthenticated", () => {
      it("should return false when no token", () => {
        expect(isAuthenticated()).toBe(false)
      })

      it("should return true when token exists", () => {
        localStorageMock.setItem("auth_access_token", "test-token")
        expect(isAuthenticated()).toBe(true)
      })
    })
  })

  // ===========================================
  // API Function Tests
  // ===========================================

  describe("API functions", () => {
    const mockUser: User = {
      id: 1,
      email: "test@example.com",
      username: "testuser",
      is_active: true,
      created_at: "2025-01-01T00:00:00Z",
    }

    const mockTokens: AuthTokens = {
      access_token: "access-token-123",
      refresh_token: "refresh-token-456",
      token_type: "bearer",
    }

    describe("login", () => {
      it("should send login request and return user with tokens", async () => {
        const response: LoginResponse = {
          user: mockUser,
          tokens: mockTokens,
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(response),
        })

        const result = await login({ email: "test@example.com", password: "password" })

        expect(mockFetch).toHaveBeenCalledWith(
          "http://localhost:17061/api/auth/login",
          expect.objectContaining({
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: "test@example.com", password: "password" }),
          })
        )
        expect(result).toEqual(response)
      })

      it("should throw error on login failure", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({ detail: "Invalid credentials" }),
        })

        await expect(
          login({ email: "test@example.com", password: "wrong" })
        ).rejects.toThrow("Invalid credentials")
      })
    })

    describe("register", () => {
      it("should send register request and return user with tokens", async () => {
        const response: RegisterResponse = {
          user: mockUser,
          tokens: mockTokens,
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(response),
        })

        const result = await register({
          email: "test@example.com",
          username: "testuser",
          password: "password123",
        })

        expect(mockFetch).toHaveBeenCalledWith(
          "http://localhost:17061/api/auth/register",
          expect.objectContaining({
            method: "POST",
            body: JSON.stringify({
              email: "test@example.com",
              username: "testuser",
              password: "password123",
            }),
          })
        )
        expect(result).toEqual(response)
      })

      it("should throw error on registration failure", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({ detail: "Email already registered" }),
        })

        await expect(
          register({
            email: "test@example.com",
            username: "testuser",
            password: "password",
          })
        ).rejects.toThrow("Email already registered")
      })
    })

    describe("refreshTokens", () => {
      it("should send refresh request and return new tokens", async () => {
        const response: RefreshResponse = {
          tokens: mockTokens,
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(response),
        })

        const result = await refreshTokens("old-refresh-token")

        expect(mockFetch).toHaveBeenCalledWith(
          "http://localhost:17061/api/auth/refresh",
          expect.objectContaining({
            method: "POST",
            body: JSON.stringify({ refresh_token: "old-refresh-token" }),
          })
        )
        expect(result).toEqual(response)
      })

      it("should throw error on refresh failure", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({ detail: "Invalid refresh token" }),
        })

        await expect(refreshTokens("invalid-token")).rejects.toThrow(
          "Invalid refresh token"
        )
      })
    })

    describe("getMe", () => {
      it("should fetch current user with auth header", async () => {
        localStorageMock.setItem("auth_access_token", "my-token")
        const response: MeResponse = { user: mockUser }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(response),
        })

        const result = await getMe()

        expect(mockFetch).toHaveBeenCalledWith(
          "http://localhost:17061/api/auth/me",
          expect.objectContaining({
            method: "GET",
            headers: { Authorization: "Bearer my-token" },
          })
        )
        expect(result).toEqual(response)
      })

      it("should throw error when not authenticated", async () => {
        await expect(getMe()).rejects.toThrow("Not authenticated")
      })

      it("should throw error on fetch failure", async () => {
        localStorageMock.setItem("auth_access_token", "my-token")

        mockFetch.mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({ detail: "Invalid token" }),
        })

        await expect(getMe()).rejects.toThrow("Invalid token")
      })
    })

    describe("logout", () => {
      it("should remove all tokens", () => {
        localStorageMock.setItem("auth_access_token", "token")
        localStorageMock.setItem("auth_refresh_token", "refresh")

        logout()

        expect(localStorageMock.removeItem).toHaveBeenCalledWith("auth_access_token")
        expect(localStorageMock.removeItem).toHaveBeenCalledWith("auth_refresh_token")
      })
    })

    describe("tryRefreshTokens", () => {
      it("should return false when no refresh token", async () => {
        const result = await tryRefreshTokens()
        expect(result).toBe(false)
      })

      it("should refresh and store new tokens on success", async () => {
        localStorageMock.setItem("auth_refresh_token", "old-refresh")
        const response: RefreshResponse = {
          tokens: mockTokens,
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(response),
        })

        const result = await tryRefreshTokens()

        expect(result).toBe(true)
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          "auth_access_token",
          mockTokens.access_token
        )
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          "auth_refresh_token",
          mockTokens.refresh_token
        )
      })

      it("should clear tokens and return false on failure", async () => {
        localStorageMock.setItem("auth_refresh_token", "invalid")

        mockFetch.mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({ detail: "Invalid refresh token" }),
        })

        const result = await tryRefreshTokens()

        expect(result).toBe(false)
        expect(localStorageMock.removeItem).toHaveBeenCalledWith("auth_access_token")
        expect(localStorageMock.removeItem).toHaveBeenCalledWith("auth_refresh_token")
      })
    })
  })
})
