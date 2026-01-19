"use client"

import { useState, useEffect, useCallback, useRef, useMemo } from "react"
import uFuzzy from "@leeoniya/ufuzzy"
import { Search, File, Folder, X } from "lucide-react"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { getAuthHeaders } from "@/lib/auth-utils"

interface FileItem {
  path: string
  isDir: boolean
}

interface FileSearchProps {
  teamId: string
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  onFileSelect: (path: string) => void
}

// uFuzzy configuration optimized for file paths
const uf = new uFuzzy({
  intraMode: 1, // Allow gaps between characters
  intraIns: 1,
  interIns: 3,
})

/**
 * FileSearch Component (Cmd+P style)
 *
 * Sprint 3 Story 3: File name search with fuzzy matching
 * Uses uFuzzy for instant client-side search over cached file list.
 */
export function FileSearch({ teamId, isOpen, onOpenChange, onFileSelect }: FileSearchProps) {
  const [query, setQuery] = useState("")
  const [files, setFiles] = useState<FileItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  // Use full paths for search (allows searching by directory names like 'components', 'hooks')
  const filePaths = useMemo(() => files.map(f => f.path), [files])

  // Perform fuzzy search
  const searchResults = useMemo(() => {
    if (!query.trim()) {
      // Show all files (limited) when no query
      return files.slice(0, 50).map((f, i) => ({ item: f, index: i }))
    }

    const results = uf.search(filePaths, query)
    if (!results || !results[0]) return []

    const [indexes, info, order] = results
    if (!indexes || indexes.length === 0) return []

    // Use order if available (sorted by relevance)
    const sortedIndexes = order || indexes

    // Re-rank to prioritize filename matches (Boss requirement)
    const rerankedIndexes = [...sortedIndexes].sort((a, b) => {
      const fileA = files[a].path.split('/').pop()?.toLowerCase() || ''
      const fileB = files[b].path.split('/').pop()?.toLowerCase() || ''
      const q = query.toLowerCase()

      // 1. Exact filename match first
      if (fileA === q && fileB !== q) return -1
      if (fileB === q && fileA !== q) return 1

      // 2. Filename starts with query
      if (fileA.startsWith(q) && !fileB.startsWith(q)) return -1
      if (fileB.startsWith(q) && !fileA.startsWith(q)) return 1

      // 3. Filename contains query
      if (fileA.includes(q) && !fileB.includes(q)) return -1
      if (fileB.includes(q) && !fileA.includes(q)) return 1

      // 4. Keep uFuzzy order for remaining
      return 0
    })

    return rerankedIndexes.slice(0, 50).map(idx => ({
      item: files[idx],
      index: idx,
      highlight: info?.idx?.[order ? rerankedIndexes.indexOf(idx) : indexes.indexOf(idx)]
    }))
  }, [query, files, filePaths])

  // Fetch file list when dialog opens
  useEffect(() => {
    if (!isOpen || !teamId) return

    const fetchFiles = async () => {
      setIsLoading(true)
      try {
        const response = await fetch(
          `/api/files/${teamId}/list?limit=10000&show_hidden=false`,
          { headers: getAuthHeaders() }
        )
        if (response.ok) {
          const data = await response.json()
          // Filter to only files (not directories) for search
          setFiles(data.files.filter((f: FileItem) => !f.isDir))
        }
      } catch (err) {
        console.error("[FileSearch] Failed to fetch files:", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchFiles()
  }, [isOpen, teamId])

  // Focus input when dialog opens
  useEffect(() => {
    if (isOpen) {
      setQuery("")
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  // Scroll selected item into view
  useEffect(() => {
    if (!listRef.current) return
    const selectedEl = listRef.current.querySelector(`[data-index="${selectedIndex}"]`)
    selectedEl?.scrollIntoView({ block: "nearest" })
  }, [selectedIndex])

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault()
        setSelectedIndex(prev => Math.min(prev + 1, searchResults.length - 1))
        break
      case "ArrowUp":
        e.preventDefault()
        setSelectedIndex(prev => Math.max(prev - 1, 0))
        break
      case "Enter":
        e.preventDefault()
        if (searchResults[selectedIndex]) {
          onFileSelect(searchResults[selectedIndex].item.path)
          onOpenChange(false)
        }
        break
      case "Escape":
        e.preventDefault()
        onOpenChange(false)
        break
    }
  }, [searchResults, selectedIndex, onFileSelect, onOpenChange])

  // Handle item click
  const handleItemClick = useCallback((path: string) => {
    onFileSelect(path)
    onOpenChange(false)
  }, [onFileSelect, onOpenChange])

  // Highlight matched characters in file name
  const highlightMatch = (path: string, fileName: string) => {
    if (!query.trim()) return fileName

    // Simple highlight - mark matching characters
    const lowerQuery = query.toLowerCase()
    const lowerName = fileName.toLowerCase()
    let result = ""
    let queryIdx = 0

    for (let i = 0; i < fileName.length; i++) {
      if (queryIdx < lowerQuery.length && lowerName[i] === lowerQuery[queryIdx]) {
        result += `<mark class="bg-yellow-200 dark:bg-yellow-800 rounded">${fileName[i]}</mark>`
        queryIdx++
      } else {
        result += fileName[i]
      }
    }

    return result
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] p-0 gap-0">
        <DialogHeader className="p-4 pb-0">
          <DialogTitle className="sr-only">Search Files</DialogTitle>
        </DialogHeader>

        {/* Search Input */}
        <div className="flex items-center gap-2 px-4 pb-2 border-b">
          <Search className="h-4 w-4 text-muted-foreground shrink-0" />
          <Input
            ref={inputRef}
            placeholder="Search files by name..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setSelectedIndex(0)
            }}
            onKeyDown={handleKeyDown}
            className="border-0 shadow-none focus-visible:ring-0 px-0"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Results List */}
        <ScrollArea className="max-h-[400px]">
          <div ref={listRef} className="py-2">
            {isLoading ? (
              <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                Loading files...
              </div>
            ) : searchResults.length === 0 ? (
              <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                {query ? "No files found" : "No files in project"}
              </div>
            ) : (
              searchResults.map((result, idx) => {
                const fileName = result.item.path.split("/").pop() || result.item.path
                const dirPath = result.item.path.split("/").slice(0, -1).join("/")

                return (
                  <div
                    key={result.item.path}
                    data-index={idx}
                    onClick={() => handleItemClick(result.item.path)}
                    className={`
                      flex items-center gap-2 px-4 py-2 cursor-pointer
                      ${idx === selectedIndex
                        ? "bg-accent text-accent-foreground"
                        : "hover:bg-muted/50"
                      }
                    `}
                  >
                    {result.item.isDir ? (
                      <Folder className="h-4 w-4 text-blue-500 shrink-0" />
                    ) : (
                      <File className="h-4 w-4 text-muted-foreground shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <div
                        className="font-medium truncate"
                        dangerouslySetInnerHTML={{
                          __html: highlightMatch(result.item.path, fileName)
                        }}
                      />
                      {dirPath && (
                        <div className="text-xs text-muted-foreground truncate">
                          {dirPath}
                        </div>
                      )}
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </ScrollArea>

        {/* Footer hint */}
        <div className="px-4 py-2 border-t text-xs text-muted-foreground flex items-center gap-4">
          <span><kbd className="px-1 rounded bg-muted">↑↓</kbd> Navigate</span>
          <span><kbd className="px-1 rounded bg-muted">Enter</kbd> Open</span>
          <span><kbd className="px-1 rounded bg-muted">Esc</kbd> Close</span>
        </div>
      </DialogContent>
    </Dialog>
  )
}
