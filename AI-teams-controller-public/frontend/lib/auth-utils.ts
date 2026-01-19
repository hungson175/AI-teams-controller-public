/**
 * Authentication Utilities
 *
 * Centralized authentication header construction for API requests.
 *
 * Wave 1: Extract Utilities (DRY Fixes) - Big Refactoring Sprint
 */

import { getToken } from "@/lib/auth"

/**
 * Get authentication headers for API requests
 *
 * @returns Headers object with Authorization and Content-Type
 *
 * Usage:
 * ```typescript
 * fetch("/api/endpoint", {
 *   headers: getAuthHeaders(),
 *   ...
 * })
 * ```
 */
export function getAuthHeaders(): Record<string, string> {
  return {
    "Authorization": `Bearer ${getToken()}`,
    "Content-Type": "application/json",
  }
}
