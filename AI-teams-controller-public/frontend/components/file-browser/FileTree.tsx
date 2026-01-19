"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { RefreshCw, AlertCircle, Eye, EyeOff, Plus, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { FileTreeItem } from "./FileTreeItem"
import { FileTreeSkeleton } from "./FileTreeSkeleton"
import { getAuthHeaders } from "@/lib/auth-utils"
import type { FileNode, TreeResponse } from "./types"

const SHOW_HIDDEN_KEY = "file-browser-show-hidden"
const EXPANDED_KEY_PREFIX = "file-browser-expanded-"

interface FileTreeProps {
  /** Team ID for API calls */
  teamId: string
  /** Currently selected file path */
  selectedPath: string | null
  /** Callback when a file is selected */
  onFileSelect: (path: string) => void
  /** Callback when project root is determined */
  onProjectRootChange?: (root: string) => void
}

/**
 * FileTree Component
 *
 * Displays a navigable directory tree for a team's project.
 * Supports lazy loading of subdirectories on expand.
 */
export function FileTree({ teamId, selectedPath, onFileSelect, onProjectRootChange }: FileTreeProps) {
  const [tree, setTree] = useState<FileNode[]>([])
  const [projectRoot, setProjectRoot] = useState<string>("")
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Hidden files toggle with localStorage persistence
  const [showHidden, setShowHidden] = useState(() => {
    if (typeof window === "undefined") return true
    const stored = localStorage.getItem(SHOW_HIDDEN_KEY)
    return stored !== null ? stored === "true" : true // Default: show hidden
  })

  // Expanded folders with localStorage persistence (per team)
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(() => {
    if (typeof window === "undefined") return new Set()
    try {
      const stored = localStorage.getItem(`${EXPANDED_KEY_PREFIX}${teamId}`)
      if (stored) {
        return new Set(JSON.parse(stored))
      }
    } catch (e) {
      console.error("[FileTree] Failed to load expanded paths:", e)
    }
    return new Set()
  })

  // Create file/folder dialog state
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [newPath, setNewPath] = useState("")
  const [isCreating, setIsCreating] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  // Get the current folder path for prefilling (always returns a path)
  const currentFolderPath = useMemo(() => {
    if (selectedPath) {
      // If selected is a directory (ends with /), use it directly
      if (selectedPath.endsWith("/")) return selectedPath
      // Otherwise, get the parent directory
      const parts = selectedPath.split("/")
      parts.pop() // Remove filename
      return parts.length > 0 ? parts.join("/") + "/" : ""
    }
    // No selection - use project root as default
    return projectRoot ? projectRoot + "/" : ""
  }, [selectedPath, projectRoot])

  const toggleShowHidden = useCallback(() => {
    setShowHidden((prev) => {
      const next = !prev
      localStorage.setItem(SHOW_HIDDEN_KEY, String(next))
      return next
    })
  }, [])

  const toggleExpanded = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      localStorage.setItem(`${EXPANDED_KEY_PREFIX}${teamId}`, JSON.stringify([...next]))
      return next
    })
  }, [teamId])

  /** Fetch the root directory tree */
  const fetchTree = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `/api/files/${teamId}/tree?path=&depth=1&show_hidden=${showHidden}`,
        { headers: getAuthHeaders() }
      )

      if (!response.ok) {
        if (response.status === 404) {
          setError("Project not found for this team")
        } else {
          setError(`Failed to load files: ${response.status}`)
        }
        return
      }

      const data: TreeResponse = await response.json()
      setTree(data.tree)
      setProjectRoot(data.project_root)
      onProjectRootChange?.(data.project_root)
    } catch (err) {
      console.error("[FileTree] Error fetching tree:", err)
      setError("Failed to load file tree")
    } finally {
      setIsLoading(false)
    }
  }, [teamId, showHidden])

  /** Load children for a directory (lazy loading) */
  const loadChildren = useCallback(
    async (path: string): Promise<FileNode[]> => {
      try {
        const response = await fetch(
          `/api/files/${teamId}/tree?path=${encodeURIComponent(path)}&depth=1&show_hidden=${showHidden}`,
          { headers: getAuthHeaders() }
        )

        if (!response.ok) {
          console.error("[FileTree] Failed to load children:", response.status)
          return []
        }

        const data: TreeResponse = await response.json()
        return data.tree
      } catch (err) {
        console.error("[FileTree] Error loading children:", err)
        return []
      }
    },
    [teamId, showHidden]
  )

  /** Open create dialog with prefilled path */
  const handleOpenCreate = useCallback(() => {
    setNewPath(currentFolderPath)
    setCreateError(null)
    setIsCreateOpen(true)
  }, [currentFolderPath])

  /** Create a new file or folder */
  const handleCreate = useCallback(async () => {
    if (!newPath.trim()) {
      setCreateError("Path is required")
      return
    }

    setIsCreating(true)
    setCreateError(null)

    try {
      // Determine type: folder if ends with /, otherwise file
      const isFolder = newPath.endsWith("/")
      const cleanPath = isFolder ? newPath.slice(0, -1) : newPath

      const response = await fetch(`/api/files/${teamId}/create`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          path: cleanPath,
          type: isFolder ? "folder" : "file",
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        setCreateError(data.detail || `Failed to create: ${response.status}`)
        return
      }

      // Success - close dialog and refresh tree
      setIsCreateOpen(false)
      setNewPath("")
      await fetchTree()
    } catch (err) {
      console.error("[FileTree] Error creating:", err)
      setCreateError("Failed to create file/folder")
    } finally {
      setIsCreating(false)
    }
  }, [newPath, teamId, fetchTree])

  // Load tree on mount and when teamId changes
  useEffect(() => {
    fetchTree()
  }, [fetchTree])

  if (isLoading) {
    return <FileTreeSkeleton />
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4 gap-2">
        <AlertCircle className="h-6 w-6 text-destructive" />
        <p className="text-sm text-muted-foreground text-center">{error}</p>
        <Button variant="outline" size="sm" onClick={fetchTree}>
          <RefreshCw className="h-4 w-4 mr-1" />
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <span className="text-xs font-medium text-muted-foreground truncate" title={projectRoot}>
          {projectRoot.split("/").pop() || "Project"}
        </span>
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={handleOpenCreate}
                aria-label="Create file or folder"
              >
                <Plus className="h-3 w-3" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Create file/folder</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={toggleShowHidden}
                aria-label={showHidden ? "Hide hidden files" : "Show hidden files"}
              >
                {showHidden ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              {showHidden ? "Hide hidden files" : "Show hidden files"}
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={fetchTree}>
                <RefreshCw className="h-3 w-3" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Refresh</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {/* Tree */}
      <ScrollArea className="flex-1 h-full min-h-0">
        <div className="py-2" role="tree" aria-label="File tree" data-testid="file-tree">
          {tree.length > 0 ? (
            tree.map((node) => (
              <FileTreeItem
                key={node.path}
                node={node}
                level={0}
                selectedPath={selectedPath}
                onFileSelect={onFileSelect}
                onLoadChildren={loadChildren}
                teamId={teamId}
                expandedPaths={expandedPaths}
                onToggleExpanded={toggleExpanded}
                projectRoot={projectRoot}
                onRefresh={fetchTree}
              />
            ))
          ) : (
            <div className="px-4 py-2 text-sm text-muted-foreground italic">
              No files found
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Create File/Folder Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={(open) => {
        if (!isCreating) {
          setIsCreateOpen(open)
          if (!open) {
            setNewPath("")
            setCreateError(null)
          }
        }
      }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Create File or Folder</DialogTitle>
            <DialogDescription>
              Enter the path. End with <code className="bg-muted px-1 rounded">/</code> for folder.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-3">
            <Input
              placeholder="docs/new-file.txt or docs/new-folder/"
              value={newPath}
              onChange={(e) => setNewPath(e.target.value)}
              disabled={isCreating}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !isCreating) {
                  handleCreate()
                }
              }}
              autoFocus
            />
            <p className="text-xs text-muted-foreground">
              {newPath.endsWith("/") ? (
                <span className="text-amber-600">Creating folder: <code>{newPath.slice(0, -1) || "(empty)"}</code></span>
              ) : newPath ? (
                <span className="text-blue-600">Creating file: <code>{newPath}</code></span>
              ) : (
                <span>Type a path to create</span>
              )}
            </p>
            {createError && (
              <p className="text-sm text-destructive">{createError}</p>
            )}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCreateOpen(false)}
              disabled={isCreating}
            >
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={isCreating || !newPath.trim()}>
              {isCreating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
