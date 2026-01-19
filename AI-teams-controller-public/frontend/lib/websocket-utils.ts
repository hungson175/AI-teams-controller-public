/**
 * WebSocket Utilities
 *
 * Centralized WebSocket URL resolution for the application.
 * WebSocket URLs must connect DIRECTLY to backend (Next.js rewrites don't support WebSocket).
 *
 * Wave 1: Extract Utilities (DRY Fixes) - Big Refactoring Sprint
 */

/**
 * Get WebSocket base URL based on environment
 *
 * @returns WebSocket base URL (ws:// or wss://)
 *
 * Environments:
 * - SSR (window undefined): ws://localhost:17061
 * - Production (voice-ui.hungson175.com): wss://voice-backend.hungson175.com
 * - Localhost/other: ws://localhost:17061
 */
export function getWebSocketBaseUrl(): string {
  // SSR environment - no window object
  if (typeof window === "undefined") {
    return "ws://localhost:17061"
  }

  // Browser environment - check hostname
  const hostname = window.location.hostname

  // Production: Cloudflare tunnel to backend
  if (hostname === "voice-ui.hungson175.com") {
    return "wss://voice-backend.hungson175.com"
  }

  // Localhost or other environments
  return "ws://localhost:17061"
}
