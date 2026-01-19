/**
 * QuickViewPopup Component (Sprint 13 - Work Item #4)
 * Enhanced in Phase 2 - Story 4 with path breadcrumb
 *
 * Modal popup for quick view of file content from terminal paths
 */

"use client"

import { useEffect, useState } from "react"
import { X, Loader2, FileX } from "lucide-react"
import { CodeEditor } from "@/components/file-browser/CodeEditor"
import { getAuthHeaders } from "@/lib/auth-utils"

interface QuickViewPopupProps {
  /** Whether popup is open */
  isOpen: boolean
  /** Close handler */
  onClose: () => void
  /** File path to display */
  filePath: string
  /** Team ID for API calls */
  teamId: string
  /** Optional line number to scroll to */
  lineNumber?: number
}

interface FileContent {
  content: string | null
  name: string
  is_binary: boolean
  error?: string
}

/**
 * Quick View Popup Component
 *
 * Displays file content in a modal overlay with syntax highlighting.
 * Reuses CodeEditor component from Work Items #1-3 for syntax highlighting.
 */
export function QuickViewPopup({
  isOpen,
  onClose,
  filePath,
  teamId,
  lineNumber,
}: QuickViewPopupProps) {
  const [content, setContent] = useState<FileContent | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch file content when popup opens
  useEffect(() => {
    if (!isOpen || !filePath) {
      setContent(null)
      setError(null)
      return
    }

    const fetchContent = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const response = await fetch(
          `/api/files/${teamId}/content?path=${encodeURIComponent(filePath)}`,
          { headers: getAuthHeaders() }
        )

        if (!response.ok) {
          throw new Error(`Failed to load file: ${response.status}`)
        }

        const data: FileContent = await response.json()
        setContent(data)

        if (data.error) {
          setError(data.error)
        }
      } catch (err) {
        console.error("[QuickViewPopup] Error fetching content:", err)
        setError("Failed to load file content")
      } finally {
        setIsLoading(false)
      }
    }

    fetchContent()
  }, [isOpen, filePath, teamId])

  // Handle ESC key
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  // Handle overlay click (click-outside)
  // Use a ref to track if click started on content to avoid closing when dragging from content to overlay
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
        className="relative w-full max-w-4xl max-h-[80vh] bg-card border border-border rounded-lg shadow-lg flex flex-col cursor-default"
        onClick={handleContentClick}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            {/* Story 4 AC3: File path breadcrumb */}
            <div className="flex items-center gap-1 min-w-0 flex-1">
              {filePath.split("/").map((segment, index, arr) => (
                <div key={index} className="flex items-center gap-1 min-w-0">
                  <span
                    className={`${
                      index === arr.length - 1
                        ? "font-semibold text-foreground"
                        : "text-muted-foreground"
                    } ${index < arr.length - 1 ? "text-sm" : "text-base"}`}
                    title={segment}
                  >
                    {segment}
                  </span>
                  {index < arr.length - 1 && (
                    <span className="text-muted-foreground text-sm">/</span>
                  )}
                </div>
              ))}
            </div>
            {lineNumber && (
              <span className="text-sm text-muted-foreground whitespace-nowrap">
                Line {lineNumber}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-accent rounded-md transition-colors flex-shrink-0 ml-2"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading...</span>
            </div>
          )}

          {error && !content && (
            <div className="flex flex-col items-center justify-center h-full gap-2 text-muted-foreground">
              <FileX className="h-12 w-12" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {content && content.is_binary && (
            <div className="flex flex-col items-center justify-center h-full gap-2 text-muted-foreground">
              <FileX className="h-12 w-12" />
              <p className="text-sm">Binary file cannot be displayed</p>
            </div>
          )}

          {content && !content.is_binary && content.content && (
            <CodeEditor
              value={content.content}
              onChange={() => {}} // Read-only
              fileName={content.name}
              className="h-full"
            />
          )}
        </div>

        {/* Footer with file path */}
        <div className="px-4 py-2 border-t border-border bg-muted/50">
          <p className="text-xs text-muted-foreground font-mono">{filePath}</p>
        </div>
      </div>
    </div>
  )
}
