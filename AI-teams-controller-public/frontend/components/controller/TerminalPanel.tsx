"use client"

import { ReactNode, useRef, useEffect, useState, useMemo, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Send, ArrowDown, X, Terminal, MessageSquare, Square } from "lucide-react"
import { cn } from "@/lib/utils"
import { parseAnsiToHtml, stripAnsi } from "@/lib/ansi-parser"
import { createCommandSearch } from "@/lib/fuzzy-search"
import { detectFilePaths, FilePath } from "@/lib/filePathParser"
import { TerminalFileLink } from "@/components/terminal/TerminalFileLink"
import { AutocompleteDropdown } from "@/components/terminal/AutocompleteDropdown"
import { useCommandHistory } from "@/components/terminal/CommandHistory"

/**
 * Role type for terminal tabs
 */
type Role = {
  id: string
  name: string
  order: number
  isActive?: boolean
}

/**
 * Pane state containing terminal output
 */
type PaneState = {
  output: string
  lastUpdated: string
  highlightText?: string | null
  isActive?: boolean
}

/**
 * Props for TerminalPanel component
 */
export interface TerminalPanelProps {
  /** List of available roles to display as tabs */
  roles: Role[]
  /** Currently selected role ID */
  selectedRole: string | null
  /** Map of role ID to activity status */
  roleActivity: Record<string, boolean>
  /** Current pane output state */
  currentPaneState: PaneState | null
  /** Current input field value */
  inputValue: string
  /** Whether a message is being sent */
  isPending: boolean
  /** Whether auto-scroll is enabled */
  isAutoScrollEnabled: boolean
  /** Whether to show the scroll-to-bottom FAB */
  showScrollFab: boolean
  /** Current voice transcript text */
  voiceTranscript: string
  /** Current voice status (listening, correcting, sent) */
  voiceStatus: string
  /** Currently selected team ID */
  selectedTeam: string | null
  /** Callback when role tab changes */
  onRoleChange: (roleId: string) => void
  /** Callback when input value changes */
  onInputChange: (value: string) => void
  /** Callback when message is sent */
  onSendMessage: () => void
  /** Callback to send Escape key (stop Claude Code) */
  onSendEscape: () => void
  /** Callback to scroll to bottom */
  onScrollToBottom: () => void
  /** Callback to clear voice transcript */
  onClearTranscript: () => void
  /** Callback when output area is scrolled */
  onScroll: () => void
  /** Ref to the output container */
  outputRef: React.RefObject<HTMLDivElement | null>
}

/**
 * TerminalPanel Component
 *
 * Main terminal interface with role tabs, output display, and input area.
 *
 * Features:
 * - Role tabs with activity indicators
 * - Terminal output with user request highlighting
 * - Auto-scroll controls and scroll-to-bottom FAB
 * - Message input with voice transcript display
 * - Text highlighting for search matches
 */
