// Auth helper functions for JWT-based authentication
// Sprint 25: PostgreSQL Integration - Frontend Auth Migration

const ACCESS_TOKEN_KEY = "auth_access_token"
const REFRESH_TOKEN_KEY = "auth_refresh_token"

// === Request Types ===

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  email: string
  username: string
  password: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

// === Response Types (matching backend schemas) ===

export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginResponse {
  user: User
  tokens: AuthTokens
}

export interface RegisterResponse {
  user: User
  tokens: AuthTokens
}

export interface RefreshResponse {
  tokens: AuthTokens
}

export interface MeResponse {
  user: User
}

export interface AuthError {
  detail: string
}

// === Token Storage Functions ===

/**
 * Get the stored access token from localStorage
 */
export function getToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

/**
 * Get the stored refresh token from localStorage
 */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

/**
 * Store both auth tokens in localStorage
 */
export function setTokens(tokens: AuthTokens): void {
  if (typeof window === "undefined") return
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token)
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
}

/**
 * Store single access token (legacy compatibility)
 */
export function setToken(token: string): void {
  if (typeof window === "undefined") return
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

/**
 * Remove all auth tokens from localStorage
 */
export function removeTokens(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

/**
 * Legacy: Remove single token (calls removeTokens)
 */
export function removeToken(): void {
  removeTokens()
}

/**
 * Check if user is authenticated (has access token)
 */
export function isAuthenticated(): boolean {
  return getToken() !== null
}

// === API Functions ===

/**
 * Login API call
 * Returns user and tokens on success
 */
export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  console.log("[lib/auth] login - START", { email: credentials.email, url: "/api/auth/login" })

  const response = await fetch(`/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  })

  console.log("[lib/auth] login - Response received:", {
    ok: response.ok,
    status: response.status,
    statusText: response.statusText
  })

  if (!response.ok) {
    const error: AuthError = await response.json()
    console.error("[lib/auth] login - API error:", error)
    throw new Error(error.detail || "Login failed")
  }

  const data = await response.json()
  console.log("[lib/auth] login - Success, returning data:", {
    hasUser: !!data.user,
    hasTokens: !!data.tokens
  })
  return data
}

/**
 * Register API call
 * Creates new user and returns user with tokens
 */
export async function register(credentials: RegisterCredentials): Promise<RegisterResponse> {
  const response = await fetch(`/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    const error: AuthError = await response.json()
    throw new Error(error.detail || "Registration failed")
  }

  return response.json()
}

/**
 * Refresh tokens API call
 * Returns new token pair from valid refresh token
 */
export async function refreshTokens(refreshToken: string): Promise<RefreshResponse> {
  const response = await fetch(`/api/auth/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })

  if (!response.ok) {
    const error: AuthError = await response.json()
    throw new Error(error.detail || "Token refresh failed")
  }

  return response.json()
}

/**
 * Get current user info
 * Requires valid access token
 */
export async function getMe(): Promise<MeResponse> {
  const token = getToken()
  if (!token) {
    throw new Error("Not authenticated")
  }

  const response = await fetch(`/api/auth/me`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    const error: AuthError = await response.json()
    throw new Error(error.detail || "Failed to get user info")
  }

  return response.json()
}

/**
 * Logout - remove all tokens
 */
export function logout(): void {
  removeTokens()
}

/**
 * Attempt to refresh tokens if access token expired
 * Returns true if refresh successful, false otherwise
 */
export async function tryRefreshTokens(): Promise<boolean> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    return false
  }

  try {
    const response = await refreshTokens(refreshToken)
    setTokens(response.tokens)
    return true
  } catch {
    // Refresh token invalid/expired, clear everything
    removeTokens()
    return false
  }
}
