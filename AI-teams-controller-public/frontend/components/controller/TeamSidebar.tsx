"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
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
import { Settings, ChevronLeft, Skull, Loader2, RefreshCw, Terminal, ChevronRight, ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { HeadphoneButton } from "./HeadphoneButton"
import { DirectoryPicker } from "./DirectoryPicker"
import { TeamList } from "./TeamList"
import { TeamSettingsPanel } from "./TeamSettingsPanel"
import type { PollingInterval as TeamSettingsPollingInterval } from "./TeamSettingsPanel"

/**
 * Team type for sidebar display
 */
type Team = {
  id: string
  name: string
}

/**
 * Polling interval options in seconds (re-export from TeamSettingsPanel)
 */
type PollingInterval = TeamSettingsPollingInterval

/**
 * Restart progress steps for team restart operation
 */
export type RestartProgress =
  | "idle"
  | "killing"
  | "looking_for_script"
  | "running_script"
  | "complete"
  | "no_script"

/**
 * Props for TeamSidebar component
 */
export interface TeamSidebarProps {
  /** List of available teams */
  teams: Team[]
  /** Currently selected team ID */
  selectedTeam: string | null
  /** Whether sidebar is open (mobile) */
  sidebarOpen: boolean
  /** Whether device is mobile */
  isMobile: boolean
  /** Whether settings panel is visible */
  showSettings: boolean
  /** Current polling interval */
  pollingInterval: PollingInterval
  /** Number of lines to capture */
  captureLines: number
  /** Voice stop word */
  stopWord: string
  /** Callback when team is selected */
  onSelectTeam: (teamId: string) => void
  /** Callback to toggle sidebar */
  onToggleSidebar: (open: boolean) => void
  /** Callback to toggle settings */
  onToggleSettings: () => void
  /** Callback when polling interval changes */
  onPollingIntervalChange: (interval: PollingInterval) => void
  /** Callback when capture lines changes */
  onCaptureLinesChange: (lines: number) => void
  /** Callback when stop word changes */
  onStopWordChange: (word: string) => void
  /** Callback to kill team */
  onKillTeam?: (teamId: string) => Promise<void>
  /** Whether kill operation is in progress */
  isKillingTeam?: boolean
  /** Callback to restart team */
  onRestartTeam?: (teamId: string) => Promise<void>
  /** Current restart progress */
  restartProgress?: RestartProgress
  /** Callback to create terminal */
  onCreateTerminal?: (name?: string, directory?: string) => Promise<void>
  /** Whether terminal creation is in progress */
  isCreatingTerminal?: boolean
  /** Current recording state for HeadphoneButton sync */
  isRecording?: boolean
  /** Callback when headphone button triggers voice toggle (from physical button) */
  onHeadphoneToggle?: (isActive: boolean) => void
  /** Set of team IDs with unread notifications */
  teamNotifications?: Set<string>
}

/**
 * TeamSidebar Component
 *
 * Sidebar for team management with:
 * - Team list with selection and activity indicators
 * - New Terminal button
 * - Kill Team action
 * - Settings panel (polling, lines, stop word, voice speed)
 * - Mobile-responsive with slide-out drawer
 */
export function TeamSidebar({
  teams,
  selectedTeam,
  sidebarOpen,
  isMobile,
  showSettings,
  pollingInterval,
  captureLines,
  stopWord,
  onSelectTeam,
  onToggleSidebar,
  onToggleSettings,
  onPollingIntervalChange,
  onCaptureLinesChange,
  onStopWordChange,
  onKillTeam,
  isKillingTeam,
  onRestartTeam,
  restartProgress = "idle",
  onCreateTerminal,
  isCreatingTerminal,
  isRecording,
  onHeadphoneToggle,
  teamNotifications = new Set(),
}: TeamSidebarProps) {
  const [killDialogOpen, setKillDialogOpen] = useState(false)
  const [restartDialogOpen, setRestartDialogOpen] = useState(false)
  const [terminalDialogOpen, setTerminalDialogOpen] = useState(false)
  const [terminalName, setTerminalName] = useState("")
  const [terminalNameError, setTerminalNameError] = useState("")
  const [selectedDirectory, setSelectedDirectory] = useState<string | null>(null)
  const [directoryPickerExpanded, setDirectoryPickerExpanded] = useState(false)
  const [showHiddenDirs, setShowHiddenDirs] = useState(false)

  const selectedTeamData = teams.find((t) => t.id === selectedTeam)
  const isRestarting = restartProgress !== "idle"

  /**
   * Validate terminal name (alphanumeric, hyphens, underscores only)
   */
  const validateTerminalName = (name: string): boolean => {
    if (!name) return true // Empty is valid (will be auto-generated)
    const validPattern = /^[a-zA-Z0-9_-]+$/
    return validPattern.test(name)
  }

  const handleTerminalNameChange = (value: string) => {
    setTerminalName(value)
    if (value && !validateTerminalName(value)) {
      setTerminalNameError("Only letters, numbers, hyphens, and underscores allowed")
    } else {
      setTerminalNameError("")
    }
  }

  const handleCreateTerminal = async () => {
    if (terminalNameError) return
    if (!onCreateTerminal) return
    await onCreateTerminal(terminalName || undefined, selectedDirectory || undefined)
    setTerminalDialogOpen(false)
    setTerminalName("")
    setTerminalNameError("")
    setSelectedDirectory(null)
    setDirectoryPickerExpanded(false)
    setShowHiddenDirs(false)
  }

  const handleKillConfirm = async () => {
    if (!selectedTeam || !onKillTeam) return
    await onKillTeam(selectedTeam)
    setKillDialogOpen(false)
  }

  const handleRestartConfirm = async () => {
    if (!selectedTeam || !onRestartTeam) return
    await onRestartTeam(selectedTeam)
    setRestartDialogOpen(false)
  }

  /**
   * Get progress message for restart dialog
   */
  const getRestartProgressMessage = () => {
    switch (restartProgress) {
      case "killing":
        return "Killing session..."
      case "looking_for_script":
        return "Looking for setup script..."
      case "running_script":
        return "Running setup script..."
      case "complete":
        return "Complete!"
      case "no_script":
        return "No setup script found"
      default:
        return null
    }
  }

  return (
    <div
      className={cn(
        "w-56 sm:w-64 border-r border-border bg-sidebar flex flex-col transition-transform duration-200",
        isMobile && !sidebarOpen && "-translate-x-full absolute z-10 h-full",
        isMobile && sidebarOpen && "absolute z-10 h-full shadow-lg",
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h1 className="text-lg font-semibold text-sidebar-foreground">TMUX Controller</h1>
          {/* Global HeadphoneButton - hardware headphone mode setting */}
          <HeadphoneButton
            isRecording={isRecording}
            onToggle={onHeadphoneToggle}
          />
        </div>
        {isMobile && (
          <Button variant="ghost" size="icon" onClick={() => onToggleSidebar(false)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Team List - ISP-compliant focused component */}
      <div className="flex-1 overflow-y-auto p-2">
        <TeamList
          teams={teams}
          selectedTeam={selectedTeam}
          onSelectTeam={(teamId) => {
            onSelectTeam(teamId)
            if (isMobile) onToggleSidebar(false)
          }}
          teamNotifications={teamNotifications}
        />
      </div>

      {/* New Terminal Button - always visible */}
      {onCreateTerminal && (
        <div className="p-2 border-t border-border">
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => setTerminalDialogOpen(true)}
            disabled={isCreatingTerminal}
          >
            {isCreatingTerminal ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Terminal className="h-4 w-4 mr-2" />
                New Terminal
              </>
            )}
          </Button>
        </div>
      )}

      {/* Restart Team Button - only visible when team selected */}
      {selectedTeam && onRestartTeam && (
        <div className="p-2 border-t border-border">
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => setRestartDialogOpen(true)}
            disabled={isKillingTeam || isRestarting}
          >
            {isRestarting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Restarting...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Restart Team
              </>
            )}
          </Button>
        </div>
      )}

      {/* Team Actions - only visible when team selected */}
      {selectedTeam && onKillTeam && (
        <div className="p-2 border-t border-border">
          <Button
            variant="destructive"
            size="sm"
            className="w-full"
            onClick={() => setKillDialogOpen(true)}
            disabled={isKillingTeam || isRestarting}
          >
            {isKillingTeam ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Killing...
              </>
            ) : (
              <>
                <Skull className="h-4 w-4 mr-2" />
                Kill Team
              </>
            )}
          </Button>
        </div>
      )}

      {/* Settings Footer */}
      <div className="p-2 border-t border-border">
        <Button
          variant="outline"
          size="sm"
          className="w-full bg-transparent"
          onClick={onToggleSettings}
        >
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>

        {showSettings && (
          <Card className="mt-2 p-3">
            {/* Settings Panel - ISP-compliant focused component */}
            <TeamSettingsPanel
              pollingInterval={pollingInterval}
              captureLines={captureLines}
              stopWord={stopWord}
              onPollingIntervalChange={onPollingIntervalChange}
              onCaptureLinesChange={onCaptureLinesChange}
              onStopWordChange={onStopWordChange}
            />
          </Card>
        )}
      </div>

      {/* Kill Confirmation Dialog */}
      <AlertDialog open={killDialogOpen} onOpenChange={setKillDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Kill Team?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure? This will terminate all agents in{" "}
              <span className="font-semibold">{selectedTeamData?.name || selectedTeam}</span>.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isKillingTeam}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleKillConfirm}
              disabled={isKillingTeam}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isKillingTeam ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Killing...
                </>
              ) : (
                "Kill Team"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Restart Confirmation Dialog */}
      <AlertDialog open={restartDialogOpen} onOpenChange={(open) => !isRestarting && setRestartDialogOpen(open)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Restart Team?</AlertDialogTitle>
            <AlertDialogDescription className="space-y-2">
              <span>
                This will kill{" "}
                <span className="font-semibold">{selectedTeamData?.name || selectedTeam}</span>{" "}
                and run setup-team.sh. Continue?
              </span>
              <span className="block text-destructive font-medium">
                Any unsaved work will be lost.
              </span>
              {/* Progress display */}
              {isRestarting && (
                <span className="block mt-3 flex items-center gap-2 text-primary">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  {getRestartProgressMessage()}
                </span>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isRestarting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleRestartConfirm}
              disabled={isRestarting}
            >
              {isRestarting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Restarting...
                </>
              ) : (
                "Restart Team"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* New Terminal Dialog */}
      <Dialog open={terminalDialogOpen} onOpenChange={(open) => {
        if (!isCreatingTerminal) {
          setTerminalDialogOpen(open)
          if (!open) {
            setTerminalName("")
            setTerminalNameError("")
            setSelectedDirectory(null)
            setDirectoryPickerExpanded(false)
            setShowHiddenDirs(false)
          }
        }
      }}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Create New Terminal</DialogTitle>
            <DialogDescription>
              Enter a name and select a starting directory.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {/* Terminal Name Input */}
            <div>
              <label className="text-sm font-medium mb-1 block">Terminal Name (optional)</label>
              <Input
                placeholder="terminal-name"
                value={terminalName}
                onChange={(e) => handleTerminalNameChange(e.target.value)}
                disabled={isCreatingTerminal}
                className={terminalNameError ? "border-destructive" : ""}
              />
              {terminalNameError && (
                <p className="text-xs text-destructive mt-1">{terminalNameError}</p>
              )}
              <p className="text-xs text-muted-foreground mt-1">
                Leave empty to auto-generate: terminal-HHMMSS
              </p>
            </div>

            {/* Directory Picker - Collapsible */}
            <div>
              <button
                type="button"
                className="flex items-center gap-2 text-sm font-medium mb-1 w-full text-left hover:text-primary transition-colors"
                onClick={() => setDirectoryPickerExpanded(!directoryPickerExpanded)}
              >
                {directoryPickerExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
                Starting Directory (optional)
              </button>
              {selectedDirectory && (
                <p className="text-xs font-mono text-muted-foreground mb-2 truncate ml-6">
                  Selected: {selectedDirectory}
                </p>
              )}
              {directoryPickerExpanded && (
                <div className="ml-6">
                  {/* Show Hidden Toggle */}
                  <label className="flex items-center gap-2 text-xs text-muted-foreground mb-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showHiddenDirs}
                      onChange={(e) => setShowHiddenDirs(e.target.checked)}
                      className="rounded border-gray-300"
                    />
                    Show hidden folders
                  </label>
                  <div className="border rounded-md h-[200px] overflow-hidden">
                    <DirectoryPicker
                      embedded
                      showHidden={showHiddenDirs}
                      onSelect={(path) => setSelectedDirectory(path)}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setTerminalDialogOpen(false)
                setTerminalName("")
                setTerminalNameError("")
                setSelectedDirectory(null)
                setDirectoryPickerExpanded(false)
                setShowHiddenDirs(false)
              }}
              disabled={isCreatingTerminal}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateTerminal}
              disabled={isCreatingTerminal || !!terminalNameError}
            >
              {isCreatingTerminal ? (
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
