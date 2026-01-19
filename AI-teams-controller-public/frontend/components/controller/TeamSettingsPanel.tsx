"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { VoiceSettingsPanel } from "@/components/voice/VoiceSettingsPanel"

/**
 * Polling interval options in seconds
 */
export type PollingInterval = 0.5 | 1 | 2

/**
 * Props for TeamSettingsPanel component (ISP - Interface Segregation Principle)
 * Only includes settings-related props, no team or UI state props
 */
export interface TeamSettingsPanelProps {
  /** Current polling interval in seconds */
  pollingInterval: PollingInterval
  /** Number of lines to capture from pane output */
  captureLines: number
  /** Voice command stop word */
  stopWord: string
  /** Callback when polling interval changes */
  onPollingIntervalChange: (interval: PollingInterval) => void
  /** Callback when capture lines changes */
  onCaptureLinesChange: (lines: number) => void
  /** Callback when stop word changes */
  onStopWordChange: (word: string) => void
}

/**
 * TeamSettingsPanel Component
 *
 * Pure, focused component for displaying and modifying application settings.
 * Follows ISP (Interface Segregation Principle) by accepting only settings props.
 *
 * Includes:
 * - Polling interval selection (0.5s, 1s, 2s)
 * - Max lines / capture lines selection (50, 100, 200, 500)
 * - Stop word input (voice command trigger)
 * - Voice settings (speech speed via VoiceTeamSettingsPanel)
 *
 * @example
 * ```tsx
 * <TeamSettingsPanel
 *   pollingInterval={0.5}
 *   captureLines={100}
 *   stopWord="thank you"
 *   onPollingIntervalChange={(interval) => console.log(interval)}
 *   onCaptureLinesChange={(lines) => console.log(lines)}
 *   onStopWordChange={(word) => console.log(word)}
 * />
 * ```
 */
export function TeamSettingsPanel({
  pollingInterval,
  captureLines,
  stopWord,
  onPollingIntervalChange,
  onCaptureLinesChange,
  onStopWordChange,
}: TeamSettingsPanelProps) {
  return (
    <div className="space-y-3" data-testid="settings-panel">
      {/* Polling Interval */}
      <div>
        <label className="text-xs text-muted-foreground mb-2 block">Polling Interval</label>
        <div className="flex gap-1">
          {([0.5, 1, 2] as PollingInterval[]).map((interval) => (
            <Button
              key={interval}
              variant={pollingInterval === interval ? "default" : "outline"}
              size="sm"
              className="flex-1 h-8 text-xs"
              onClick={() => onPollingIntervalChange(interval)}
            >
              {interval}s
            </Button>
          ))}
        </div>
      </div>

      {/* Max Lines */}
      <div>
        <label className="text-xs text-muted-foreground mb-2 block">Max Lines</label>
        <div className="flex gap-1">
          {([50, 100, 200, 500] as const).map((lines) => (
            <Button
              key={lines}
              variant={captureLines === lines ? "default" : "outline"}
              size="sm"
              className="flex-1 h-8 text-xs"
              onClick={() => onCaptureLinesChange(lines)}
            >
              {lines}
            </Button>
          ))}
        </div>
      </div>

      {/* Stop Word */}
      <div>
        <label className="text-xs text-muted-foreground mb-2 block">Stop Word</label>
        <Input
          value={stopWord}
          onChange={(e) => onStopWordChange(e.target.value)}
          placeholder="thank you"
          className="h-8 text-xs"
          style={{ fontSize: '16px' }}
        />
        <p className="text-[10px] text-muted-foreground mt-1">
          Say this to send command
        </p>
      </div>

      {/* Voice Settings Panel (Speech Speed only) */}
      <div className="pt-4 border-t">
        <VoiceSettingsPanel />
      </div>
    </div>
  )
}
