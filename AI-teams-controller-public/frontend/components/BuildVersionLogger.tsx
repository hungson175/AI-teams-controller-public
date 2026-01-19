"use client"

import { useEffect } from "react"

/**
 * Logs build version to console on page load.
 * Helps debug caching issues - verify the correct build is running.
 *
 * Usage: Check browser console for "BUILD VERSION: YYYY-MM-DD HH:MM:SS"
 */
export function BuildVersionLogger() {
  useEffect(() => {
    const version = process.env.NEXT_PUBLIC_BUILD_VERSION || "unknown"
    console.log(
      "%c🔨 BUILD VERSION: %c" + version,
      "color: #888; font-weight: bold;",
      "color: #0af; font-weight: bold; font-size: 14px;"
    )
  }, [])

  return null
}
