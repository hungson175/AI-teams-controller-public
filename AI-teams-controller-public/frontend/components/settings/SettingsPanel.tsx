"use client"

import { useState, useCallback, useEffect } from "react"
import { useSettings, type Settings, DEFAULT_SETTINGS } from "@/contexts/SettingsContext"
import { useAuth } from "@/contexts/AuthContext"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, Save, RotateCcw, AlertCircle, Check } from "lucide-react"
import { cn } from "@/lib/utils"

// ============================================
// Constants
// ============================================

const NOISE_FILTER_OPTIONS = [
  { value: "very-low", label: "Very Low (Quiet environment)" },
  { value: "low", label: "Low (Home office)" },
  { value: "medium", label: "Medium (Balanced)" },
  { value: "high", label: "High (Noisy office)" },
  { value: "very-high", label: "Very High (Very noisy)" },
] as const

const THEME_OPTIONS = [
  { value: "light", label: "Light" },
  { value: "dark", label: "Dark" },
  { value: "system", label: "System" },
] as const

// ============================================
// Types
// ============================================

interface SettingsPanelProps {
  className?: string
  compact?: boolean
}

// ============================================
// Component
// ============================================

export function SettingsPanel({ className, compact = false }: SettingsPanelProps) {
  const { isAuthenticated } = useAuth()
  const {
    settings: savedSettings,
    isLoading,
    isSyncing,
    hasUnsavedChanges: contextHasUnsaved,
    error,
    updateSettings,
    syncToServer,
    resetToDefaults,
  } = useSettings()

  // Local form state for editing
  const [localSettings, setLocalSettings] = useState<Settings>(savedSettings)
  const [localHasChanges, setLocalHasChanges] = useState(false)
  const [applySuccess, setApplySuccess] = useState(false)

  // Sync local state when saved settings change (e.g., after server load)
  useEffect(() => {
    setLocalSettings(savedSettings)
    setLocalHasChanges(false)
  }, [savedSettings])

  // Clear success message after delay
  useEffect(() => {
    if (applySuccess) {
      const timeout = setTimeout(() => setApplySuccess(false), 3000)
      return () => clearTimeout(timeout)
    }
  }, [applySuccess])

  // ============================================
  // Handlers
  // ============================================

  const handleChange = useCallback(<K extends keyof Settings>(key: K, value: Settings[K]) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }))
    setLocalHasChanges(true)
    setApplySuccess(false)
  }, [])

  const handleApply = useCallback(async () => {
    // Update context with local changes
    updateSettings(localSettings)

    // Sync to server if authenticated
    if (isAuthenticated) {
      const success = await syncToServer()
      if (success) {
        // Dispatch custom event for other components to react
        window.dispatchEvent(new CustomEvent("settings-updated", {
          detail: { settings: localSettings },
        }))
        setApplySuccess(true)
      }
    } else {
      // Not authenticated - just update local
      window.dispatchEvent(new CustomEvent("settings-updated", {
        detail: { settings: localSettings },
      }))
      setApplySuccess(true)
    }

    setLocalHasChanges(false)
  }, [localSettings, updateSettings, syncToServer, isAuthenticated])

  const handleReset = useCallback(() => {
    setLocalSettings(DEFAULT_SETTINGS)
    setLocalHasChanges(true)
    setApplySuccess(false)
  }, [])

  const handleResetToSaved = useCallback(() => {
    setLocalSettings(savedSettings)
    setLocalHasChanges(false)
    setApplySuccess(false)
  }, [savedSettings])

  // ============================================
  // Render
  // ============================================

  if (isLoading) {
    return (
      <Card className={cn("w-full", className)}>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    )
  }

  const hasUnsavedChanges = localHasChanges || contextHasUnsaved

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className={compact ? "pb-2" : undefined}>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className={compact ? "text-lg" : undefined}>Voice Settings</CardTitle>
            {!compact && (
              <CardDescription>Configure voice detection and recording preferences</CardDescription>
            )}
          </div>
          {hasUnsavedChanges && (
            <div className="flex items-center gap-1 text-sm text-amber-600 dark:text-amber-500">
              <AlertCircle className="h-4 w-4" />
              <span>Unsaved changes</span>
            </div>
          )}
          {applySuccess && (
            <div className="flex items-center gap-1 text-sm text-green-600 dark:text-green-500">
              <Check className="h-4 w-4" />
              <span>Settings applied</span>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className={cn("space-y-4", compact && "pt-0")}>
        {error && (
          <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
            {error}
          </div>
        )}

        {/* Stop Word */}
        <div className="space-y-2">
          <Label htmlFor="stop-word">Stop Word</Label>
          <Input
            id="stop-word"
            value={localSettings.stop_word}
            onChange={(e) => handleChange("stop_word", e.target.value)}
            placeholder="e.g., thank you"
            maxLength={50}
          />
          <p className="text-xs text-muted-foreground">
            Say this phrase to send your command
          </p>
        </div>

        {/* Noise Filter */}
        <div className="space-y-2">
          <Label htmlFor="noise-filter">Noise Filter Level</Label>
          <Select
            value={localSettings.noise_filter_level}
            onValueChange={(value) => handleChange("noise_filter_level", value as Settings["noise_filter_level"])}
          >
            <SelectTrigger id="noise-filter">
              <SelectValue placeholder="Select noise filter level" />
            </SelectTrigger>
            <SelectContent>
              {NOISE_FILTER_OPTIONS.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Speech Speed */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="speech-speed">Speech Speed</Label>
            <span className="text-sm font-medium">
              {localSettings.speech_speed.toFixed(1)}x
            </span>
          </div>

          <Slider
            id="speech-speed"
            value={[localSettings.speech_speed]}
            min={0.5}
            max={2.0}
            step={0.1}
            onValueChange={(value) => handleChange("speech_speed", value[0])}
            className="w-full"
            aria-label="Speech speed"
          />

          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Slow (0.5x)</span>
            <span>Fast (2.0x)</span>
          </div>

          <p className="text-xs text-muted-foreground">
            Controls voice feedback playback speed. Lower is slower, higher is faster.
          </p>
        </div>

        {/* Theme */}
        <div className="space-y-2">
          <Label htmlFor="theme">Theme</Label>
          <Select
            value={localSettings.theme}
            onValueChange={(value) => handleChange("theme", value as Settings["theme"])}
          >
            <SelectTrigger id="theme">
              <SelectValue placeholder="Select theme" />
            </SelectTrigger>
            <SelectContent>
              {THEME_OPTIONS.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 pt-2">
          <Button
            onClick={handleApply}
            disabled={!hasUnsavedChanges || isSyncing}
            className="flex-1"
          >
            {isSyncing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Apply Settings
              </>
            )}
          </Button>

          {hasUnsavedChanges && (
            <Button
              variant="outline"
              onClick={handleResetToSaved}
              disabled={isSyncing}
            >
              Cancel
            </Button>
          )}

          <Button
            variant="ghost"
            size="icon"
            onClick={handleReset}
            disabled={isSyncing}
            title="Reset to defaults"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>

        {!isAuthenticated && (
          <p className="text-xs text-muted-foreground text-center">
            Sign in to sync settings across devices
          </p>
        )}
      </CardContent>
    </Card>
  )
}

export default SettingsPanel
