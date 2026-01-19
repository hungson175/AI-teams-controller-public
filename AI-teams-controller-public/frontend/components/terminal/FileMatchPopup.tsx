/**
 * FileMatchPopup Component (Sprint 14 - Work Item #3)
 * Enhanced in Phase 2 - Story 4 with keyboard navigation
 *
 * Modal popup for selecting from multiple file path matches
 */

"use client"

import { useEffect, useState } from "react"
import { X, File } from "lucide-react"

interface FileMatchPopupProps {
  /** Whether popup is open */
  isOpen: boolean
  /** Close handler */
  onClose: () => void
  /** List of matching file paths */
  matches: string[]
  /** Selection handler - called when user picks a file */
  onSelect: (path: string) => void
}

/**
 * File Match Selection Popup
 *
 * Shows list of matching files when path resolution finds multiple matches.
 * User clicks a file to open it in QuickViewPopup.
 */
export function FileMatchPopup({
  isOpen,
  onClose,
  matches,
  onSelect,
}: FileMatchPopupProps) {
  // Story 4 AC2: Keyboard navigation state
  const [selectedIndex, setSelectedIndex] = useState(0)

  // Reset selection when popup opens or matches change
  useEffect(() => {
    if (isOpen) {
      setSelectedIndex(0)
    }
  }, [isOpen, matches])

  // Handle keyboard navigation (ESC, Arrow keys, Enter)
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose()
      } else if (e.key === "ArrowDown") {
        e.preventDefault()
        setSelectedIndex((prev) => Math.min(prev + 1, matches.length - 1))
      } else if (e.key === "ArrowUp") {
        e.preventDefault()
        setSelectedIndex((prev) => Math.max(prev - 1, 0))
      } else if (e.key === "Enter") {
        e.preventDefault()
        if (matches[selectedIndex]) {
          onSelect(matches[selectedIndex])
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onClose, matches, selectedIndex, onSelect])

  if (!isOpen) return null

  // Extract filename from first match for header
  const filename = matches[0]?.split("/").pop() || "file"

  // Handle overlay click (click-outside)
  const handleOverlayClick = () => {
    onClose()
  }

  const handleContentClick = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      data-testid="popup-overlay"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm cursor-pointer"
      onClick={handleOverlayClick}
    >
      <div
        data-testid="popup-content"
        className="relative w-full max-w-2xl bg-card border border-border rounded-lg shadow-lg flex flex-col cursor-default"
        onClick={handleContentClick}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 className="text-lg font-semibold">
            Multiple files match "{filename}"
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-accent rounded-md transition-colors"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* File list */}
        <div className="max-h-[60vh] overflow-y-auto">
          {matches.length === 0 ? (
            <div className="px-4 py-8 text-center text-muted-foreground">
              No matching files found
            </div>
          ) : (
            <ul className="divide-y divide-border">
              {matches.map((filePath, index) => (
                <li key={index}>
                  <button
                    onClick={() => onSelect(filePath)}
                    onMouseEnter={() => setSelectedIndex(index)}
                    className={`w-full px-4 py-3 flex items-center gap-3 transition-colors text-left ${
                      index === selectedIndex
                        ? "bg-accent"
                        : "hover:bg-accent/50"
                    }`}
                    data-selected={index === selectedIndex}
                  >
                    <File className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                    <span className="font-mono text-sm">{filePath}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer hint */}
        <div className="px-4 py-2 border-t border-border bg-muted/50">
          <p className="text-xs text-muted-foreground">
            Use ↑↓ arrows to navigate, Enter to select, or ESC to cancel
          </p>
        </div>
      </div>
    </div>
  )
}
