"use client"

import { useState, useCallback, useRef, useEffect } from "react"

/**
 * Props for useCommandHistory hook
 */
export interface UseCommandHistoryProps {
  /** Whether terminal mode is active (command history only works in terminal mode) */
  isTerminalMode?: boolean
}

/**
 * Return type for useCommandHistory hook
 */
export interface UseCommandHistoryReturn {
  /** Array of command history */
  history: string[]
  /** Current position in history (-1 = not navigating) */
  historyIndex: number
  /** Saved input before navigating history */
  savedInput: string
  /** Add command to history */
  addToHistory: (command: string) => void
  /** Navigate to previous command (ArrowUp) */
  navigateUp: (currentInput: string) => string | null
  /** Navigate to next command (ArrowDown) */
  navigateDown: () => string | null
  /** Reset navigation state */
  reset: () => void
}

/**
 * useCommandHistory Hook
 *
 * Manages command history for terminal mode with keyboard navigation.
 *
 * Features:
 * - Stores command history array
 * - ArrowUp navigates to older commands
 * - ArrowDown navigates to newer commands
 * - Saves/restores current input when navigating
 * - Prevents duplicate consecutive commands
 * - Resets navigation state after command submission
 */
export function useCommandHistory({ isTerminalMode = true }: UseCommandHistoryProps = {}): UseCommandHistoryReturn {
  const [history, setHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [savedInput, setSavedInput] = useState("")

  // Use refs for synchronous access (needed for consecutive calls)
  const historyRef = useRef<string[]>([])
  const indexRef = useRef(-1)

  // Keep refs in sync with state
  useEffect(() => {
    historyRef.current = history
  }, [history])

  useEffect(() => {
    indexRef.current = historyIndex
  }, [historyIndex])

  /**
   * Add command to history
   * Skips empty commands and consecutive duplicates
   */
  const addToHistory = useCallback((command: string) => {
    const trimmed = command.trim()
    if (!trimmed) return

    setHistory(prev => {
      // Prevent duplicate of last command
      if (prev[prev.length - 1] === trimmed) {
        return prev
      }
      return [...prev, trimmed]
    })

    // Reset navigation state
    setHistoryIndex(-1)
    setSavedInput("")
  }, [])

  /**
   * Navigate to older command (ArrowUp)
   * Returns the command to display, or null if no history
   */
  const navigateUp = useCallback((currentInput: string): string | null => {
    if (!isTerminalMode) return null

    const currentHistory = historyRef.current
    if (currentHistory.length === 0) return null

    const currentIndex = indexRef.current

    if (currentIndex === -1) {
      // Starting to navigate - save current input
      setSavedInput(currentInput)
      const newIndex = currentHistory.length - 1
      setHistoryIndex(newIndex)
      indexRef.current = newIndex
      return currentHistory[newIndex]
    } else if (currentIndex > 0) {
      // Navigate to older command
      const newIndex = currentIndex - 1
      setHistoryIndex(newIndex)
      indexRef.current = newIndex
      return currentHistory[newIndex]
    }

    // Already at oldest, stay there
    return currentHistory[currentIndex]
  }, [isTerminalMode])

  /**
   * Navigate to newer command (ArrowDown)
   * Returns the command to display, or null if not navigating
   */
  const navigateDown = useCallback((): string | null => {
    if (!isTerminalMode) return null

    const currentHistory = historyRef.current
    const currentIndex = indexRef.current

    if (currentIndex === -1) return null

    if (currentIndex < currentHistory.length - 1) {
      // Navigate to newer command
      const newIndex = currentIndex + 1
      setHistoryIndex(newIndex)
      indexRef.current = newIndex
      return currentHistory[newIndex]
    } else {
      // Back to saved input
      setHistoryIndex(-1)
      indexRef.current = -1
      return savedInput
    }
  }, [savedInput, isTerminalMode])

  /**
   * Reset navigation state (called after command submission)
   */
  const reset = useCallback(() => {
    setHistoryIndex(-1)
    setSavedInput("")
    indexRef.current = -1
  }, [])

  return {
    history,
    historyIndex,
    savedInput,
    addToHistory,
    navigateUp,
    navigateDown,
    reset,
  }
}
