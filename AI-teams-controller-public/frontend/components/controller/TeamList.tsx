"use client"

import { cn } from "@/lib/utils"

/**
 * Team type for list display (focused, minimal interface)
 */
export type Team = {
  id: string
  name: string
}

/**
 * Props for TeamList component (ISP - Interface Segregation Principle)
 * Only includes props directly used by this component
 */
export interface TeamListProps {
  /** List of available teams */
  teams: Team[]
  /** Currently selected team ID (null if none selected) */
  selectedTeam: string | null
  /** Callback when a team is selected */
  onSelectTeam: (teamId: string) => void
  /** Optional: Set of team IDs with unread notifications */
  teamNotifications?: Set<string>
}

/**
 * TeamList Component
 *
 * Pure, focused component for displaying a list of teams with selection.
 * Follows ISP (Interface Segregation Principle) by accepting only the props it needs.
 *
 * @example
 * ```tsx
 * <TeamList
 *   teams={[{ id: '1', name: 'Team A' }]}
 *   selectedTeam="1"
 *   onSelectTeam={(id) => console.log(id)}
 *   teamNotifications={new Set(['2'])}
 * />
 * ```
 */
export function TeamList({
  teams,
  selectedTeam,
  onSelectTeam,
  teamNotifications = new Set(),
}: TeamListProps) {
  return (
    <div className="space-y-1">
      {teams.map((team) => {
        const isSelected = selectedTeam === team.id
        const hasNotification = teamNotifications.has(team.id)

        return (
          <button
            key={team.id}
            onClick={() => onSelectTeam(team.id)}
            className={cn(
              "w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center gap-2",
              isSelected
                ? "bg-primary text-primary-foreground font-semibold border-l-4 border-primary-foreground shadow-sm"
                : hasNotification
                  ? "text-green-500 bg-green-500/10 hover:bg-green-500/20 font-medium"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50",
            )}
            title={hasNotification ? "New activity" : ""}
            aria-current={isSelected ? "page" : undefined}
          >
            {team.name}
          </button>
        )
      })}
    </div>
  )
}
