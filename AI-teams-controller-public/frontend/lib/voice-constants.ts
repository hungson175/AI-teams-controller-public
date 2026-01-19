/**
 * Voice-related Constants
 *
 * Centralized constants for voice recording, feedback, and notification management.
 *
 * Wave 1: Extract Utilities (DRY Fixes) - Big Refactoring Sprint
 */

/**
 * Voice feedback and notification constants
 */
export const VOICE_CONSTANTS = {
  /**
   * Debounce duration for duplicate voice commands (ms)
   * Prevents duplicate command submissions within this window
   */
  DEBOUNCE_MS: 500,

  /**
   * Maximum number of voice feedback notifications to retain
   * Older notifications are dropped when limit is reached
   */
  MAX_NOTIFICATIONS: 50,

  /**
   * Deduplication window for voice feedback messages (ms)
   * Identical messages within this window are considered duplicates
   */
  DEDUP_WINDOW_MS: 30 * 1000, // 30 seconds

  /**
   * Notification expiry time (ms)
   * Notifications older than this are automatically removed
   */
  NOTIFICATION_EXPIRY_MS: 24 * 60 * 60 * 1000, // 24 hours

  /**
   * Maximum age for auto-playing voice feedback (ms)
   * Messages older than this won't auto-play even in hands-free mode
   */
  MAX_AGE_FOR_AUTOPLAY_MS: 60 * 1000, // 60 seconds
} as const
