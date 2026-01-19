"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { Node, Edge, useNodesState, useEdgesState } from "@xyflow/react"
import { TeamFlowCanvas } from "./TeamFlowCanvas"
import { WorkflowMatrix } from "./WorkflowMatrix"
import { TeamToolbar } from "./controls/TeamToolbar"
import { LayoutGrid, Network } from "lucide-react"
import { TeamTemplate, TEMPLATES } from "@/lib/team-creator/templates"
import { SavedTeamConfig, loadCurrentConfig, saveCurrentConfig } from "@/lib/team-creator/storage"
import { TeamCreatorMode } from "@/lib/team-creator/types"
import { useTeamStatus } from "@/hooks/useTeamStatus"

type ViewMode = "workflow" | "canvas"

// Default to full-stack template
const defaultTemplate = TEMPLATES["full-stack"]

export function TeamCreatorPanel() {
  const [viewMode, setViewMode] = useState<ViewMode>("canvas")
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultTemplate.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultTemplate.edges)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // Sprint 32: Design/Monitor mode toggle
  const [mode, setMode] = useState<TeamCreatorMode>("design")
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)

  // Extract role IDs from nodes for WebSocket connections
  const roleIds = useMemo(() => {
    return nodes.map((node) => node.id)
  }, [nodes])

  // WebSocket status hook - only active in Monitor mode with selected team
  const { statusMap, connectionStatus } = useTeamStatus({
    team: selectedTeam,
    roles: roleIds,
    enabled: mode === "monitor" && !!selectedTeam,
  })

  // Load saved config on mount
  useEffect(() => {
    const saved = loadCurrentConfig()
    if (saved) {
      setNodes(saved.nodes)
      setEdges(saved.edges)
    }
  }, [setNodes, setEdges])

  // Track changes
  const handleNodesChange: typeof onNodesChange = useCallback((changes) => {
    onNodesChange(changes)
    setHasUnsavedChanges(true)
  }, [onNodesChange])

  const handleEdgesChange: typeof onEdgesChange = useCallback((changes) => {
    onEdgesChange(changes)
    setHasUnsavedChanges(true)
  }, [onEdgesChange])

  // Load template
  const handleLoadTemplate = useCallback((template: TeamTemplate) => {
    setNodes(template.nodes)
    setEdges(template.edges)
    setHasUnsavedChanges(true)
  }, [setNodes, setEdges])

  // Load saved config
  const handleLoadConfig = useCallback((config: SavedTeamConfig) => {
    setNodes(config.nodes)
    setEdges(config.edges)
    setHasUnsavedChanges(false)
  }, [setNodes, setEdges])

  // Mark as saved
  const handleChangesSaved = useCallback(() => {
    setHasUnsavedChanges(false)
    // Save to current config for persistence
    saveCurrentConfig(nodes, edges)
  }, [nodes, edges])

  return (
    <div className="flex h-full bg-background">
      {/* Left Sidebar - Role Palette (placeholder for Sprint 2) */}
      <div className="w-56 border-r border-border bg-sidebar p-4 hidden md:block">
        <h2 className="text-sm font-semibold mb-4 text-sidebar-foreground">Role Palette</h2>
        <p className="text-xs text-muted-foreground">
          Drag roles onto the canvas to build your team.
        </p>
        <div className="mt-4 space-y-2">
          <div className="p-3 rounded-lg bg-amber-500/20 border border-amber-500/30 cursor-not-allowed opacity-60">
            <span className="text-sm font-medium text-amber-400">Boss</span>
            <p className="text-xs text-muted-foreground">Project Owner</p>
          </div>
          <div className="p-3 rounded-lg bg-purple-500/20 border border-purple-500/30 cursor-not-allowed opacity-60">
            <span className="text-sm font-medium text-purple-400">PM</span>
            <p className="text-xs text-muted-foreground">Project Manager</p>
          </div>
          <div className="p-3 rounded-lg bg-blue-500/20 border border-blue-500/30 cursor-not-allowed opacity-60">
            <span className="text-sm font-medium text-blue-400">SA</span>
            <p className="text-xs text-muted-foreground">Solution Architect</p>
          </div>
          <div className="p-3 rounded-lg bg-orange-500/20 border border-orange-500/30 cursor-not-allowed opacity-60">
            <span className="text-sm font-medium text-orange-400">BE</span>
            <p className="text-xs text-muted-foreground">Backend Engineer</p>
          </div>
          <div className="p-3 rounded-lg bg-green-500/20 border border-green-500/30 cursor-not-allowed opacity-60">
            <span className="text-sm font-medium text-green-400">FE</span>
            <p className="text-xs text-muted-foreground">Frontend Engineer</p>
          </div>
          <div className="p-3 rounded-lg bg-red-500/20 border border-red-500/30 cursor-not-allowed opacity-60">
            <span className="text-sm font-medium text-red-400">CR</span>
            <p className="text-xs text-muted-foreground">Code Reviewer</p>
          </div>
          <div className="p-3 rounded-lg bg-gray-500/20 border border-gray-500/30 cursor-not-allowed opacity-60">
            <span className="text-sm font-medium text-gray-400">DK</span>
            <p className="text-xs text-muted-foreground">Document Keeper</p>
          </div>
        </div>
        <p className="mt-4 text-[10px] text-muted-foreground italic">
          * Drag-drop coming in Sprint 2
        </p>
      </div>

      {/* Main Canvas */}
      <div className="flex-1 flex flex-col">
        {/* View Mode Toggle */}
        <div className="h-10 border-b border-border bg-card flex items-center px-4">
          <span className="text-sm font-medium mr-4">Team Creator</span>
          <div className="flex items-center bg-muted rounded-md p-0.5">
            <button
              onClick={() => setViewMode("workflow")}
              className={`flex items-center gap-1.5 px-2.5 py-1 text-xs rounded transition-colors ${
                viewMode === "workflow"
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <LayoutGrid className="h-3.5 w-3.5" />
              <span>Workflow</span>
            </button>
            <button
              onClick={() => setViewMode("canvas")}
              className={`flex items-center gap-1.5 px-2.5 py-1 text-xs rounded transition-colors ${
                viewMode === "canvas"
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Network className="h-3.5 w-3.5" />
              <span>Canvas</span>
            </button>
          </div>
        </div>

        {/* TeamToolbar - Templates, Save, Load, Export, Mode Toggle */}
        {viewMode === "canvas" && (
          <TeamToolbar
            nodes={nodes}
            edges={edges}
            onLoadTemplate={handleLoadTemplate}
            onLoadConfig={handleLoadConfig}
            hasUnsavedChanges={hasUnsavedChanges}
            onChangesSaved={handleChangesSaved}
            mode={mode}
            onModeChange={setMode}
            selectedTeam={selectedTeam}
            onSelectTeam={setSelectedTeam}
            connectionStatus={connectionStatus}
          />
        )}

        {/* Content Area */}
        <div className="flex-1 relative">
          {viewMode === "workflow" ? (
            <WorkflowMatrix />
          ) : (
            <TeamFlowCanvas
              nodes={nodes}
              edges={edges}
              onNodesChange={handleNodesChange}
              onEdgesChange={handleEdgesChange}
              setEdges={setEdges}
              mode={mode}
              statusMap={statusMap}
            />
          )}
        </div>
      </div>
    </div>
  )
}