export function TerminalPanel({
  roles,
  selectedRole,
  roleActivity,
  currentPaneState,
  inputValue,
  isPending,
  isAutoScrollEnabled,
  showScrollFab,
  voiceTranscript,
  voiceStatus,
  selectedTeam,
  onRoleChange,
  onInputChange,
  onSendMessage,
  onSendEscape,
  onScrollToBottom,
  onClearTranscript,
  onScroll,
  outputRef,
}: TerminalPanelProps) {
  // Ref for input field to maintain focus
  const inputRef = useRef<HTMLInputElement>(null)

  // Terminal mode state (Chat mode = false, Terminal mode = true)
  const [isTerminalMode, setIsTerminalMode] = useState(false)

  // Command history for Terminal mode (extracted hook)
  const {
    history: commandHistory,
    historyIndex,
    savedInput,
    addToHistory,
    navigateUp: navigateHistoryUp,
    navigateDown: navigateHistoryDown,
    reset: resetHistory,
  } = useCommandHistory({ isTerminalMode })

  // Autocomplete state - dismissed tracks if user closed dropdown (resets on input change)
  const [suggestionIndex, setSuggestionIndex] = useState(0)
  const [suggestionsDismissed, setSuggestionsDismissed] = useState(false)

  // Path API state for async path completions
  const [pathSuggestions, setPathSuggestions] = useState<string[]>([])
  const [isLoadingPaths, setIsLoadingPaths] = useState(false)
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null)

  // Common command suggestions for Terminal mode
  const COMMAND_SUGGESTIONS = [
    "run tests",
    "run pytest",
    "run build",
    "fix the bug",
    "check the logs",
    "git status",
    "git diff",
    "git commit",
    "read file",
    "search for",
    "explain this code",
    "refactor",
    "add tests for",
    "create a new",
    "update the",
    "delete",
    "list files",
    "show me",
  ]

  // Common path suggestions for Tab completion
  const PATH_SUGGESTIONS = [
    "src/",
    "lib/",
    "app/",
    "components/",
    "hooks/",
    "utils/",
    "services/",
    "api/",
    "tests/",
    "docs/",
    "config/",
    "public/",
    "assets/",
    "styles/",
    "../",
    "./",
  ]

  // Detect if input looks like a path
  const isPathInput = inputValue.includes("/") || inputValue.startsWith(".")

  // Debounced path autocomplete fetch
  const fetchPathSuggestions = useCallback(
    async (partial: string, team: string) => {
      if (!partial || partial.length < 1 || !team) {
        setPathSuggestions([])
        setIsLoadingPaths(false)
        return
      }

      setIsLoadingPaths(true)
      try {
        const res = await fetch(
          `/api/files/autocomplete?path=${encodeURIComponent(partial)}&team=${encodeURIComponent(team)}`
        )
        if (res.ok) {
          const data = await res.json()
          setPathSuggestions(data.completions.map((c: { path: string }) => c.path))
        } else {
          setPathSuggestions([])
        }
      } catch (e) {
        console.error("Path autocomplete error:", e)
        setPathSuggestions([])
      } finally {
        setIsLoadingPaths(false)
      }
    },
    []
  )

  // Trigger path fetch when input changes (debounced)
  useEffect(() => {
    if (isTerminalMode && isPathInput && selectedTeam) {
      // Clear previous timer
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }

      // Set new debounce timer
      debounceTimerRef.current = setTimeout(() => {
        fetchPathSuggestions(inputValue, selectedTeam)
      }, 200)
    } else {
      // Clear suggestions when not in path mode
      setPathSuggestions([])
      setIsLoadingPaths(false)
    }

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [inputValue, isTerminalMode, isPathInput, selectedTeam, fetchPathSuggestions])

  // Create fuzzy search function for commands (memoized)
  const commandSearch = useMemo(
    () => createCommandSearch(COMMAND_SUGGESTIONS),
    []
  )

  // Filter suggestions based on input type using fuzzy search
  const filteredSuggestions = useMemo(() => {
    if (!isTerminalMode || inputValue.length < 1) return []

    if (isPathInput) {
      // Path completion mode - use API results when available
      if (pathSuggestions.length > 0) {
        return pathSuggestions.slice(0, 5)
      }

      // If loading paths, don't show fallback suggestions (show loading indicator instead)
      if (isLoadingPaths) {
        return []
      }

      // Fallback to static suggestions if no API results
      const lastSlash = inputValue.lastIndexOf("/")
      const prefix = lastSlash >= 0 ? inputValue.substring(lastSlash + 1) : inputValue
      const basePath = lastSlash >= 0 ? inputValue.substring(0, lastSlash + 1) : ""

      return PATH_SUGGESTIONS
        .filter(path => path.toLowerCase().startsWith(prefix.toLowerCase()))
        .map(path => basePath + path)
        .slice(0, 5)
    } else if (inputValue.length >= 2) {
      // Command completion mode - use fuzzy search
      return commandSearch(inputValue, 5)
    }

    return []
  }, [isTerminalMode, inputValue, isPathInput, commandSearch, pathSuggestions, isLoadingPaths])

  // Compute showSuggestions directly - no useEffect needed
  const showSuggestions = filteredSuggestions.length > 0 && historyIndex === -1 && !suggestionsDismissed

  // Reset dismissed state and suggestion index when input changes
  useEffect(() => {
    setSuggestionsDismissed(false)
    setSuggestionIndex(0)
  }, [inputValue])

  // Refocus input when isPending changes from true to false (message sent)
  useEffect(() => {
    if (!isPending && inputRef.current) {
      // Small delay to ensure state updates are complete
      const timer = setTimeout(() => {
        inputRef.current?.focus()
      }, 50)
      return () => clearTimeout(timer)
    }
  }, [isPending])

  /**
   * Select a suggestion and apply it to input
   */
  const selectSuggestion = (suggestion: string) => {
    onInputChange(suggestion)
    setSuggestionsDismissed(true)
    setSuggestionIndex(0)
    inputRef.current?.focus()
  }

  /**
   * Handle keyboard events for command history navigation and autocomplete
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Enter key - send message and save to history
    if (e.key === "Enter" && !e.shiftKey) {
      if (inputValue.trim() && isTerminalMode) {
        addToHistory(inputValue)
      }
      setSuggestionsDismissed(true)
      onSendMessage()
      return
    }

    // Only handle special keys in Terminal mode
    if (!isTerminalMode) return

    // Escape key - close suggestions
    if (e.key === "Escape") {
      if (showSuggestions) {
        e.preventDefault()
        setSuggestionsDismissed(true)
      }
      return
    }

    // Tab key - select current suggestion
    if (e.key === "Tab" && showSuggestions && filteredSuggestions.length > 0) {
      e.preventDefault()
      selectSuggestion(filteredSuggestions[suggestionIndex])
      return
    }

    // Arrow keys - navigate suggestions or history
    if (e.key === "ArrowUp") {
      e.preventDefault()

      // If suggestions are shown, navigate suggestions
      if (showSuggestions && filteredSuggestions.length > 0) {
        setSuggestionIndex(prev =>
          prev > 0 ? prev - 1 : filteredSuggestions.length - 1
        )
        return
      }

      // Otherwise navigate command history using hook
      const command = navigateHistoryUp(inputValue)
      if (command !== null) {
        onInputChange(command)
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault()

      // If suggestions are shown, navigate suggestions
      if (showSuggestions && filteredSuggestions.length > 0) {
        setSuggestionIndex(prev =>
          prev < filteredSuggestions.length - 1 ? prev + 1 : 0
        )
        return
      }

      // Otherwise navigate command history using hook
      const command = navigateHistoryDown()
      if (command !== null) {
        onInputChange(command)
      }
    }
  }

  /**
   * Escape special regex characters in a string
   */
  const escapeRegex = (str: string): string => {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }

  /**
   * Render a single line with file path detection
   * Splits line into text parts and TerminalFileLink components
   */
  const renderLineWithFilePaths = (
    line: string,
    lineIndex: number,
    highlightText?: string | null
  ): ReactNode => {
    const isUserRequest = line.trimStart().startsWith('>')

    // Detect file paths in the line (before ANSI parsing)
    const strippedLine = stripAnsi(line)
    const filePaths = detectFilePaths(strippedLine)

    // If no file paths, render as before (HTML string)
    if (filePaths.length === 0) {
      let htmlContent = parseAnsiToHtml(line)

      // Apply text highlighting
      if (highlightText) {
        const escapedHighlight = escapeRegex(highlightText)
        const highlightHtml = `<span class="highlight-message bg-yellow-500/20 text-yellow-200 px-1 rounded">${highlightText}</span>`
        htmlContent = htmlContent.replace(new RegExp(escapedHighlight, 'g'), highlightHtml)
      }

      return (
        <span key={lineIndex}>
          {isUserRequest ? (
            <span
              className="bg-primary/10 block -mx-2 sm:-mx-4 px-2 sm:px-4"
              dangerouslySetInnerHTML={{ __html: htmlContent }}
            />
          ) : (
            <span dangerouslySetInnerHTML={{ __html: htmlContent }} />
          )}
          {'\n'}
        </span>
      )
    }

    // Split line into parts: text and file paths
    const parts: ReactNode[] = []
    let lastIndex = 0

    filePaths.forEach((filePath, fpIndex) => {
      // Add text before this file path
      if (filePath.startIndex > lastIndex) {
        const textBefore = strippedLine.substring(lastIndex, filePath.startIndex)
        parts.push(
          <span key={`text-${lineIndex}-${fpIndex}`}>
            {textBefore}
          </span>
        )
      }

      // Add TerminalFileLink component
      // Use stable key based on path content, not line index
      // This prevents component unmount/remount when terminal output changes
      const stableKey = `${filePath.path}-${filePath.lineNumber || 0}-${filePath.columnNumber || 0}-${fpIndex}`
      parts.push(
        <TerminalFileLink
          key={stableKey}
          path={filePath.path}
          teamId={selectedTeam || undefined}
          lineNumber={filePath.lineNumber}
          columnNumber={filePath.columnNumber}
        />
      )

      lastIndex = filePath.endIndex
    })

    // Add remaining text after last file path
    if (lastIndex < strippedLine.length) {
      const textAfter = strippedLine.substring(lastIndex)
      parts.push(
        <span key={`text-${lineIndex}-end`}>
          {textAfter}
        </span>
      )
    }

    // Wrap in appropriate container
    return (
      <span key={lineIndex}>
        {isUserRequest ? (
          <span className="bg-primary/10 block -mx-2 sm:-mx-4 px-2 sm:px-4">
            {parts}
          </span>
        ) : (
          <span>{parts}</span>
        )}
        {'\n'}
      </span>
    )
  }

  /**
   * Render output with ANSI color support and line highlighting
   * Highlights lines starting with ">" as user requests
   * Detects file paths and renders them as clickable TerminalFileLink components
   */
  const renderOutput = (output: string, highlightText?: string | null): ReactNode => {
    const lines = output.split('\n')

    return lines.map((line, lineIndex) => {
      // Skip rendering last newline if it's an empty line
      if (lineIndex === lines.length - 1 && line === '') {
        return null
      }

      return renderLineWithFilePaths(line, lineIndex, highlightText)
    })
  }

  return (
    <>
      {/* Tabs */}
      {selectedTeam && roles.length > 0 ? (
        <Tabs
          value={selectedRole || ""}
          onValueChange={onRoleChange}
          className="flex-1 flex flex-col overflow-hidden"
        >
          <div className="border-b border-border bg-muted/20 px-2 overflow-x-auto">
            <TabsList className="h-10 sm:h-11 bg-transparent gap-1 w-max sm:w-auto">
              {roles.map((role) => {
                const isActive = roleActivity[role.id] ?? false

                return (
                  <TabsTrigger
                    key={role.id}
                    value={role.id}
                    className="text-xs sm:text-sm px-2 sm:px-3 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm data-[state=active]:font-semibold data-[state=inactive]:text-muted-foreground data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-muted/50 transition-all whitespace-nowrap flex items-center gap-1.5"
                  >
                    {/* Activity indicator dot */}
                    <span
                      className={cn(
                        "h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full transition-all duration-300 flex-shrink-0",
                        isActive
                          ? "bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.6)] animate-pulse-gentle"
                          : "bg-gray-400"
                      )}
                      aria-hidden="true"
                    />
                    {role.name}
                  </TabsTrigger>
                )
              })}
            </TabsList>
          </div>

          {roles.map((role) => (
            <TabsContent
              key={role.id}
              value={role.id}
              className="flex-1 flex flex-col overflow-hidden m-0 data-[state=active]:flex data-[state=inactive]:hidden"
            >
              {/* Terminal Output */}
              <div className="flex-1 overflow-hidden flex flex-col bg-muted/30 relative">
                <div className="flex items-center justify-between px-2 sm:px-4 py-1.5 sm:py-2 border-b border-border bg-card/50">
                  <span className="text-[10px] sm:text-xs text-muted-foreground font-mono truncate">
                    {currentPaneState?.lastUpdated && `Updated: ${currentPaneState.lastUpdated}`}
                  </span>
                  <button
                    onClick={() => {
                      if (!isAutoScrollEnabled) {
                        onScrollToBottom()
                      }
                    }}
                    className={cn(
                      "text-[10px] sm:text-xs font-mono px-2 py-0.5 rounded-full transition-colors",
                      isAutoScrollEnabled
                        ? "bg-green-500/20 text-green-500"
                        : "bg-yellow-500/20 text-yellow-500 cursor-pointer hover:bg-yellow-500/30"
                    )}
                  >
                    Streaming: {isAutoScrollEnabled ? "ON" : "OFF"}
                  </button>
                </div>

                <div
                  ref={outputRef}
                  className="flex-1 overflow-y-auto p-2 sm:p-4 font-mono text-xs sm:text-sm leading-relaxed"
                  onScroll={onScroll}
                >
                  <pre
                    className="whitespace-pre font-mono text-foreground/90"
                    style={{
                      overflowX: 'auto',
                      wordBreak: 'normal',
                      overflowWrap: 'normal'
                    }}
                  >
                    {currentPaneState?.output
                      ? renderOutput(currentPaneState.output, currentPaneState.highlightText)
                      : "No output available. Send a message to get started."}
                  </pre>
                </div>

                {showScrollFab && (
                  <Button
                    onClick={onScrollToBottom}
                    size="icon"
                    className="absolute bottom-4 right-4 h-10 w-10 rounded-full shadow-lg bg-primary hover:bg-primary/90 z-10"
                    aria-label="Scroll to bottom"
                  >
                    <ArrowDown className="h-5 w-5" />
                  </Button>
                )}
              </div>

              {/* Input Area */}
              <div className="border-t border-border bg-card p-2 sm:p-4">
                <div className="relative">
                  <div className="flex gap-2 items-center">
                    {/* Mode Toggle Button */}
                    <Button
                      variant="ghost"
                      size="icon"
                      className={cn(
                        "h-10 w-10 shrink-0 transition-colors",
                        isTerminalMode
                          ? "text-green-500 hover:text-green-400 hover:bg-green-500/10"
                          : "text-muted-foreground hover:text-foreground"
                      )}
                      onClick={() => setIsTerminalMode(!isTerminalMode)}
                      title={isTerminalMode ? "Switch to Chat mode" : "Switch to Terminal mode"}
                      aria-label={isTerminalMode ? "Switch to Chat mode" : "Switch to Terminal mode"}
                    >
                      {isTerminalMode ? (
                        <Terminal className="h-4 w-4" />
                      ) : (
                        <MessageSquare className="h-4 w-4" />
                      )}
                    </Button>

                    <Input
                      ref={inputRef}
                      value={inputValue}
                      onChange={(e) => onInputChange(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder={isPending ? "Waiting..." : isTerminalMode ? "$ Enter command..." : "Type a message..."}
                      disabled={isPending}
                      className={cn(
                        "flex-1 font-mono text-sm h-10",
                        isTerminalMode && "bg-black/20 border-green-500/30 focus-visible:ring-green-500/50"
                      )}
                      style={{ fontSize: '16px' }}
                      autoComplete="off"
                    />
                    <Button
                      onClick={onSendEscape}
                      variant="ghost"
                      size="icon"
                      className="h-10 w-10 shrink-0 text-red-500 hover:text-red-400 hover:bg-red-500/10"
                      title="Stop (send Escape key)"
                      aria-label="Stop agent"
                    >
                      <Square className="h-4 w-4" />
                    </Button>
                    <Button onClick={onSendMessage} disabled={!inputValue.trim() || isPending} size="icon" className="h-10 w-10 shrink-0">
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Autocomplete Dropdown Component */}
                  {(showSuggestions || (isLoadingPaths && isPathInput && isTerminalMode)) && (
                    <AutocompleteDropdown
                      suggestions={filteredSuggestions}
                      selectedIndex={suggestionIndex}
                      onSelect={selectSuggestion}
                      onDismiss={() => setSuggestionsDismissed(true)}
                      onNavigate={setSuggestionIndex}
                      isLoading={isLoadingPaths && isPathInput && isTerminalMode}
                      isPathMode={isPathInput}
                    />
                  )}
                </div>
                <div className={cn(
                  "mt-2 p-2 bg-muted/50 rounded-md flex items-center gap-2 min-h-[2.5rem] transition-opacity",
                  voiceTranscript ? "opacity-100" : "opacity-0 pointer-events-none"
                )}>
                  <p className={cn(
                    "text-sm font-mono flex-1",
                    voiceStatus === "correcting" ? "text-yellow-500" :
                    voiceStatus === "sent" ? "text-green-500" :
                    voiceStatus === "listening" ? "text-blue-500" :
                    "text-foreground/80"
                  )}>
                    {voiceStatus === "listening" && "🎤 "}
                    {voiceStatus === "correcting" && "✏️ "}
                    {voiceStatus === "sent" && "✅ "}
                    {voiceTranscript}
                  </p>
                  {voiceTranscript && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6 text-muted-foreground hover:text-destructive shrink-0"
                      onClick={onClearTranscript}
                      title="Clear recording"
                      aria-label="Clear recording"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                {isPending && (
                  <p className="text-xs text-muted-foreground mt-2">
                    Message sent. Streaming updates...
                  </p>
                )}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      ) : (
        <div className="flex-1 flex items-center justify-center text-muted-foreground">
          {selectedTeam ? "Loading roles..." : "Select a team to get started"}
        </div>
      )}
    </>
  )
}
