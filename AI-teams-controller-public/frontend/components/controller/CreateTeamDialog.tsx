"use client"

import { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Loader2, Plus, AlertCircle } from "lucide-react"
import { getAuthHeaders } from "@/lib/auth-utils"

// Types matching backend schemas
interface TemplateRole {
  id: string
  name: string
  description: string
  optional: boolean
}

interface TeamTemplate {
  name: string
  display_name: string
  description: string
  version: string
  roles: TemplateRole[]
}

interface CreateTeamResponse {
  success: boolean
  team_id: string
  message: string
  output_dir: string
}

/**
 * CreateTeamDialog Component
 *
 * Dialog for creating a new AI team from a template.
 *
 * Features:
 * - Template selector dropdown (fetches from GET /api/templates)
 * - Project name input with validation
 * - PRD (Project Requirements Document) textarea
 * - Submits to POST /api/templates/create
 * - Success/error handling with messages
 */
export interface CreateTeamDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: (teamId: string) => void
}

export function CreateTeamDialog({
  open,
  onOpenChange,
  onSuccess,
}: CreateTeamDialogProps) {
  // Form state
  const [selectedTemplate, setSelectedTemplate] = useState<string>("")
  const [projectName, setProjectName] = useState<string>("")
  const [prd, setPrd] = useState<string>("")
  const [projectNameError, setProjectNameError] = useState<string>("")

  // API state
  const [templates, setTemplates] = useState<TeamTemplate[]>([])
  const [isLoadingTemplates, setIsLoadingTemplates] = useState<boolean>(true)
  const [templatesError, setTemplatesError] = useState<string>("")
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [submitError, setSubmitError] = useState<string>("")

  // Validate project name (alphanumeric, hyphens, underscores only)
  const validateProjectName = useCallback((name: string): boolean => {
    if (!name) return true // Empty is valid (will show as required)
    const validPattern = /^[a-zA-Z0-9_-]+$/
    return validPattern.test(name)
  }, [])

  const handleProjectNameChange = useCallback((value: string) => {
    setProjectName(value)
    if (value && !validateProjectName(value)) {
      setProjectNameError("Only letters, numbers, hyphens, and underscores allowed")
    } else {
      setProjectNameError("")
    }
  }, [validateProjectName])

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      // Reset form state when opening
      setSelectedTemplate("")
      setProjectName("")
      setPrd("")
      setProjectNameError("")
      setSubmitError("")
      // Fetch templates
      fetchTemplates()
    }
  }, [open])

  // Fetch templates from API
  const fetchTemplates = async () => {
    setIsLoadingTemplates(true)
    setTemplatesError("")

    try {
      const response = await fetch("/api/templates", {
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch templates: ${response.status}`)
      }

      const data = await response.json()
      setTemplates(data.templates || [])
    } catch (error) {
      console.error("[CreateTeamDialog] Failed to fetch templates:", error)
      setTemplatesError("Failed to load templates. Please try again.")
    } finally {
      setIsLoadingTemplates(false)
    }
  }

  // Check if form is valid
  const isFormValid =
    selectedTemplate !== "" &&
    projectName.trim() !== "" &&
    prd.trim() !== "" &&
    projectNameError === ""

  // Handle form submission
  const handleSubmit = async () => {
    if (!isFormValid || isSubmitting) return

    setIsSubmitting(true)
    setSubmitError("")

    try {
      const response = await fetch("/api/templates/create", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          template_name: selectedTemplate,
          project_name: projectName.trim(),
          prd: prd.trim(),
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || `Failed to create team: ${response.status}`)
      }

      const result = data as CreateTeamResponse

      if (result.success) {
        onSuccess(result.team_id)
        onOpenChange(false)
      } else {
        throw new Error(result.message || "Failed to create team")
      }
    } catch (error) {
      console.error("[CreateTeamDialog] Failed to create team:", error)
      setSubmitError(error instanceof Error ? error.message : "Failed to create team")
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

  // Get selected template details
  const selectedTemplateDetails = templates.find(t => t.name === selectedTemplate)

  return (
    <Dialog open={open} onOpenChange={(open) => !isSubmitting && onOpenChange(open)}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Create New Team
          </DialogTitle>
          <DialogDescription>
            Create a new AI team from a template. Fill in the project details below.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Template Selector */}
          <div className="space-y-2">
            <Label htmlFor="template">Template</Label>
            {isLoadingTemplates ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading templates...
              </div>
            ) : templatesError ? (
              <div className="flex items-center gap-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                {templatesError}
              </div>
            ) : (
              <Select
                value={selectedTemplate}
                onValueChange={setSelectedTemplate}
                disabled={isSubmitting}
              >
                <SelectTrigger id="template" className="w-full">
                  <SelectValue placeholder="Select a template" />
                </SelectTrigger>
                <SelectContent>
                  {templates.map((template) => (
                    <SelectItem key={template.name} value={template.name}>
                      {template.display_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            {selectedTemplateDetails && (
              <p className="text-xs text-muted-foreground">
                {selectedTemplateDetails.description}
              </p>
            )}
          </div>

          {/* Project Name */}
          <div className="space-y-2">
            <Label htmlFor="projectName">Project Name</Label>
            <Input
              id="projectName"
              placeholder="my-project"
              value={projectName}
              onChange={(e) => handleProjectNameChange(e.target.value)}
              disabled={isSubmitting}
              className={projectNameError ? "border-destructive" : ""}
              aria-label="Project Name"
            />
            {projectNameError ? (
              <p className="text-xs text-destructive">{projectNameError}</p>
            ) : (
              <p className="text-xs text-muted-foreground">
                Alphanumeric, hyphens, and underscores only
              </p>
            )}
          </div>

          {/* PRD Textarea */}
          <div className="space-y-2">
            <Label htmlFor="prd">Project Description (PRD)</Label>
            <Textarea
              id="prd"
              placeholder="Describe your project requirements..."
              value={prd}
              onChange={(e) => setPrd(e.target.value)}
              disabled={isSubmitting}
              className="min-h-[120px]"
              aria-label="Project Description"
            />
            <p className="text-xs text-muted-foreground">
              This will be used to initialize your team with context
            </p>
          </div>

          {/* Submit Error */}
          {submitError && (
            <div className="flex items-center gap-2 text-sm text-destructive">
              <AlertCircle className="h-4 w-4" />
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
            onClick={handleSubmit}
            disabled={!isFormValid || isSubmitting}
          >
            {isSubmitting ? (
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
  )
}
