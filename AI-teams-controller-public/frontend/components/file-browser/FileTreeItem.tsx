"use client"

import { useState, useCallback, useEffect } from "react"
import { ChevronRight, ChevronDown, Folder, FolderOpen, Loader2, Copy, Trash2, Pencil } from "lucide-react"
import { cn } from "@/lib/utils"
import { FileIcon } from "./file-icons"
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { getAuthHeaders } from "@/lib/auth-utils"
import type { FileNode } from "./types"

interface FileTreeItemProps {
  /** The file node to render */
  node: FileNode
  /** Current indentation level */
  level: number
  /** Currently selected file path */
  selectedPath: string | null
  /** Callback when a file is clicked */
  onFileSelect: (path: string) => void
  /** Callback to load children for a directory */
  onLoadChildren: (path: string) => Promise<FileNode[]>
  /** Team ID for API calls */
  teamId: string
  /** Set of expanded folder paths */
  expandedPaths: Set<string>
  /** Callback to toggle folder expansion */
  onToggleExpanded: (path: string) => void
  /** Project root path for full path construction */
  projectRoot: string
  /** Callback to refresh tree after mutation */
  onRefresh: () => void
}

/**
 * FileTreeItem Component
 *
 * Renders a single file or directory in the file tree.
 * Directories can be expanded/collapsed on click.
 * Files trigger the onFileSelect callback when clicked.
 */
