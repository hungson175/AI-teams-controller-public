"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import dynamic from "next/dynamic"
import { Button } from "@/components/ui/button"
import { Menu, Wifi, WifiOff } from "lucide-react"
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder"
import { useVoiceFeedback } from "@/contexts/VoiceFeedbackContext"
import { useTeamState } from "@/hooks/useTeamState"
import { usePanePolling } from "@/hooks/usePanePolling"
import { useTeamLifecycle } from "@/hooks/useTeamLifecycle"
import { useScrollManager } from "@/hooks/useScrollManager"
import { useAudioFeedback } from "@/hooks/useAudioFeedback"
import { cn } from "@/lib/utils"
import { useIsMobile } from "@/hooks/use-mobile"
import {
  getStopWord,
  setStopWordSetting,
  DEFAULT_STOP_WORD,
} from "@/lib/voice-types"
import { getWebSocketBaseUrl } from "@/lib/websocket-utils"
import { getAuthHeaders } from "@/lib/auth-utils"
import { tryRefreshTokens, getToken } from "@/lib/auth"
import { toast } from "@/hooks/use-toast"
import { TerminalPanel } from "./TerminalPanel"
import { VoiceOverlay } from "./VoiceOverlay"
import { TeamSidebar, type RestartProgress } from "./TeamSidebar"
import { FileBrowser } from "@/components/file-browser"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Monitor, FolderOpen, Terminal as TerminalIcon } from "lucide-react"
import type { ViewMode } from "@/components/file-browser"

// Dynamic import for InteractiveTerminal to avoid SSR issues with xterm.js
const InteractiveTerminal = dynamic(
  () => import("@/components/terminal/InteractiveTerminal").then(mod => ({ default: mod.InteractiveTerminal })),
  { ssr: false }
)

type Team = {
  id: string
  name: string
  isActive?: boolean
}

type Role = {
  id: string
  name: string
  order: number
  isActive?: boolean
}

type PaneState = {
  output: string
  lastUpdated: string
  highlightText?: string | null
  isActive?: boolean
}

type PollingInterval = 0.5 | 1 | 2

