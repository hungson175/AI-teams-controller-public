/**
 * ModeToggle Component
 *
 * Toggle between Design and Monitor modes in Team Creator.
 * - Design: Create/edit team layouts (no tmux connection)
 * - Monitor: View live agent status from tmux
 *
 * Sprint 32: Team Creator S5 - Real-time Status
 * Sprint 33: Added tooltips for better discoverability
 */
"use client"

import { Pencil, Activity } from "lucide-react"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { TeamCreatorMode } from "@/lib/team-creator/types"

interface ModeToggleProps {
  mode: TeamCreatorMode
  onModeChange: (mode: TeamCreatorMode) => void
}

export function ModeToggle({ mode, onModeChange }: ModeToggleProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <ToggleGroup
          type="single"
          value={mode}
          onValueChange={(value) => {
            if (value) onModeChange(value as TeamCreatorMode)
          }}
          className="bg-muted rounded-md p-0.5"
          aria-label="Team Creator mode"
        >
          <ToggleGroupItem
            value="design"
            className="gap-1.5 px-3 py-1.5 text-xs data-[state=on]:bg-violet-500 data-[state=on]:text-white"
            aria-label="Design mode - Create team layouts"
          >
            <Pencil className="h-3.5 w-3.5" />
            Design
          </ToggleGroupItem>
          <ToggleGroupItem
            value="monitor"
            className="gap-1.5 px-3 py-1.5 text-xs data-[state=on]:bg-blue-500 data-[state=on]:text-white"
            aria-label="Monitor mode - View live team status"
          >
            <Activity className="h-3.5 w-3.5" />
            Monitor
          </ToggleGroupItem>
        </ToggleGroup>
      </TooltipTrigger>
      <TooltipContent side="bottom" sideOffset={8}>
        {mode === "design"
          ? "Design mode: Create and edit team layouts"
          : "Monitor mode: View live agent status from tmux"}
      </TooltipContent>
    </Tooltip>
  )
}
