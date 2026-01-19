/**
 * useScrollManager - Scroll State Management Hook
 *
 * Extracted from TmuxController.tsx as part of Sprint 3 FE-3 refactoring.
 *
 * Manages:
 * - Auto-scroll behavior (scroll to bottom on new content)
 * - Manual scroll detection (user scrolls up = disable auto-scroll)
 * - Scroll FAB (floating action button) visibility
 * - Auto-scroll on role selection
 * - Scroll to highlighted message
 */

import { useState, useEffect, useRef, useCallback, RefObject, MutableRefObject } from 'react'

interface PaneState {
  output: string
  highlightText?: string | null
  isActive?: boolean
}

interface UseScrollManagerParams {
  outputRef: RefObject<HTMLDivElement>
  selectedRole: string | null
}

interface UseScrollManagerReturn {
  isAutoScrollEnabled: boolean
  showScrollFab: boolean
  isAutoScrollEnabledRef: RefObject<boolean>
  handleScroll: () => void
  scrollToBottom: () => void
}

export function useScrollManager({
  outputRef,
  selectedRole,
}: UseScrollManagerParams): UseScrollManagerReturn {
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true)
  const [showScrollFab, setShowScrollFab] = useState(false)
  const isAutoScrollEnabledRef = useRef(true)

  const handleScroll = useCallback(() => {
    if (!outputRef.current) return
    const { scrollTop, scrollHeight, clientHeight } = outputRef.current
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight
    const isAtBottom = distanceFromBottom < 50

    if (isAtBottom) {
      setIsAutoScrollEnabled(true)
      isAutoScrollEnabledRef.current = true
      setShowScrollFab(false)
    } else {
      setIsAutoScrollEnabled(false)
      isAutoScrollEnabledRef.current = false
      setShowScrollFab(true)
    }
  }, [outputRef])

  const scrollToBottom = useCallback(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
      setIsAutoScrollEnabled(true)
      isAutoScrollEnabledRef.current = true
      setShowScrollFab(false)
    }
  }, [outputRef])

  // Auto-scroll to bottom when role first selected
  useEffect(() => {
    if (selectedRole && outputRef.current) {
      // Use requestAnimationFrame to ensure content is rendered before scrolling
      requestAnimationFrame(() => {
        if (outputRef.current) {
          outputRef.current.scrollTop = outputRef.current.scrollHeight
          setIsAutoScrollEnabled(true)
          isAutoScrollEnabledRef.current = true
          setShowScrollFab(false)
        }
      })
    }
  }, [selectedRole, outputRef])

  return {
    isAutoScrollEnabled,
    showScrollFab,
    isAutoScrollEnabledRef,
    handleScroll,
    scrollToBottom,
  }
}
