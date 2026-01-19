"use client"

import { Folder, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * Props for AutocompleteDropdown component
 */
export interface AutocompleteDropdownProps {
  /** Array of autocomplete suggestions to display */
  suggestions: string[]
  /** Currently selected/highlighted suggestion index */
  selectedIndex: number
  /** Callback when a suggestion is selected */
  onSelect: (suggestion: string) => void
  /** Callback to dismiss/close the dropdown */
  onDismiss: () => void
  /** Callback when navigating between suggestions */
  onNavigate: (newIndex: number) => void
  /** Whether path suggestions are being loaded from API */
  isLoading: boolean
  /** Whether suggestions are path completions (vs command completions) */
  isPathMode: boolean
}

/**
 * AutocompleteDropdown Component
 *
 * Displays autocomplete suggestions (commands or paths) in a dropdown menu.
 * Supports keyboard navigation (ArrowUp, ArrowDown, Tab, Escape) and mouse interaction.
 *
 * Features:
 * - Visual distinction between path and command suggestions
 * - Loading state for async path completions
 * - Keyboard hints in footer
 * - Hover preview
 * - Wrap-around navigation
 */
export function AutocompleteDropdown({
  suggestions,
  selectedIndex,
  onSelect,
  onDismiss,
  onNavigate,
  isLoading,
  isPathMode,
}: AutocompleteDropdownProps) {
  /**
   * Handle keyboard navigation within the dropdown
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault()
        onNavigate(selectedIndex < suggestions.length - 1 ? selectedIndex + 1 : 0)
        break
      case "ArrowUp":
        e.preventDefault()
        onNavigate(selectedIndex > 0 ? selectedIndex - 1 : suggestions.length - 1)
        break
      case "Tab":
        e.preventDefault()
        if (suggestions.length > 0) {
          onSelect(suggestions[selectedIndex])
        }
        break
      case "Escape":
        e.preventDefault()
        onDismiss()
        break
    }
  }

  // Show loading indicator when fetching paths
  if (isLoading && suggestions.length === 0) {
    return (
      <div
        data-testid="path-loading"
        className="absolute bottom-full left-10 right-12 mb-1 bg-card border border-border rounded-md shadow-lg p-3 z-50 flex items-center gap-2"
      >
        <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
        <span className="text-sm text-muted-foreground">Loading paths...</span>
      </div>
    )
  }

  // Don't render if no suggestions
  if (suggestions.length === 0) {
    return null
  }

  return (
    <div
      className="absolute bottom-full left-10 right-12 mb-1 bg-card border border-border rounded-md shadow-lg overflow-hidden z-50"
      role="listbox"
      aria-label={isPathMode ? "Path suggestions" : "Command suggestions"}
      onKeyDown={handleKeyDown}
    >
      {suggestions.map((suggestion, index) => {
        const isPath = suggestion.includes("/")
        const isSelected = index === selectedIndex

        return (
          <button
            key={suggestion}
            type="button"
            role="option"
            aria-selected={isSelected}
            className={cn(
              "w-full text-left px-3 py-2 text-sm font-mono transition-colors flex items-center gap-2",
              isSelected
                ? isPath
                  ? "bg-blue-500/20 text-blue-400"
                  : "bg-green-500/20 text-green-400"
                : "hover:bg-muted/50 text-foreground/80"
            )}
            onClick={() => onSelect(suggestion)}
            onMouseEnter={() => onNavigate(index)}
          >
            {isPath ? (
              <Folder className="h-3.5 w-3.5 text-blue-500 shrink-0" />
            ) : (
              <span className="text-green-500">$</span>
            )}
            {suggestion}
          </button>
        )
      })}
      <div className="px-3 py-1.5 text-xs text-muted-foreground border-t border-border bg-muted/30">
        ↑↓ Navigate • Tab Select • Esc Close
      </div>
    </div>
  )
}
