/**
 * ContentSearch Component (Story 2: Word Search in File Browser)
 *
 * Searches file contents across project files
 * - Text input with search icon and clear button
 * - 300ms debounce (handled by useContentSearch hook)
 * - Shows results inline with file paths and match counts
 * - Click result → open file in viewer
 */

"use client"

import { useState } from 'react'
import { Search, X, FileText } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useContentSearch } from '@/hooks/useContentSearch'
import { cn } from '@/lib/utils'

interface ContentSearchProps {
  /** Team ID for API calls */
  teamId: string
  /** Callback when file is selected from results */
  onFileSelect: (path: string) => void
}

export function ContentSearch({ teamId, onFileSelect }: ContentSearchProps) {
  const [query, setQuery] = useState('')
  const { results, isLoading, error } = useContentSearch(teamId, query)

  const handleClear = () => {
    setQuery('')
  }

  const handleResultClick = (path: string) => {
    onFileSelect(path)
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
            placeholder="Search in files..."
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
              Searching...
            </div>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <div className="flex items-center justify-center p-4 text-sm text-destructive">
              {error}
            </div>
          )}

          {/* No Results */}
          {!isLoading && !error && results.length === 0 && (
            <div className="flex items-center justify-center p-4 text-sm text-muted-foreground">
              No results found
            </div>
          )}

          {/* Results List */}
          {!isLoading && !error && results.length > 0 && (
            <ScrollArea className="h-full">
              <div className="p-2 space-y-1">
                {results.map((result) => (
                  <button
                    key={result.path}
                    onClick={() => handleResultClick(result.path)}
                    className={cn(
                      "w-full flex items-start gap-2 p-2 rounded-md",
                      "hover:bg-accent hover:text-accent-foreground",
                      "transition-colors text-left"
                    )}
                  >
                    <FileText className="h-4 w-4 mt-0.5 flex-shrink-0 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">
                        {result.path}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {result.match_count} {result.match_count === 1 ? 'match' : 'matches'}
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
