"use client"

import { useState, useRef } from "react"
import { Node, Edge } from "@xyflow/react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Save,
  FolderOpen,
  Download,
  Upload,
  MoreHorizontal,
  Trash2,
  Check,
} from "lucide-react"
import { TemplateSelector } from "./TemplateSelector"
import { ModeToggle } from "./ModeToggle"
import { TeamSelector } from "./TeamSelector"
import { TeamTemplate } from "@/lib/team-creator/templates"
import {
  saveConfig,
  loadAllConfigs,
  deleteConfig,
  downloadAsJson,
  importFromJson,
  SavedTeamConfig,
} from "@/lib/team-creator/storage"
import { TeamCreatorMode, MonitorConnectionStatus } from "@/lib/team-creator/types"

interface TeamToolbarProps {
  nodes: Node[]
  edges: Edge[]
  onLoadTemplate: (template: TeamTemplate) => void
  onLoadConfig: (config: SavedTeamConfig) => void
  hasUnsavedChanges: boolean
  onChangesSaved: () => void
  // Sprint 32: Mode toggle props
  mode: TeamCreatorMode
  onModeChange: (mode: TeamCreatorMode) => void
  selectedTeam: string | null
  onSelectTeam: (team: string) => void
  connectionStatus: MonitorConnectionStatus
}

export function TeamToolbar({
  nodes,
  edges,
  onLoadTemplate,
  onLoadConfig,
  hasUnsavedChanges,
  onChangesSaved,
  mode,
  onModeChange,
  selectedTeam,
  onSelectTeam,
  connectionStatus,
}: TeamToolbarProps) {
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [showLoadDialog, setShowLoadDialog] = useState(false)
  const [configName, setConfigName] = useState("")
  const [configDescription, setConfigDescription] = useState("")
  const [savedConfigs, setSavedConfigs] = useState<SavedTeamConfig[]>([])
  const [saveSuccess, setSaveSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // ============================================
  // Save Handlers
  // ============================================

  const handleOpenSaveDialog = () => {
    setConfigName("")
    setConfigDescription("")
    setSaveSuccess(false)
    setShowSaveDialog(true)
  }

  const handleSave = () => {
    if (!configName.trim()) return

    const id = configName.toLowerCase().replace(/\s+/g, "-")
    const config = saveConfig({
      id,
      name: configName.trim(),
      description: configDescription.trim(),
      nodes,
      edges,
    })

    setSaveSuccess(true)
    onChangesSaved()

    // Close dialog after short delay to show success
    setTimeout(() => {
      setShowSaveDialog(false)
      setSaveSuccess(false)
    }, 1000)
  }

  // ============================================
  // Load Handlers
  // ============================================

  const handleOpenLoadDialog = () => {
    const configs = loadAllConfigs()
    setSavedConfigs(Object.values(configs))
    setShowLoadDialog(true)
  }

  const handleLoadConfig = (config: SavedTeamConfig) => {
    onLoadConfig(config)
    setShowLoadDialog(false)
  }

  const handleDeleteConfig = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    deleteConfig(id)
    setSavedConfigs((prev) => prev.filter((c) => c.id !== id))
  }

  // ============================================
  // Export/Import Handlers
  // ============================================

  const handleExport = () => {
    const config: SavedTeamConfig = {
      id: `export-${Date.now()}`,
      name: "Exported Team",
      description: "Exported from Team Creator",
      nodes,
      edges,
      version: 1,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    }
    downloadAsJson(config)
  }

  const handleImportClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      const config = importFromJson(text)
      onLoadConfig(config)
    } catch (error) {
      console.error("[TeamCreator] Failed to import:", error)
      alert("Failed to import file. Please check the format.")
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <div className="flex items-center gap-2 p-2 border-b border-border bg-background/95 backdrop-blur">
      {/* Mode Toggle */}
      <ModeToggle mode={mode} onModeChange={onModeChange} />

      <div className="w-px h-6 bg-border mx-2" />

      {/* Design Mode: Template Selector */}
      {mode === "design" && (
        <TemplateSelector
          onSelectTemplate={onLoadTemplate}
          hasUnsavedChanges={hasUnsavedChanges}
        />
      )}

      {/* Monitor Mode: Team Selector */}
      {mode === "monitor" && (
        <TeamSelector
          selectedTeam={selectedTeam}
          onSelectTeam={onSelectTeam}
          connectionStatus={connectionStatus}
        />
      )}

      <div className="w-px h-6 bg-border mx-2" />

      {/* Save Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={handleOpenSaveDialog}
        className="gap-2"
      >
        <Save className="h-4 w-4" />
        Save
      </Button>

      {/* Load Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={handleOpenLoadDialog}
        className="gap-2"
      >
        <FolderOpen className="h-4 w-4" />
        Load
      </Button>

      {/* More Actions Menu */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export as JSON
          </DropdownMenuItem>
          <DropdownMenuItem onClick={handleImportClick}>
            <Upload className="h-4 w-4 mr-2" />
            Import from JSON
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Hidden file input for import */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Unsaved changes indicator */}
      {hasUnsavedChanges && (
        <span className="text-xs text-amber-500 ml-2">Unsaved changes</span>
      )}

      {/* Save Dialog */}
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save Team Configuration</DialogTitle>
            <DialogDescription>
              Save your current team layout for later use.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={configName}
                onChange={(e) => setConfigName(e.target.value)}
                placeholder="My Team"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Input
                id="description"
                value={configDescription}
                onChange={(e) => setConfigDescription(e.target.value)}
                placeholder="Description of this team configuration"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={!configName.trim() || saveSuccess}>
              {saveSuccess ? (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Saved!
                </>
              ) : (
                "Save"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Load Dialog */}
      <Dialog open={showLoadDialog} onOpenChange={setShowLoadDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Load Saved Configuration</DialogTitle>
            <DialogDescription>
              Select a previously saved team configuration to load.
            </DialogDescription>
          </DialogHeader>
          <div className="max-h-[300px] overflow-y-auto">
            {savedConfigs.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No saved configurations yet.
              </div>
            ) : (
              <div className="space-y-2">
                {savedConfigs.map((config) => (
                  <div
                    key={config.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent cursor-pointer"
                    onClick={() => handleLoadConfig(config)}
                  >
                    <div>
                      <div className="font-medium">{config.name}</div>
                      {config.description && (
                        <div className="text-xs text-muted-foreground">
                          {config.description}
                        </div>
                      )}
                      <div className="text-xs text-muted-foreground">
                        {config.nodes.length} nodes, {config.edges.length} edges
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => handleDeleteConfig(config.id, e)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLoadDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
