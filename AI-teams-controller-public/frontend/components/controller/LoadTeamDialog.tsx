"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Loader2, Download, AlertCircle, CheckCircle2 } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { listAvailableTeams, loadTeam, AvailableTeam } from "@/lib/api/teams"

/**
 * LoadTeamDialog Component
 *
 * Dialog for browsing and loading existing AI teams.
 *
 * Features:
 * - Fetch available teams from GET /api/teams/available
 * - Display list with: name, status (active/inactive), setup script indicator
 * - Load button disabled if no setup script
 * - Calls POST /api/teams/load/{team_name} to load team
 * - Loading/error states with user feedback
 */
export interface LoadTeamDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: (teamName: string) => void
}

export function LoadTeamDialog({
  open,
  onOpenChange,
  onSuccess,
}: LoadTeamDialogProps) {
  // Team list state
  const [teams, setTeams] = useState<AvailableTeam[]>([])
  const [isLoadingTeams, setIsLoadingTeams] = useState<boolean>(true)
  const [teamsError, setTeamsError] = useState<string>("")

  // Selection state
  const [selectedTeamName, setSelectedTeamName] = useState<string>("")

  // Loading state
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [submitError, setSubmitError] = useState<string>("")

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      // Reset form state when opening
      setSelectedTeamName("")
      setSubmitError("")
      // Fetch teams
      fetchTeams()
    }
  }, [open])

  // Fetch teams from API
  const fetchTeams = async () => {
    setIsLoadingTeams(true)
    setTeamsError("")

    try {
      const availableTeams = await listAvailableTeams()
      setTeams(availableTeams)
    } catch (error) {
      console.error("[LoadTeamDialog] Failed to fetch teams:", error)
      setTeamsError("Failed to load teams. Please try again.")
    } finally {
      setIsLoadingTeams(false)
    }
  }

  // Get selected team details
  const selectedTeam = teams.find(t => t.name === selectedTeamName)
  const canLoad = selectedTeamName !== "" && selectedTeam?.hasSetupScript === true

  // Handle team loading
  const handleLoad = async () => {
    if (!canLoad || isSubmitting) return

    setIsSubmitting(true)
    setSubmitError("")

    try {
      const result = await loadTeam(selectedTeamName)

      if (result.success) {
        onSuccess(selectedTeamName)
        onOpenChange(false)
      } else {
        throw new Error(result.message || "Failed to load team")
      }
    } catch (error) {
      console.error("[LoadTeamDialog] Failed to load team:", error)
      setSubmitError(error instanceof Error ? error.message : "Failed to load team")
    } finally {
      setIsSubmitting(false)
    }
  }

  // Handle cancel
  const handleCancel = () => {
    if (!isSubmitting) {
      onOpenChange(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !isSubmitting && onOpenChange(open)}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Load Team
          </DialogTitle>
          <DialogDescription>
            Browse and load existing AI teams from your workspace.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Teams List */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Available Teams</label>

            {isLoadingTeams ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground p-4 bg-muted/50 rounded-md">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading teams...
              </div>
            ) : teamsError ? (
              <div className="flex items-center gap-2 text-sm text-destructive p-4 bg-destructive/10 rounded-md">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                {teamsError}
              </div>
            ) : teams.length === 0 ? (
              <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-md text-center">
                No teams found in your workspace
              </div>
            ) : (
              <ul className="space-y-1 max-h-[300px] overflow-y-auto border border-input rounded-md p-1">
                {teams.map((team) => (
                  <li key={team.name}>
                    <button
                      onClick={() => setSelectedTeamName(team.name)}
                      className={`w-full text-left px-3 py-2 rounded-md transition-colors flex items-center justify-between text-sm ${
                        selectedTeamName === team.name
                          ? "bg-primary text-primary-foreground ring-2 ring-offset-2 ring-primary"
                          : "hover:bg-muted/50"
                      }`}
                      disabled={isSubmitting}
                    >
                      <div className="flex-1">
                        <div className="font-medium">{team.name}</div>
                        <div className="text-xs opacity-75">
                          {team.path}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 ml-2 flex-shrink-0">
                        {/* Status Indicator */}
                        <span className={`text-xs px-2 py-1 rounded ${
                          team.isActive
                            ? "bg-green-500/20 text-green-700 dark:text-green-400"
                            : "bg-gray-500/20 text-gray-700 dark:text-gray-400"
                        }`}>
                          {team.isActive ? "active" : "inactive"}
                        </span>

                        {/* Setup Script Indicator */}
                        {team.hasSetupScript && (
                          <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                        )}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}

            {/* No Setup Script Warning */}
            {selectedTeam && !selectedTeam.hasSetupScript && (
              <div className="flex items-start gap-2 text-sm text-amber-700 dark:text-amber-300 p-3 bg-amber-50/50 dark:bg-amber-950/30 rounded-md">
                <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                <span>This team does not have a setup script and cannot be loaded.</span>
              </div>
            )}
          </div>

          {/* Submit Error */}
          {submitError && (
            <div className="flex items-center gap-2 text-sm text-destructive p-3 bg-destructive/10 rounded-md">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              {submitError}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleLoad}
            disabled={!canLoad || isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Loading...
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Load
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
