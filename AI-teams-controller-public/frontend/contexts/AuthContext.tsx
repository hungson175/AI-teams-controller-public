"use client"

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  type ReactNode,
} from "react"
import {
  User,
  LoginCredentials,
  RegisterCredentials,
  login as apiLogin,
  register as apiRegister,
  getMe,
  logout as apiLogout,
  setTokens,
  getToken,
  getRefreshToken,
  tryRefreshTokens,
} from "@/lib/auth"

// ============================================
// Types
// ============================================

export interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => void
  clearError: () => void
  refreshUser: () => Promise<void>
}

// ============================================
// Context
// ============================================

const AuthContext = createContext<AuthContextValue | null>(null)

// ============================================
// Provider
// ============================================

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isAuthenticated = useMemo(() => user !== null, [user])

  /**
   * Clear any auth error
   */
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  /**
   * Fetch current user from API
   */
  const refreshUser = useCallback(async () => {
    const token = getToken()
    if (!token) {
      setUser(null)
      setIsLoading(false)
      return
    }

    try {
      const response = await getMe()
      setUser(response.user)
      setError(null)
    } catch (err) {
      // Token might be expired, try refresh
      const refreshed = await tryRefreshTokens()
      if (refreshed) {
        try {
          const response = await getMe()
          setUser(response.user)
          setError(null)
          return
        } catch {
          // Refresh worked but getMe failed
        }
      }
      // Clear user state if token refresh failed
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Login with email and password
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    setIsLoading(true)
    setError(null)

    console.log("[AuthContext] login - START", { email: credentials.email })

    try {
      console.log("[AuthContext] login - Calling apiLogin()...")
      const response = await apiLogin(credentials)
      console.log("[AuthContext] login - API response:", { user: response.user, hasTokens: !!response.tokens })
      setTokens(response.tokens)
      setUser(response.user)
      console.log("[AuthContext] login - Tokens and user set successfully")
    } catch (err) {
      console.error("[AuthContext] login - ERROR:", err)
      const message = err instanceof Error ? err.message : "Login failed"
      setError(message)
      throw err
    } finally {
      setIsLoading(false)
      console.log("[AuthContext] login - END")
    }
  }, [])

  /**
   * Register new user
   */
  const register = useCallback(async (credentials: RegisterCredentials) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await apiRegister(credentials)
      setTokens(response.tokens)
      setUser(response.user)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Registration failed"
      setError(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Logout - clear tokens and user state
   */
  const logout = useCallback(() => {
    apiLogout()
    setUser(null)
    setError(null)
  }, [])

  // Initialize auth state on mount
  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  // Set up periodic token refresh (every 10 minutes)
  useEffect(() => {
    if (!isAuthenticated) return

    const refreshInterval = setInterval(async () => {
      const refreshToken = getRefreshToken()
      if (refreshToken) {
        const success = await tryRefreshTokens()
        if (!success) {
          // Refresh failed, log out
          logout()
        }
      }
    }, 10 * 60 * 1000) // 10 minutes

    return () => clearInterval(refreshInterval)
  }, [isAuthenticated, logout])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated,
      error,
      login,
      register,
      logout,
      clearError,
      refreshUser,
    }),
    [user, isLoading, isAuthenticated, error, login, register, logout, clearError, refreshUser]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// ============================================
// Hook
// ============================================

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

// ============================================
// Exports
// ============================================

export { AuthContext }
export type { AuthContextValue }
