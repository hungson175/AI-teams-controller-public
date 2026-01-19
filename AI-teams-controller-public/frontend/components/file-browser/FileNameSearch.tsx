/**
 * FileNameSearch Component (Story 2 REVISED: Filename Search)
 *
 * Inline fuzzy search for file/folder names
 * - Empty query: Hide results (FileTree shows)
 * - Has query: Show fuzzy results inline
 * - Click result: Open file, clear query
 */

"use client"

import { useState, useMemo } from 'react'
import uFuzzy from '@leeoniya/ufuzzy'
import { Search, X, FileText } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useFileListCache } from '@/hooks/useFileListCache'
import { cn } from '@/lib/utils'

interface FileNameSearchProps {
  /** Team ID for API calls */
  teamId: string
  /** Callback when file is selected from results */
  onFileSelect: (path: string) => void
}

// uFuzzy configuration (same as FileSearch.tsx)
const uf = new uFuzzy({
  intraMode: 1, // Allow gaps between characters
  intraIns: 1,
  interIns: 3,
})

export function FileNameSearch({ teamId, onFileSelect }: FileNameSearchProps) {
  const [query, setQuery] = useState('')
  const { files, isLoading } = useFileListCache(teamId)

  // Perform fuzzy search
  const searchResults = useMemo(() => {
    if (!query.trim()) {
      return []
    }

    const results = uf.search(files, query)
    if (!results || !results[0]) return []

    const [indexes, info, order] = results
    if (!indexes || indexes.length === 0) return []

    // Use order if available (sorted by relevance)
    const sortedIndexes = order || indexes
    return sortedIndexes.slice(0, 50).map(idx => files[idx])
  }, [query, files])

  const handleClear = () => {
    setQuery('')
  }

  const handleResultClick = (path: string) => {
    onFileSelect(path)
    setQuery('') // Clear query after selection
  }

  // Show results section only if query is not empty
  const showResults = query.trim() !== ''

  return (
    <div className="flex flex-col">
      {/* Search Input */}
      <div className="flex items-center gap-2 px-3 py-2 border-b">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search files..."
            className="pl-9 pr-9"
          />
          {query && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6"
              onClick={handleClear}
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Results Section */}
      {showResults && (
        <div className="flex-1 min-h-0">
          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center p-4 text-sm text-muted-foreground">
              Loading files...
            </div>
          )}

          {/* No Results */}
          {!isLoading && searchResults.length === 0 && (
            <div className="flex items-center justify-center p-4 text-sm text-muted-foreground">
              No files found
            </div>
          )}

          {/* Results List */}
          {!isLoading && searchResults.length > 0 && (
            <ScrollArea className="h-[400px]">
              <div className="p-2 space-y-1">
                {searchResults.map((filePath) => (
                  <button
                    key={filePath}
                    onClick={() => handleResultClick(filePath)}
                    className={cn(
                      "w-full flex items-start gap-2 p-2 rounded-md",
                      "hover:bg-accent hover:text-accent-foreground",
                      "transition-colors text-left"
                    )}
                  >
                    <FileText className="h-4 w-4 mt-0.5 flex-shrink-0 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">
                        {filePath}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </ScrollArea>
          )}
        </div>
      )}
    </div>
  )
}