export function TmuxController() {
  // Team and Role State Management (extracted to useTeamState hook)
  const {
    teams,
    selectedTeam,
    roles,
    selectedRole,
    teamNotifications,
    roleActivity,
    prevTeamActivityRef,
    setTeams,
    setSelectedTeam,
    setRoles,
    setSelectedRole,
    setTeamNotifications,
    setRoleActivity,
    fetchTeams,
    fetchRoles,
    handleSelectTeam,
  } = useTeamState()

  const [inputValue, setInputValue] = useState("")
  const [isPending, setIsPending] = useState(false)
  const [pollingInterval, setPollingInterval] = useState<PollingInterval>(0.5)
  const [captureLines, setCaptureLines] = useState<number>(100)
  const [showSettings, setShowSettings] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [voiceTranscript, setVoiceTranscript] = useState("")
  const [voiceStatus, setVoiceStatus] = useState("")
  const outputRef = useRef<HTMLDivElement>(null)
  const isMobile = useIsMobile()
  const [stopWord, setStopWordState] = useState<string>(DEFAULT_STOP_WORD)
  const [viewMode, setViewMode] = useState<ViewMode>("monitor")
  const { unreadCount, togglePanel, isConnected: isFeedbackConnected, setHandsFreeMode } = useVoiceFeedback()
  const { clearTranscript, startRecording, stopRecording, isRecording, state: voiceState, canRecord } = useVoiceRecorder()

  // Scroll Management (extracted to useScrollManager hook - Sprint 3)
  const {
    isAutoScrollEnabled,
    showScrollFab,
    isAutoScrollEnabledRef,
    handleScroll,
    scrollToBottom,
  } = useScrollManager({
    outputRef,
    selectedRole,
  })

  // P0 FIX: Memoize callback to prevent WebSocket reconnection loop
  // Root cause: Inline callback creates new function every render → effect re-runs → WS reconnects
  const handleRoleActivityUpdate = useCallback((roleId: string, isActive: boolean) => {
    setRoleActivity((prev) => {
      // Skip update if value unchanged (prevents re-render every 5s)
      if (prev[roleId] === isActive) return prev
      return {
        ...prev,
        [roleId]: isActive,
      }
    })
  }, [])

  // Pane Polling and WebSocket Management (extracted to usePanePolling hook)
  const { paneStates, wsConnected, setPaneStates, wsRef } = usePanePolling({
    selectedTeam,
    selectedRole,
    pollingInterval,
    captureLines,
    outputRef,
    isAutoScrollEnabledRef,
    onRoleActivityUpdate: handleRoleActivityUpdate,
  })

  // Team Lifecycle Management (extracted to useTeamLifecycle hook)
  const {
    isKillingTeam,
    restartProgress,
    isCreatingTerminal,
    restartingRoles,
    handleKillTeam,
    handleRestartTeam,
    handleRestartRole,
    handleCreateTerminal,
    handleCreateTeam,
    handleLoadTeam,
  } = useTeamLifecycle({
    teams,
    selectedTeam,
    onTeamListRefresh: fetchTeams,
    onTeamSelect: setSelectedTeam,
    onRoleSelect: setSelectedRole,
    onRolesUpdate: setRoles,
  })

  // Audio Feedback (extracted to useAudioFeedback hook - Sprint 3)
  const { playBeep } = useAudioFeedback()

  useEffect(() => {
    setStopWordState(getStopWord())
  }, [])

  // Centralized hands-free mode sync (moved from VoiceInputToggle for single source of truth)
  useEffect(() => {
    setHandsFreeMode(isRecording)
  }, [isRecording, setHandsFreeMode])

  const handleStopWordChange = (value: string) => {
    setStopWordState(value)
    setStopWordSetting(value)
  }

  const handleVoiceTranscriptChange = useCallback((transcript: string, status: string) => {
    setVoiceTranscript(transcript)
    setVoiceStatus(status)
  }, [])

  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false)
    }
  }, [isMobile])

  useEffect(() => {
    fetchTeams()
  }, [])


  useEffect(() => {
    if (selectedTeam) {
      fetchRoles(selectedTeam)
    }
  }, [selectedTeam])

  // Scroll to highlighted message when pane content updates
  useEffect(() => {
    if (outputRef.current && isAutoScrollEnabled) {
      const highlightedElement = outputRef.current.querySelector(".highlight-message")
      if (highlightedElement) {
        highlightedElement.scrollIntoView({ behavior: "smooth", block: "center" })
      } else {
        outputRef.current.scrollTop = outputRef.current.scrollHeight
      }
    }
  }, [paneStates, selectedRole, isAutoScrollEnabled])

  // fetchTeams and fetchRoles moved to useTeamState hook
  // Scroll management moved to useScrollManager hook (Sprint 3)

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !selectedTeam || !selectedRole || isPending) return

    setIsPending(true)

    try {
      const response = await fetch(`/api/send/${selectedTeam}/${selectedRole}`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ message: inputValue }),
      })

      if (!response.ok) {
        console.error("[TmuxController] sendMessage error:", response.status)
        setIsPending(false)
        return
      }

      setInputValue("")
      setTimeout(() => {
        setIsPending(false)
      }, 1000)
    } catch (error) {
      console.error("[v0] Error sending message:", error)
      setIsPending(false)
    }
  }

  const handleSendEscape = async () => {
    if (!selectedTeam || !selectedRole) return

    try {
      const response = await fetch(`/api/send/${selectedTeam}/${selectedRole}`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ message: "\x1b" }),
      })

      if (!response.ok) {
        console.error("[TmuxController] sendEscape error:", response.status)
      }
    } catch (error) {
      console.error("[TmuxController] Error sending escape:", error)
    }
  }

  const handleRoleChange = (roleId: string) => {
    setSelectedRole(roleId)
  }

  // handleSelectTeam moved to useTeamState hook


  const handleClearTranscript = useCallback(() => {
    clearTranscript()
    setVoiceTranscript("")
  }, [clearTranscript])

  // Work Item 2 Fix: Memoize onHeadphoneToggle to prevent TeamSidebar re-renders
  const handleHeadphoneToggle = useCallback(async (isActive: boolean) => {
    // Play audio feedback: High beep (880Hz) = ON, Low beep (440Hz) = OFF
    playBeep(isActive)

    // Start/stop actual voice recording
    if (isActive) {
      if (selectedTeam && selectedRole) {
        await startRecording(selectedTeam, selectedRole)
      } else {
        console.warn("[TmuxController] Cannot start recording - no team/role selected")
      }
    } else {
      stopRecording()
    }
  }, [playBeep, selectedTeam, selectedRole, startRecording, stopRecording])

  const currentPaneState = selectedTeam && selectedRole ? paneStates[`${selectedTeam}-${selectedRole}`] : null

  return (
    <div className="flex h-full bg-background text-foreground overflow-hidden">
      {/* Team Sidebar (Wave 3 Phase 3) */}
      <TeamSidebar
        teams={teams}
        selectedTeam={selectedTeam}
        sidebarOpen={sidebarOpen}
        isMobile={isMobile}
        showSettings={showSettings}
        pollingInterval={pollingInterval}
        captureLines={captureLines}
        stopWord={stopWord}
        onSelectTeam={handleSelectTeam}
        onToggleSidebar={setSidebarOpen}
        onToggleSettings={() => setShowSettings(!showSettings)}
        onPollingIntervalChange={setPollingInterval}
        onCaptureLinesChange={setCaptureLines}
        onStopWordChange={handleStopWordChange}
        onKillTeam={handleKillTeam}
        isKillingTeam={isKillingTeam}
        onRestartTeam={handleRestartTeam}
        restartProgress={restartProgress}
        onCreateTerminal={handleCreateTerminal}
        isCreatingTerminal={isCreatingTerminal}
        onCreateTeam={handleCreateTeam}
        onLoadTeam={handleLoadTeam}
        isRecording={isRecording}
        teamNotifications={teamNotifications}
        onHeadphoneToggle={handleHeadphoneToggle}
      />

      {/* Main Content - Role Tabs */}
      <div className="flex-1 flex flex-col overflow-hidden min-h-0">
        {/* Header */}
        <div className="h-12 sm:h-14 border-b border-border flex items-center justify-between px-2 sm:px-4 bg-card">
          <div className="flex items-center gap-2 min-w-0">
            {isMobile && !sidebarOpen && (
              <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(true)} className="mr-1 h-8 w-8 shrink-0">
                <Menu className="h-4 w-4" />
              </Button>
            )}
            {wsConnected ? (
              <Wifi
                className="h-3 w-3 sm:h-4 sm:w-4 text-green-500 shrink-0"
                data-testid="wifi-icon"
                data-connection-state="connected"
              />
            ) : (
              <WifiOff
                className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground shrink-0"
                data-testid="wifi-icon"
                data-connection-state="disconnected"
              />
            )}
            <span className="text-xs sm:text-sm font-medium font-mono truncate">
              {teams.find((t) => t.id === selectedTeam)?.name || "No Team"}
            </span>
            {wsConnected && (
              <span className="text-xs text-muted-foreground shrink-0">({pollingInterval}s)</span>
            )}
          </div>

          {/* Voice Overlay (Wave 3 Phase 2) */}
          <VoiceOverlay
            unreadCount={unreadCount}
            isFeedbackConnected={isFeedbackConnected}
            selectedTeam={selectedTeam}
            selectedRole={selectedRole}
            onTogglePanel={togglePanel}
            onTranscriptChange={handleVoiceTranscriptChange}
            voiceState={voiceState}
            isRecording={isRecording}
            startRecording={startRecording}
            stopRecording={stopRecording}
            canRecord={canRecord}
          />
        </div>

        {/* View Mode Tabs */}
        <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as ViewMode)} className="flex-1 flex flex-col overflow-hidden min-h-0">
          <div className="border-b bg-muted/30 px-2">
            <TabsList className="h-9 bg-transparent">
              <TabsTrigger value="monitor" className="gap-1.5 text-xs data-[state=active]:bg-background">
                <Monitor className="h-3.5 w-3.5" />
                Monitor
              </TabsTrigger>
              <TabsTrigger value="browse" className="gap-1.5 text-xs data-[state=active]:bg-background">
                <FolderOpen className="h-3.5 w-3.5" />
                Browse
              </TabsTrigger>
              <TabsTrigger value="terminal" className="gap-1.5 text-xs data-[state=active]:bg-background">
                <TerminalIcon className="h-3.5 w-3.5" />
                Terminal
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Monitor Tab - Terminal Panel */}
          <TabsContent value="monitor" className="flex-1 mt-0 flex flex-col min-h-0">
            <TerminalPanel
              roles={roles}
              selectedRole={selectedRole}
              roleActivity={roleActivity}
              currentPaneState={currentPaneState}
              inputValue={inputValue}
              isPending={isPending}
              isAutoScrollEnabled={isAutoScrollEnabled}
              showScrollFab={showScrollFab}
              voiceTranscript={voiceTranscript}
              voiceStatus={voiceStatus}
              selectedTeam={selectedTeam}
              onRoleChange={handleRoleChange}
              onInputChange={setInputValue}
              onSendMessage={handleSendMessage}
              onSendEscape={handleSendEscape}
              onScrollToBottom={scrollToBottom}
              onClearTranscript={handleClearTranscript}
              onScroll={handleScroll}
              outputRef={outputRef}
              onRestartRole={handleRestartRole}
              restartingRoles={restartingRoles}
            />
          </TabsContent>

          {/* Browse Tab - File Browser */}
          <TabsContent value="browse" className="flex-1 mt-0 overflow-hidden min-h-0 h-full">
            {selectedTeam ? (
              <FileBrowser teamId={selectedTeam} />
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <p className="text-sm">Select a team to browse files</p>
              </div>
            )}
          </TabsContent>

          {/* Terminal Tab - Interactive Shell */}
          <TabsContent value="terminal" className="flex-1 mt-0 flex flex-col min-h-0">
            <InteractiveTerminal
              token={getToken()}
              isVisible={viewMode === "terminal"}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
