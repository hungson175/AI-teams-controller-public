"use client"

import { useState, useEffect, useCallback } from "react"
import { Loader2, File, Copy, Download, Edit, Save, X } from "lucide-react"
import { CodeViewer } from "./CodeViewer"
import { MarkdownViewer } from "./MarkdownViewer"
import { BinaryPlaceholder } from "./BinaryPlaceholder"
import { PathBreadcrumb } from "./PathBreadcrumb"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useToast } from "@/hooks/use-toast"
import { getAuthHeaders } from "@/lib/auth-utils"
import type { FileContent } from "./types"

interface FileViewerProps {
  /** Team ID for API calls */
  teamId: string
  /** Path to the file to display */
  filePath: string | null
  /** Project root path for breadcrumb display */
  projectRoot?: string
}

/**
 * Determine if a file should use the markdown viewer
 */
function isMarkdownFile(fileName: string): boolean {
  const ext = fileName.split(".").pop()?.toLowerCase() || ""
  return ["md", "mdx", "markdown"].includes(ext)
}

/**
 * FileViewer Component
 *
 * Container that loads and displays file content.
 * Automatically selects the appropriate viewer based on file type.
 */
export function FileViewer({ teamId, filePath, projectRoot }: FileViewerProps) {
  const { toast } = useToast()
  const projectName = projectRoot?.split("/").pop() || "Project"
  const [fileContent, setFileContent] = useState<FileContent | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Sprint 12 - Edit mode state
  const [isEditMode, setIsEditMode] = useState(false)
  const [editContent, setEditContent] = useState("")
  const [isSaving, setIsSaving] = useState(false)

  const handleCopyContent = useCallback(async () => {
    if (!fileContent?.content) return
    try {
      await navigator.clipboard.writeText(fileContent.content)
      toast({
        title: "Content copied",
        description: "File content copied to clipboard",
      })
    } catch (err) {
      console.error("[FileViewer] Failed to copy content:", err)
      toast({
        title: "Failed to copy",
        description: "Could not copy content to clipboard",
        variant: "destructive",
      })
    }
  }, [fileContent?.content, toast])

  const handleDownload = useCallback(() => {
    if (!fileContent?.content || !fileContent?.name) return
    try {
      const blob = new Blob([fileContent.content], { type: "text/plain" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = fileContent.name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast({
        title: "Download started",
        description: `Downloading ${fileContent.name}`,
      })
    } catch (err) {
      console.error("[FileViewer] Failed to download:", err)
      toast({
        title: "Download failed",
        description: "Could not download file",
        variant: "destructive",
      })
    }
  }, [fileContent?.content, fileContent?.name, toast])

  // Sprint 12 - Edit mode handlers
  const handleEdit = useCallback(() => {
    if (!fileContent?.content) return
    setEditContent(fileContent.content)
    setIsEditMode(true)
  }, [fileContent?.content])

  const handleCancel = useCallback(() => {
    setIsEditMode(false)
    setEditContent("")
  }, [])

  const handleSave = useCallback(async () => {
    if (!filePath) return

    setIsSaving(true)
    try {
      const response = await fetch(`/api/files/${teamId}/${filePath}`, {
        method: "PUT",
        headers: {
          ...getAuthHeaders(),
          "Content-Type": "text/plain",
        },
        body: editContent,
      })

      if (response.ok) {
        toast({
          title: "File saved",
          description: "File saved successfully",
        })
        setIsEditMode(false)
        // Refresh file content
        setFileContent((prev) => prev ? { ...prev, content: editContent } : null)
      } else {
        const error = await response.json()
        toast({
          title: "Save failed",
          description: error.error || "Failed to save file",
          variant: "destructive",
        })
      }
    } catch (err) {
      console.error("[FileViewer] Save error:", err)
      toast({
        title: "Network error",
        description: "Could not save file",
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }, [teamId, filePath, editContent, toast])

  // Sprint 12 - Keyboard shortcut for save (Cmd+S / Ctrl+S)
  useEffect(() => {
    if (!isEditMode) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault()
        handleSave()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isEditMode, handleSave])

  useEffect(() => {
    if (!filePath) {
      setFileContent(null)
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
          if (response.status === 404) {
            setError("File not found")
          } else {
            setError(`Failed to load file: ${response.status}`)
          }
          return
        }

        const data: FileContent = await response.json()
        setFileContent(data)

        // Check for API-level errors
        if (data.error) {
          setError(data.error)
        }
      } catch (err) {
        console.error("[FileViewer] Error fetching content:", err)
        setError("Failed to load file content")
      } finally {
        setIsLoading(false)
      }
    }

    fetchContent()
  }, [teamId, filePath])

  // No file selected
  if (!filePath) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 text-muted-foreground">
        <File className="h-16 w-16" />
        <p className="text-sm">Select a file to view</p>
      </div>
    )
  }

  // Loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  // Error (but no file content)
  if (error && !fileContent) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 text-muted-foreground">
        <p className="text-sm text-destructive">{error}</p>
      </div>
    )
  }

  // No content loaded yet
  if (!fileContent) {
    return null
  }

  // Check if content can be copied/downloaded (text files only)
  const canCopyOrDownload = fileContent?.content && !fileContent?.is_binary && !fileContent?.is_truncated

  // Helper to wrap content with breadcrumb header and toolbar
  const withHeader = (content: React.ReactNode) => (
    <div className="flex flex-col h-full min-h-0">
      {/* Breadcrumb header with toolbar */}
      <div className="flex items-center justify-between px-3 py-2 border-b bg-card min-h-[40px]">
        <PathBreadcrumb
          filePath={filePath || ""}
          projectName={projectName}
          onNavigate={() => {
            // Navigation handled by tree - breadcrumb is informational
          }}
        />
        {/* Toolbar buttons */}
        {canCopyOrDownload && (
          <div className="flex items-center gap-1 ml-2">
            {isEditMode ? (
              // Edit mode: Save and Cancel buttons
              <>
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleSave}
                  disabled={isSaving}
                  className="h-7"
                >
                  <Save className="h-4 w-4 mr-1" />
                  {isSaving ? "Saving..." : "Save"}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCancel}
                  disabled={isSaving}
                  className="h-7"
                >
                  <X className="h-4 w-4 mr-1" />
                  Cancel
                </Button>
              </>
            ) : (
              // View mode: Copy, Download, Edit buttons
              <>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={handleCopyContent}
                      aria-label="Copy content"
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Copy Content</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={handleDownload}
                      aria-label="Download file"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Download</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={handleEdit}
                      aria-label="Edit file"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Edit File</TooltipContent>
                </Tooltip>
              </>
            )}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {content}
      </div>
    </div>
  )

  // Binary file
  if (fileContent.is_binary) {
    return withHeader(
      <BinaryPlaceholder
        fileName={fileContent.name}
        size={fileContent.size}
        message={fileContent.error || "Binary files cannot be displayed"}
      />
    )
  }

  // Truncated file
  if (fileContent.is_truncated) {
    return withHeader(
      <BinaryPlaceholder
        fileName={fileContent.name}
        size={fileContent.size}
        message={fileContent.error || "File too large to display"}
      />
    )
  }

  // File with error (e.g., blacklisted)
  if (fileContent.error && !fileContent.content) {
    return withHeader(
      <BinaryPlaceholder
        fileName={fileContent.name}
        size={fileContent.size}
        message={fileContent.error}
      />
    )
  }

  // Text content - choose appropriate viewer or editor
  const textContent = fileContent.content || ""

  // Sprint 12 - Edit mode: Show textarea
  if (isEditMode) {
    return withHeader(
      <textarea
        value={editContent}
        onChange={(e) => setEditContent(e.target.value)}
        className="w-full h-full p-4 font-mono text-sm resize-none focus:outline-none bg-background"
        spellCheck={false}
      />
    )
  }

  // View mode: Show appropriate viewer
  if (isMarkdownFile(fileContent.name)) {
    return withHeader(<MarkdownViewer content={textContent} />)
  }

  return withHeader(<CodeViewer content={textContent} fileName={fileContent.name} />)
}
