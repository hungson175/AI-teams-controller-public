"use client"

import { useState, useCallback, useEffect } from "react"
import { FolderTree, FileText, Search } from "lucide-react"
import { FileTree } from "./FileTree"
import { FileViewer } from "./FileViewer"
import { FileSearch } from "./FileSearch"
import { useIsDesktop } from "@/hooks/use-desktop"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

interface FileBrowserProps {
  /** Team ID for API calls */
  teamId: string
}

/**
 * FileBrowser Component
 *
 * Main container for the file browser feature.
 * - Desktop (1024px+): Split view with resizable panels
 * - Mobile/Tablet (<1024px): Tab-based view (Tree or Viewer)
 * - Cmd+P / Ctrl+P: Quick file search
 */
export function FileBrowser({ teamId }: FileBrowserProps) {
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
  const [projectRoot, setProjectRoot] = useState<string>("")
  const [activeTab, setActiveTab] = useState<string>("tree")
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const isDesktop = useIsDesktop()

  // Cmd+P / Ctrl+P hotkey for file search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+P (Mac) or Ctrl+P (Windows/Linux)
      if ((e.metaKey || e.ctrlKey) && e.key === "p") {
        e.preventDefault()
        setIsSearchOpen(true)
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  const handleFileSelect = useCallback((path: string) => {
    setSelectedPath(path)
    // On mobile, switch to viewer tab when file is selected
    if (!isDesktop) {
      setActiveTab("viewer")
    }
  }, [isDesktop])

  const handleProjectRootChange = useCallback((root: string) => {
    setProjectRoot(root)
  }, [])

  // Desktop layout: Resizable split panels
  if (isDesktop) {
    return (
      <div className="h-full flex flex-col min-h-0 overflow-hidden">
        {/* Search Bar */}
        <div className="flex items-center gap-2 px-3 py-2 border-b bg-card">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsSearchOpen(true)}
                className="flex-1 justify-start text-muted-foreground font-normal"
              >
                <Search className="h-4 w-4 mr-2" />
                <span>Search files...</span>
                <kbd className="ml-auto text-xs bg-muted px-1.5 py-0.5 rounded">
                  {navigator.platform?.includes("Mac") ? "⌘P" : "Ctrl+P"}
                </kbd>
              </Button>
            </TooltipTrigger>
            <TooltipContent>Quick file search</TooltipContent>
          </Tooltip>
        </div>

        {/* File Search Dialog */}
        <FileSearch
          teamId={teamId}
          isOpen={isSearchOpen}
          onOpenChange={setIsSearchOpen}
          onFileSelect={handleFileSelect}
        />

        {/* Resizable Panels */}
        <ResizablePanelGroup direction="horizontal" className="flex-1 min-h-0 overflow-hidden">
          {/* File Tree Panel */}
          <ResizablePanel
            defaultSize={30}
            minSize={20}
            maxSize={50}
            className="bg-card border-r h-full min-h-0 overflow-hidden"
          >
            <FileTree
              teamId={teamId}
              selectedPath={selectedPath}
              onFileSelect={handleFileSelect}
              onProjectRootChange={handleProjectRootChange}
            />
          </ResizablePanel>

          <ResizableHandle withHandle />

          {/* File Viewer Panel */}
          <ResizablePanel defaultSize={70} minSize={50} className="h-full min-h-0">
            <div className="h-full min-h-0 bg-background">
              <FileViewer
                teamId={teamId}
                filePath={selectedPath}
                projectRoot={projectRoot}
              />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    )
  }

  // Mobile/Tablet layout: Tab-based view
  return (
    <div className="h-full flex flex-col min-h-0 overflow-hidden">
      {/* File Search Dialog (shared) */}
      <FileSearch
        teamId={teamId}
        isOpen={isSearchOpen}
        onOpenChange={setIsSearchOpen}
        onFileSelect={handleFileSelect}
      />

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="h-full flex flex-col min-h-0 overflow-hidden"
      >
        {/* Tab switcher header with search button */}
        <div className="border-b bg-card px-2 py-1.5 flex items-center gap-2">
          <TabsList className="flex-1 grid grid-cols-2">
            <TabsTrigger value="tree" className="flex items-center gap-2">
              <FolderTree className="h-4 w-4" />
              <span>Files</span>
            </TabsTrigger>
            <TabsTrigger value="viewer" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span>Viewer</span>
              {selectedPath && (
                <span className="ml-1 text-xs text-muted-foreground truncate max-w-[100px]">
                  ({selectedPath.split("/").pop()})
                </span>
              )}
            </TabsTrigger>
          </TabsList>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setIsSearchOpen(true)}
          >
            <Search className="h-4 w-4" />
          </Button>
        </div>

        {/* Tab content - full width */}
        <TabsContent value="tree" className="flex-1 m-0 min-h-0 data-[state=inactive]:hidden">
          <div className="h-full bg-card min-h-0 overflow-hidden">
            <FileTree
              teamId={teamId}
              selectedPath={selectedPath}
              onFileSelect={handleFileSelect}
              onProjectRootChange={handleProjectRootChange}
            />
          </div>
        </TabsContent>

        <TabsContent value="viewer" className="flex-1 m-0 data-[state=inactive]:hidden">
          <div className="h-full bg-background">
            <FileViewer
              teamId={teamId}
              filePath={selectedPath}
              projectRoot={projectRoot}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
