/**
 * AuthContext Tests
 *
 * Tests for the authentication context provider.
 * Sprint 25: Frontend Auth Migration
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

// Import after mocks
import { AuthProvider, useAuth } from "./AuthContext"
import type { User, AuthTokens, LoginResponse, RegisterResponse, MeResponse } from "@/lib/auth"

// Test data
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

// Helper wrapper
function createWrapper() {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <AuthProvider>{children}</AuthProvider>
  }
}

describe("AuthContext", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ===========================================
  // Provider Tests
  // ===========================================

  describe("AuthProvider", () => {
    it("should throw error when useAuth is used outside provider", () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {})

      expect(() => {
        renderHook(() => useAuth())
      }).toThrow("useAuth must be used within an AuthProvider")

      consoleSpy.mockRestore()
    })

    it("should initialize with no user when no token", async () => {
      // No token, so no fetch call will be made
      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      // Wait for initial auth check
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(mockFetch).not.toHaveBeenCalled()
    })

    it("should load user from stored token on mount", async () => {
      localStorageMock.setItem("auth_access_token", "valid-token")

      const meResponse: MeResponse = { user: mockUser }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(meResponse),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
    })
  })

  // ===========================================
  // Login Tests
  // ===========================================

  describe("login", () => {
    it("should login and store tokens", async () => {
      const loginResponse: LoginResponse = {
        user: mockUser,
        tokens: mockTokens,
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(loginResponse),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      // Wait for initial load (no token, quick)
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      // Perform login
      await act(async () => {
        await result.current.login({ email: "test@example.com", password: "password" })
      })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "auth_access_token",
        mockTokens.access_token
      )
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "auth_refresh_token",
        mockTokens.refresh_token
      )
    })

    it("should set error on login failure", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: "Invalid credentials" }),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      await act(async () => {
        try {
          await result.current.login({ email: "test@example.com", password: "wrong" })
        } catch {
          // Expected to throw
        }
      })

      expect(result.current.error).toBe("Invalid credentials")
      expect(result.current.user).toBeNull()
    })
  })

  // ===========================================
  // Register Tests
  // ===========================================

  describe("register", () => {
    it("should register and store tokens", async () => {
      const registerResponse: RegisterResponse = {
        user: mockUser,
        tokens: mockTokens,
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(registerResponse),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      await act(async () => {
        await result.current.register({
          email: "test@example.com",
          username: "testuser",
          password: "password123",
        })
      })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "auth_access_token",
        mockTokens.access_token
      )
    })

    it("should set error on registration failure", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: "Email already registered" }),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      await act(async () => {
        try {
          await result.current.register({
            email: "test@example.com",
            username: "testuser",
            password: "password",
          })
        } catch {
          // Expected to throw
        }
      })

      expect(result.current.error).toBe("Email already registered")
    })
  })

  // ===========================================
  // Logout Tests
  // ===========================================

  describe("logout", () => {
    it("should clear user and tokens on logout", async () => {
      // Setup authenticated user
      localStorageMock.setItem("auth_access_token", "valid-token")
      const meResponse: MeResponse = { user: mockUser }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(meResponse),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
      }, { timeout: 1000 })

      // Logout
      act(() => {
        result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith("auth_access_token")
      expect(localStorageMock.removeItem).toHaveBeenCalledWith("auth_refresh_token")
    })
  })

  // ===========================================
  // Error Handling Tests
  // ===========================================

  describe("error handling", () => {
    it("should clear error with clearError", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: "Test error" }),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      await act(async () => {
        try {
          await result.current.login({ email: "test@example.com", password: "wrong" })
        } catch {
          // Expected
        }
      })

      expect(result.current.error).toBe("Test error")

      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBeNull()
    })
  })

  // ===========================================
  // Token Refresh Tests
  // ===========================================

  describe("token refresh", () => {
    it("should try token refresh when getMe fails", async () => {
      localStorageMock.setItem("auth_access_token", "expired-token")
      localStorageMock.setItem("auth_refresh_token", "valid-refresh")

      // First getMe fails (expired token)
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: "Token expired" }),
      })

      // Refresh succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ tokens: mockTokens }),
      })

      // Second getMe succeeds
      const meResponse: MeResponse = { user: mockUser }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(meResponse),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
    })

    it("should logout when token refresh fails", async () => {
      localStorageMock.setItem("auth_access_token", "expired-token")
      localStorageMock.setItem("auth_refresh_token", "invalid-refresh")

      // First getMe fails
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: "Token expired" }),
      })

      // Refresh also fails
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: "Invalid refresh token" }),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  // ===========================================
  // refreshUser Tests
  // ===========================================

  describe("refreshUser", () => {
    it("should refresh user data from API", async () => {
      localStorageMock.setItem("auth_access_token", "valid-token")

      const meResponse: MeResponse = { user: mockUser }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(meResponse),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      }, { timeout: 1000 })

      // Update user data
      const updatedUser = { ...mockUser, username: "updateduser" }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ user: updatedUser }),
      })

      await act(async () => {
        await result.current.refreshUser()
      })

      expect(result.current.user?.username).toBe("updateduser")
    })
  })
})