export function FileTreeItem({
  node,
  level,
  selectedPath,
  onFileSelect,
  onLoadChildren,
  teamId,
  expandedPaths,
  onToggleExpanded,
  projectRoot,
  onRefresh,
}: FileTreeItemProps) {
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [children, setChildren] = useState<FileNode[]>(node.children || [])
  const [hasLoadedChildren, setHasLoadedChildren] = useState(!!node.children)

  // Delete dialog state
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  // Rename dialog state
  const [isRenameOpen, setIsRenameOpen] = useState(false)
  const [newName, setNewName] = useState("")
  const [isRenaming, setIsRenaming] = useState(false)
  const [renameError, setRenameError] = useState<string | null>(null)

  const isDirectory = node.type === "directory"
  const isSelected = selectedPath === node.path
  const isExpanded = expandedPaths.has(node.path)

  const handleCopyPath = useCallback(async () => {
    try {
      // Construct full path by combining project root with relative path
      const fullPath = node.path ? `${projectRoot}/${node.path}` : projectRoot
      await navigator.clipboard.writeText(fullPath)
      toast({
        title: "Path copied",
        description: "Full path copied to clipboard",
      })
    } catch (err) {
      console.error("[FileTreeItem] Failed to copy path:", err)
      toast({
        title: "Failed to copy",
        description: "Could not copy path to clipboard",
        variant: "destructive",
      })
    }
  }, [node.path, projectRoot, toast])

  const handleOpenRename = useCallback(() => {
    setNewName(node.name) // Pre-fill with current name
    setRenameError(null)
    setIsRenameOpen(true)
  }, [node.name])

  const handleRename = useCallback(async () => {
    if (!newName.trim() || newName === node.name) {
      setIsRenameOpen(false)
      return
    }

    setIsRenaming(true)
    setRenameError(null)

    try {
      const response = await fetch(`/api/files/${teamId}/rename`, {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          old_path: node.path,
          new_name: newName.trim(),
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        setRenameError(data.detail || "Could not rename item")
        return
      }

      toast({
        title: "Renamed",
        description: `Successfully renamed to ${newName}`,
      })
      setIsRenameOpen(false)
      onRefresh()
    } catch (err) {
      setRenameError("Network error")
    } finally {
      setIsRenaming(false)
    }
  }, [teamId, node.path, node.name, newName, toast, onRefresh])

  const handleDelete = useCallback(async () => {
    setIsDeleting(true)
    try {
      const response = await fetch(`/api/files/${teamId}/delete`, {
        method: "DELETE",
        headers: getAuthHeaders(),
        body: JSON.stringify({ path: node.path }),
      })

      if (!response.ok) {
        const data = await response.json()
        toast({
          title: "Delete failed",
          description: data.detail || "Could not delete item",
          variant: "destructive",
        })
        return
      }

      toast({
        title: "Deleted",
        description: `${node.type === "directory" ? "Folder" : "File"} deleted successfully`,
      })
      setIsDeleteOpen(false)
      onRefresh()
    } catch (err) {
      toast({
        title: "Delete failed",
        description: "Network error",
        variant: "destructive",
      })
    } finally {
      setIsDeleting(false)
    }
  }, [teamId, node.path, node.type, toast, onRefresh])

  const handleClick = useCallback(async () => {
    if (isDirectory) {
      // Toggle expansion for directories
      if (!isExpanded && !hasLoadedChildren) {
        // Need to load children first
        setIsLoading(true)
        try {
          const loadedChildren = await onLoadChildren(node.path)
          setChildren(loadedChildren)
          setHasLoadedChildren(true)
          onToggleExpanded(node.path)
        } catch (error) {
          console.error("[FileTreeItem] Failed to load children:", error)
        } finally {
          setIsLoading(false)
        }
      } else {
        onToggleExpanded(node.path)
      }
    } else {
      // Select file
      onFileSelect(node.path)
    }
  }, [isDirectory, isExpanded, hasLoadedChildren, node.path, onFileSelect, onLoadChildren, onToggleExpanded])

  // Auto-load children if expanded from localStorage but children not yet loaded
  useEffect(() => {
    if (isDirectory && isExpanded && !hasLoadedChildren && !isLoading) {
      const loadChildrenAsync = async () => {
        setIsLoading(true)
        try {
          const loadedChildren = await onLoadChildren(node.path)
          setChildren(loadedChildren)
          setHasLoadedChildren(true)
        } catch (error) {
          console.error("[FileTreeItem] Failed to auto-load children:", error)
          // Remove from expanded paths if load fails
          onToggleExpanded(node.path)
        } finally {
          setIsLoading(false)
        }
      }
      loadChildrenAsync()
    }
  }, [isDirectory, isExpanded, hasLoadedChildren, isLoading, node.path, onLoadChildren, onToggleExpanded])

  return (
    <div>
      {/* Item row with context menu */}
      <ContextMenu>
        <ContextMenuTrigger asChild>
          <div
            className={cn(
              "flex items-center gap-1 px-2 py-1 cursor-pointer hover:bg-muted/50 rounded-sm text-sm",
              isSelected && "bg-accent text-accent-foreground"
            )}
            style={{ paddingLeft: `${level * 16 + 8}px` }}
            onClick={handleClick}
            role="treeitem"
            aria-selected={isSelected}
            aria-expanded={isDirectory ? isExpanded : undefined}
          >
            {/* Expand/collapse chevron for directories */}
            {isDirectory ? (
              isLoading ? (
                <Loader2 className="h-4 w-4 shrink-0 animate-spin text-muted-foreground" />
              ) : isExpanded ? (
                <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
              )
            ) : (
              <span className="w-4" /> // Spacer for files to align with folders
            )}

            {/* Icon */}
            {isDirectory ? (
              isExpanded ? (
                <FolderOpen className="h-4 w-4 shrink-0 text-amber-500" />
              ) : (
                <Folder className="h-4 w-4 shrink-0 text-amber-500" />
              )
            ) : (
              <FileIcon fileName={node.name} />
            )}

            {/* Name */}
            <span className="truncate">{node.name}</span>
          </div>
        </ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem onClick={handleCopyPath}>
            <Copy className="h-4 w-4 mr-2" />
            Copy Path
          </ContextMenuItem>
          <ContextMenuItem onClick={handleOpenRename}>
            <Pencil className="h-4 w-4 mr-2" />
            Rename
          </ContextMenuItem>
          <ContextMenuItem
            onClick={() => setIsDeleteOpen(true)}
            className="text-destructive focus:text-destructive"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>

      {/* Children (only for expanded directories) */}
      {isDirectory && isExpanded && (
        <div role="group">
          {children.length > 0 ? (
            children.map((child) => (
              <FileTreeItem
                key={child.path}
                node={child}
                level={level + 1}
                selectedPath={selectedPath}
                onFileSelect={onFileSelect}
                onLoadChildren={onLoadChildren}
                teamId={teamId}
                expandedPaths={expandedPaths}
                onToggleExpanded={onToggleExpanded}
                projectRoot={projectRoot}
                onRefresh={onRefresh}
              />
            ))
          ) : (
            <div
              className="text-xs text-muted-foreground italic px-2 py-1"
              style={{ paddingLeft: `${(level + 1) * 16 + 8}px` }}
            >
              Empty directory
            </div>
          )}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {node.type === "directory" ? "folder" : "file"}?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{node.name}</strong>?
              {node.type === "directory" && " This will delete all contents inside."}
              {" "}This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Rename Dialog */}
      <Dialog
        open={isRenameOpen}
        onOpenChange={(open) => {
          if (!isRenaming) {
            setIsRenameOpen(open)
            if (!open) {
              setNewName("")
              setRenameError(null)
            }
          }
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Rename {node.type === "directory" ? "folder" : "file"}</DialogTitle>
            <DialogDescription>
              Enter a new name for <strong>{node.name}</strong>
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-3">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="New name"
              disabled={isRenaming}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !isRenaming) {
                  handleRename()
                }
              }}
              autoFocus
            />
            {renameError && <p className="text-sm text-destructive">{renameError}</p>}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsRenameOpen(false)} disabled={isRenaming}>
              Cancel
            </Button>
            <Button onClick={handleRename} disabled={isRenaming || !newName.trim()}>
              {isRenaming ? "Renaming..." : "Rename"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
