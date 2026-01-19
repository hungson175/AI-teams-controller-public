"use client"

import { useState, useCallback, useEffect } from "react"
import { ChevronRight, ChevronDown, Folder, FolderOpen, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { getAuthHeaders } from "@/lib/auth-utils"

/**
 * Directory node in the tree
 */
interface DirectoryNode {
  name: string
  path: string
  type: "directory" | "file"
  size: number | null
  children?: DirectoryNode[]
}

/**
 * Props for DirectoryPicker component
 */
export interface DirectoryPickerProps {
  /** Callback when directory is selected */
  onSelect: (path: string) => void
  /** Callback when picker is cancelled (only used when not embedded) */
  onCancel?: () => void
  /** If true, hides header/footer and calls onSelect immediately on click */
  embedded?: boolean
  /** Whether to show hidden files/folders */
  showHidden?: boolean
  /** Callback when showHidden changes */
  onShowHiddenChange?: (show: boolean) => void
}

/**
 * Props for DirectoryTreeItem subcomponent
 */
interface DirectoryTreeItemProps {
  node: DirectoryNode
  level: number
  selectedPath: string | null
  onDirectoryClick: (path: string) => void
  onLoadChildren: (path: string) => Promise<DirectoryNode[]>
  expandedPaths: Set<string>
  onToggleExpanded: (path: string) => void
}

/**
 * DirectoryTreeItem - Renders a single directory in the tree
 */
function DirectoryTreeItem({
  node,
  level,
  selectedPath,
  onDirectoryClick,
  onLoadChildren,
  expandedPaths,
  onToggleExpanded,
}: DirectoryTreeItemProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [children, setChildren] = useState<DirectoryNode[]>(node.children || [])
  const [hasLoadedChildren, setHasLoadedChildren] = useState(!!node.children)

  const isSelected = selectedPath === node.path
  const isExpanded = expandedPaths.has(node.path)

  const handleClick = useCallback(async () => {
    // Select this directory
    onDirectoryClick(node.path)

    // Toggle expansion
    if (!isExpanded && !hasLoadedChildren) {
      setIsLoading(true)
      try {
        const loadedChildren = await onLoadChildren(node.path)
        // Filter to directories only
        const dirs = loadedChildren.filter(c => c.type === "directory")
        setChildren(dirs)
        setHasLoadedChildren(true)
        onToggleExpanded(node.path)
      } catch (error) {
        console.error("[DirectoryTreeItem] Failed to load children:", error)
      } finally {
        setIsLoading(false)
      }
    } else {
      onToggleExpanded(node.path)
    }
  }, [node.path, isExpanded, hasLoadedChildren, onDirectoryClick, onLoadChildren, onToggleExpanded])

  // Auto-load children if expanded but children not yet loaded
  useEffect(() => {
    if (isExpanded && !hasLoadedChildren && !isLoading) {
      const loadChildrenAsync = async () => {
        setIsLoading(true)
        try {
          const loadedChildren = await onLoadChildren(node.path)
          const dirs = loadedChildren.filter(c => c.type === "directory")
          setChildren(dirs)
          setHasLoadedChildren(true)
        } catch (error) {
          console.error("[DirectoryTreeItem] Failed to auto-load children:", error)
          onToggleExpanded(node.path)
        } finally {
          setIsLoading(false)
        }
      }
      loadChildrenAsync()
    }
  }, [isExpanded, hasLoadedChildren, isLoading, node.path, onLoadChildren, onToggleExpanded])

  return (
    <div>
      <div
        className={cn(
          "flex items-center gap-1 px-2 py-1 cursor-pointer hover:bg-muted/50 rounded-sm text-sm",
          isSelected && "bg-accent text-accent-foreground"
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={handleClick}
        role="treeitem"
        aria-selected={isSelected}
        aria-expanded={isExpanded}
      >
        {/* Expand/collapse chevron */}
        {isLoading ? (
          <Loader2 className="h-4 w-4 shrink-0 animate-spin text-muted-foreground" />
        ) : isExpanded ? (
          <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
        )}

        {/* Folder icon */}
        {isExpanded ? (
          <FolderOpen className="h-4 w-4 shrink-0 text-amber-500" />
        ) : (
          <Folder className="h-4 w-4 shrink-0 text-amber-500" />
        )}

        {/* Name */}
        <span className="truncate">{node.name}</span>
      </div>

      {/* Children (only for expanded directories) */}
      {isExpanded && (
        <div role="group">
          {children.length > 0 ? (
            children.map((child) => (
              <DirectoryTreeItem
                key={child.path}
                node={child}
                level={level + 1}
                selectedPath={selectedPath}
                onDirectoryClick={onDirectoryClick}
                onLoadChildren={onLoadChildren}
                expandedPaths={expandedPaths}
                onToggleExpanded={onToggleExpanded}
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
    </div>
  )
}

/**
 * DirectoryPicker Component
 *
 * A directory browser for selecting a starting directory.
 * Shows only directories (no files) in a tree structure.
 * Used in New Terminal dialog for directory selection.
 */
export function DirectoryPicker({ onSelect, onCancel, embedded = false, showHidden = false, onShowHiddenChange }: DirectoryPickerProps) {
  const [directories, setDirectories] = useState<DirectoryNode[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set())

  /**
   * Load directories from API
   */
  const loadDirectories = useCallback(async (path: string): Promise<DirectoryNode[]> => {
    const encodedPath = encodeURIComponent(path)
    const response = await fetch(`/api/system/directories?path=${encodedPath}&show_hidden=${showHidden}`, {
      headers: getAuthHeaders(),
    })

    if (!response.ok) {
      throw new Error(`Failed to load directories: ${response.status}`)
    }

    const data = await response.json()
    // Filter to directories only
    return (data.tree || []).filter((node: DirectoryNode) => node.type === "directory")
  }, [showHidden])

  /**
   * Load root directories on mount and when showHidden changes
   */
  useEffect(() => {
    const loadRoot = async () => {
      setIsLoading(true)
      setError(null)
      setExpandedPaths(new Set()) // Reset expanded state when reloading
      try {
        const dirs = await loadDirectories("~")
        setDirectories(dirs)
      } catch (err) {
        console.error("[DirectoryPicker] Failed to load directories:", err)
        setError("Failed to load directories")
      } finally {
        setIsLoading(false)
      }
    }
    loadRoot()
  }, [loadDirectories, showHidden])

  /**
   * Toggle directory expansion
   */
  const handleToggleExpanded = useCallback((path: string) => {
    setExpandedPaths(prev => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }, [])

  /**
   * Handle directory selection
   */
  const handleDirectoryClick = useCallback((path: string) => {
    setSelectedPath(path)
    // In embedded mode, call onSelect immediately
    if (embedded) {
      onSelect(path)
    }
  }, [embedded, onSelect])

  /**
   * Handle Select button click
   */
  const handleSelect = useCallback(() => {
    if (selectedPath) {
      onSelect(selectedPath)
    }
  }, [selectedPath, onSelect])

  return (
    <div className={cn("flex flex-col overflow-hidden", embedded ? "h-full" : "h-[300px]")}>
      {/* Header - hidden in embedded mode */}
      {!embedded && (
        <div className="pb-2 border-b mb-2 shrink-0">
          <h3 className="text-sm font-medium">Select Directory</h3>
        </div>
      )}

      {/* Directory tree - scrollable */}
      <ScrollArea className="flex-1 min-h-0">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="text-sm text-destructive p-4 text-center">
            {error}
          </div>
        ) : (
          <div role="tree">
            {directories.map((dir) => (
              <DirectoryTreeItem
                key={dir.path}
                node={dir}
                level={0}
                selectedPath={selectedPath}
                onDirectoryClick={handleDirectoryClick}
                onLoadChildren={loadDirectories}
                expandedPaths={expandedPaths}
                onToggleExpanded={handleToggleExpanded}
              />
            ))}
          </div>
        )}
      </ScrollArea>

      {/* Selected path display - hidden in embedded mode (parent shows it) */}
      {!embedded && selectedPath && (
        <div className="py-2 border-t mt-2 shrink-0">
          <p className="text-xs text-muted-foreground">Selected:</p>
          <p className="text-sm font-mono truncate">{selectedPath}</p>
        </div>
      )}

      {/* Footer with buttons - hidden in embedded mode */}
      {!embedded && (
        <div className="flex justify-end gap-2 pt-2 border-t mt-2 shrink-0">
          <Button variant="outline" size="sm" onClick={onCancel}>
            Cancel
          </Button>
          <Button size="sm" onClick={handleSelect} disabled={!selectedPath}>
            Select
          </Button>
        </div>
      )}
    </div>
  )
}
