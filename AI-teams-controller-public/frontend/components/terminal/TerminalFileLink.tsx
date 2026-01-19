/**
 * TerminalFileLink Component
 * Sprint 13 - Work Item #4: Basic clickable link
 * Sprint 14 - Work Item #4: Path resolution integration
 * Phase 2 Story 4 - AC4: Enhanced visual indication
 *
 * Clickable file path link in terminal output with intelligent path resolution
 */

"use client"

import { useState } from "react"
import { usePathResolver } from "@/hooks/usePathResolver"
import { QuickViewPopup } from "./QuickViewPopup"
import { FileMatchPopup } from "./FileMatchPopup"
import { useToast } from "@/hooks/use-toast"

interface TerminalFileLinkProps {
  /** File path to display */
  path: string
  /** Team ID for path resolution */
  teamId?: string
  /** Optional line number */
  lineNumber?: number
  /** Optional column number */
  columnNumber?: number
  /** Click handler - opens quick view popup (legacy, optional) */
  onClick?: () => void
}

/**
 * Clickable file path link component with intelligent path resolution
 *
 * Sprint 13: Renders a file path as a clickable button
 * Sprint 14: Resolves path using usePathResolver, handles 0/1/N matches
 *
 * Behavior:
 * - Single match → Opens QuickViewPopup directly
 * - Multiple matches → Shows FileMatchPopup for selection
 * - No matches → Shows error toast
 */
export function TerminalFileLink({
  path,
  teamId,
  lineNumber,
  columnNumber,
  onClick,
}: TerminalFileLinkProps) {
  const { toast } = useToast()
  const [showQuickView, setShowQuickView] = useState(false)
  const [showFileMatch, setShowFileMatch] = useState(false)
  const [selectedPath, setSelectedPath] = useState<string | null>(null)

  // Sprint 14: Path resolution (only if teamId provided)
  // Use conditional hook call pattern - always call but with safe default
  const shouldResolve = Boolean(teamId)
  const resolution = usePathResolver(teamId || "", shouldResolve ? path : "")

  // Build display text with line/column numbers if present
  let displayText = path
  if (lineNumber !== undefined) {
    displayText += `:${lineNumber}`
    if (columnNumber !== undefined) {
      displayText += `:${columnNumber}`
    }
  }

  const handleClick = (e: React.MouseEvent) => {
    // CRITICAL: Stop event propagation to prevent overlay click handler from firing
    // This fixes the bug where popup would immediately close after opening
    e.stopPropagation()

    // Legacy onClick handler (Sprint 13)
    if (onClick && !teamId) {
      onClick()
      return
    }

    // Sprint 14: Path resolution logic
    if (!teamId) {
      toast({
        title: "No team context",
        description: "Cannot resolve file path without team ID",
        variant: "destructive",
      })
      return
    }

    // Handle based on resolution status
    switch (resolution.status) {
      case "loading":
        // Do nothing while loading
        break

      case "resolved":
        // Single match - open QuickViewPopup directly
        setSelectedPath(resolution.resolvedPath!)
        setShowQuickView(true)
        break

      case "multiple":
        // Multiple matches - show FileMatchPopup for selection
        setShowFileMatch(true)
        break

      case "not_found":
        // No matches - show error toast
        toast({
          title: "File not found",
          description: `Could not find file: ${path}`,
          variant: "destructive",
        })
        break
    }
  }

  const handleFileSelect = (filePath: string) => {
    setSelectedPath(filePath)
    setShowFileMatch(false)
    setShowQuickView(true)
  }

  return (
    <>
      <button
        onClick={handleClick}
        className="inline break-all underline underline-offset-2 cursor-pointer text-blue-400 hover:text-blue-300 hover:bg-blue-400/10 rounded-sm px-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        type="button"
        disabled={resolution.status === "loading"}
        title={`Click to open: ${path}`}
      >
        {displayText}
      </button>

      {/* QuickViewPopup - Sprint 13 */}
      {showQuickView && selectedPath && teamId && (
        <QuickViewPopup
          isOpen={showQuickView}
          onClose={() => setShowQuickView(false)}
          filePath={selectedPath}
          teamId={teamId}
          lineNumber={lineNumber}
        />
      )}

      {/* FileMatchPopup - Sprint 14 */}
      {showFileMatch && (
        <FileMatchPopup
          isOpen={showFileMatch}
          onClose={() => setShowFileMatch(false)}
          matches={resolution.matches}
          onSelect={handleFileSelect}
        />
      )}
    </>
  )
}
