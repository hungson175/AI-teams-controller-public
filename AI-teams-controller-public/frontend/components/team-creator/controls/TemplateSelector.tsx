"use client"

import { useState } from "react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { LayoutTemplate, AlertTriangle } from "lucide-react"
import { getAllTemplates, TeamTemplate } from "@/lib/team-creator/templates"

interface TemplateSelectorProps {
  onSelectTemplate: (template: TeamTemplate) => void
  hasUnsavedChanges?: boolean
}

export function TemplateSelector({
  onSelectTemplate,
  hasUnsavedChanges = false,
}: TemplateSelectorProps) {
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("")
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  const [pendingTemplate, setPendingTemplate] = useState<TeamTemplate | null>(null)

  const templates = getAllTemplates()

  const handleSelectChange = (templateId: string) => {
    const template = templates.find((t) => t.id === templateId)
    if (!template) return

    if (hasUnsavedChanges) {
      // Show confirmation dialog if there are unsaved changes
      setPendingTemplate(template)
      setShowConfirmDialog(true)
    } else {
      // Load template directly
      setSelectedTemplateId(templateId)
      onSelectTemplate(template)
    }
  }

  const handleConfirmLoad = () => {
    if (pendingTemplate) {
      setSelectedTemplateId(pendingTemplate.id)
      onSelectTemplate(pendingTemplate)
    }
    setShowConfirmDialog(false)
    setPendingTemplate(null)
  }

  const handleCancelLoad = () => {
    setShowConfirmDialog(false)
    setPendingTemplate(null)
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <LayoutTemplate className="h-4 w-4 text-muted-foreground" />
        <Select value={selectedTemplateId} onValueChange={handleSelectChange}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Load template..." />
          </SelectTrigger>
          <SelectContent>
            {templates.map((template) => (
              <SelectItem key={template.id} value={template.id}>
                <div className="flex flex-col">
                  <span className="font-medium">{template.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {template.description}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              Unsaved Changes
            </DialogTitle>
            <DialogDescription>
              You have unsaved changes to your current team configuration. Loading
              a new template will discard these changes.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={handleCancelLoad}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleConfirmLoad}>
              Discard & Load
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
