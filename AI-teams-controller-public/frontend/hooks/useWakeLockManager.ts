"use client"

import { useRef, useCallback, useEffect } from "react"

/**
 * Props for useWakeLockManager hook
 */
export interface UseWakeLockManagerProps {
  /** Whether wake lock should be active (e.g., during recording) */
  isActive: boolean
}

/**
 * Return type for useWakeLockManager hook
 */
export interface UseWakeLockManagerReturn {
  /** Request screen wake lock */
  requestWakeLock: () => Promise<void>
  /** Release screen wake lock */
  releaseWakeLock: () => Promise<void>
}

/**
 * useWakeLockManager Hook
 *
 * Manages screen wake lock to keep screen on during voice recording (mobile).
 *
 * Features:
 * - Automatically requests wake lock when isActive becomes true
 * - Automatically releases wake lock when isActive becomes false
 * - Re-acquires wake lock when page becomes visible again
 * - Progressive enhancement (fails silently if Wake Lock API unavailable)
 * - Cleans up wake lock on unmount
 */
export function useWakeLockManager({ isActive }: UseWakeLockManagerProps): UseWakeLockManagerReturn {
  const wakeLockRef = useRef<WakeLockSentinel | null>(null)

  /**
   * Request Wake Lock to keep screen on during recording (mobile)
   * Progressive enhancement - fails silently if not supported
   */
  const requestWakeLock = useCallback(async () => {
    try {
      if ('wakeLock' in navigator) {
        wakeLockRef.current = await navigator.wakeLock.request('screen')
        console.log('[WakeLock] Screen wake lock acquired')

        // Handle release (e.g., tab becomes hidden)
        wakeLockRef.current.addEventListener('release', () => {
          console.log('[WakeLock] Screen wake lock released')
        })
      }
    } catch (error) {
      // Fail silently - not all browsers support Wake Lock
      console.log('[WakeLock] Could not acquire wake lock:', error)
    }
  }, [])

  /**
   * Release Wake Lock when recording stops
   */
  const releaseWakeLock = useCallback(async () => {
    if (wakeLockRef.current) {
      try {
        await wakeLockRef.current.release()
        wakeLockRef.current = null
        console.log('[WakeLock] Screen wake lock released manually')
      } catch (error) {
        console.log('[WakeLock] Error releasing wake lock:', error)
      }
    }
  }, [])

  // Auto-request wake lock when isActive becomes true
  useEffect(() => {
    if (isActive) {
      requestWakeLock()
    } else {
      releaseWakeLock()
    }
  }, [isActive, requestWakeLock, releaseWakeLock])

  // Re-acquire wake lock when page becomes visible again (if still active)
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible' && isActive && !wakeLockRef.current) {
        console.log('[WakeLock] Page visible, re-acquiring wake lock')
        await requestWakeLock()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [isActive, requestWakeLock])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      releaseWakeLock()
    }
  }, [releaseWakeLock])

  return {
    requestWakeLock,
    releaseWakeLock,
  }
}
