"use client"

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useMemo,
  type ReactNode,
} from "react"
import { useAuth } from "./AuthContext"
import { getAuthHeaders } from "@/lib/auth-utils"
import { tryRefreshTokens } from "@/lib/auth"

// ============================================
// Types
// ============================================

// Only stopword detection mode is supported
export type DetectionMode = "stopword"
export type NoiseFilterLevel = "very-low" | "low" | "medium" | "high" | "very-high"
export type Theme = "light" | "dark" | "system"

export interface Settings {
  detection_mode: DetectionMode
  stop_word: string
  noise_filter_level: NoiseFilterLevel
  theme: Theme
  speech_speed: number
}

export interface SettingsResponse extends Settings {
  updated_at: string
}

export interface SettingsState {
  settings: Settings
  isLoading: boolean
  isSyncing: boolean
  lastSynced: number | null
  hasUnsavedChanges: boolean
  error: string | null
}

interface SettingsContextValue extends SettingsState {
  updateSetting: <K extends keyof Settings>(key: K, value: Settings[K]) => void
  updateSettings: (updates: Partial<Settings>) => void
  syncToServer: () => Promise<boolean>
  resetToDefaults: () => void
}

// ============================================
// Constants
// ============================================

// localStorage keys for migration
const LEGACY_KEYS = {
  NOISE_FILTER: "voice-noise-filter",
  STOP_WORD: "voice-stop-word",
  SPEECH_SPEED: "speech-speed",
}

// New unified localStorage key
const SETTINGS_CACHE_KEY = "ai_teams_settings_cache"

// Deprecated stopwords that should be migrated to "thank you"
const DEPRECATED_STOP_WORDS = ["go go go"]

export const DEFAULT_SETTINGS: Settings = {
  detection_mode: "stopword",
  stop_word: "thank you",
  noise_filter_level: "medium",
  theme: "system",
  speech_speed: 0.58,  // 20% slower than normal (Boss requirement)
}

// ============================================
// Context
// ============================================

const SettingsContext = createContext<SettingsContextValue | null>(null)

// ============================================
// Provider
// ============================================

interface SettingsProviderProps {
  children: ReactNode
}

export function SettingsProvider({ children }: SettingsProviderProps) {
  const { isAuthenticated, isLoading: authLoading } = useAuth()

  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS)
  const [isLoading, setIsLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)
  const [lastSynced, setLastSynced] = useState<number | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // ============================================
  // Migration Helper
  // ============================================

  // Helper to migrate deprecated stopwords (must be defined first)
  const migrateStopWord = useCallback((word: string): string => {
    if (DEPRECATED_STOP_WORDS.includes(word.toLowerCase())) {
      console.log(`[Settings] Migrating deprecated stopword "${word}" to "thank you"`)
      return DEFAULT_SETTINGS.stop_word
    }
    return word
  }, [])

  // ============================================
  // localStorage Helpers
  // ============================================

  const saveToLocalStorage = useCallback((newSettings: Settings) => {
    if (typeof window === "undefined") return
    try {
      localStorage.setItem(SETTINGS_CACHE_KEY, JSON.stringify(newSettings))
      // Also update legacy keys for backwards compatibility with voice recorder
      localStorage.setItem(LEGACY_KEYS.STOP_WORD, newSettings.stop_word || DEFAULT_SETTINGS.stop_word)
      localStorage.setItem(LEGACY_KEYS.NOISE_FILTER, newSettings.noise_filter_level || DEFAULT_SETTINGS.noise_filter_level)
      localStorage.setItem(LEGACY_KEYS.SPEECH_SPEED, (newSettings.speech_speed ?? DEFAULT_SETTINGS.speech_speed).toString())
    } catch (err) {
      console.error("[Settings] localStorage save error:", err)
    }
  }, [])

  const loadFromLocalStorage = useCallback((): Settings | null => {
    if (typeof window === "undefined") return null
    try {
      // First try unified cache
      const cached = localStorage.getItem(SETTINGS_CACHE_KEY)
      if (cached) {
        const settings = JSON.parse(cached) as Settings
        // Migrate deprecated stopwords in cached settings
        settings.stop_word = migrateStopWord(settings.stop_word)
        return settings
      }

      // Fall back to legacy keys (for migration)
      const stopWord = localStorage.getItem(LEGACY_KEYS.STOP_WORD)
      const noiseFilter = localStorage.getItem(LEGACY_KEYS.NOISE_FILTER)
      const speechSpeed = localStorage.getItem(LEGACY_KEYS.SPEECH_SPEED)

      if (stopWord || noiseFilter || speechSpeed) {
        return {
          detection_mode: "stopword" as DetectionMode,  // Only stopword mode supported
          stop_word: migrateStopWord(stopWord || DEFAULT_SETTINGS.stop_word),
          noise_filter_level: (noiseFilter as NoiseFilterLevel) || DEFAULT_SETTINGS.noise_filter_level,
          theme: DEFAULT_SETTINGS.theme,
          speech_speed: speechSpeed ? parseFloat(speechSpeed) : DEFAULT_SETTINGS.speech_speed,
        }
      }
    } catch (err) {
      console.error("[Settings] localStorage load error:", err)
    }
    return null
  }, [migrateStopWord])

  // ============================================
  // API Helpers
  // ============================================

  const fetchFromServer = useCallback(async (): Promise<{ settings: Settings; migrated: boolean } | null> => {
    try {
      let response = await fetch(`/api/settings`, {
        headers: getAuthHeaders(),
      })

      // Handle 401: try refresh tokens and retry once
      if (response.status === 401) {
        const refreshed = await tryRefreshTokens()
        if (refreshed) {
          response = await fetch(`/api/settings`, {
            headers: getAuthHeaders(),
          })
        } else {
          console.error("[Settings] Token refresh failed")
          return null
        }
      }

      if (!response.ok) {
        throw new Error(`Settings fetch failed: ${response.status}`)
      }

      const data: SettingsResponse = await response.json()
      const originalStopWord = data.stop_word
      const migratedStopWord = migrateStopWord(data.stop_word)
      const migrated = originalStopWord !== migratedStopWord

      return {
        settings: {
          detection_mode: "stopword" as DetectionMode,  // Only stopword mode supported
          stop_word: migratedStopWord,
          noise_filter_level: data.noise_filter_level as NoiseFilterLevel,
          theme: data.theme as Theme,
        },
        migrated,
      }
    } catch (err) {
      console.error("[Settings] Server fetch error:", err)
      return null
    }
  }, [migrateStopWord])

  const saveToServer = useCallback(async (settingsToSave: Settings): Promise<boolean> => {
    try {
      let response = await fetch(`/api/settings`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(settingsToSave),
      })

      // Handle 401: try refresh tokens and retry once
      if (response.status === 401) {
        const refreshed = await tryRefreshTokens()
        if (refreshed) {
          response = await fetch(`/api/settings`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: JSON.stringify(settingsToSave),
          })
        } else {
          console.error("[Settings] Token refresh failed")
          return false
        }
      }

      if (!response.ok) {
        throw new Error(`Settings save failed: ${response.status}`)
      }

      return true
    } catch (err) {
      console.error("[Settings] Server save error:", err)
      return false
    }
  }, [])

  // ============================================
  // Initialization (localStorage → DB migration)
  // ============================================

  useEffect(() => {
    // Wait for auth to finish loading
    if (authLoading) return

    const initialize = async () => {
      setIsLoading(true)
      setError(null)

      if (isAuthenticated) {
        // User is logged in - fetch from server
        const result = await fetchFromServer()

        if (result) {
          const { settings: serverSettings, migrated } = result
          // Server has settings - use them (migration already applied in fetchFromServer)
          setSettings(serverSettings)
          saveToLocalStorage(serverSettings)
          setLastSynced(Date.now())
          console.log("[Settings] Loaded from server")

          // If stopword was migrated from deprecated value, persist to server
          if (migrated) {
            console.log("[Settings] Persisting migrated stopword to server...")
            await saveToServer(serverSettings)
          }
        } else {
          // No server settings or fetch failed - migrate from localStorage
          const localSettings = loadFromLocalStorage()

          if (localSettings) {
            // Found localStorage settings - migrate to server
            console.log("[Settings] Migrating localStorage to database...")
            setSettings(localSettings)
            const success = await saveToServer(localSettings)
            if (success) {
              setLastSynced(Date.now())
              console.log("[Settings] Migration successful")
            } else {
              setError("Failed to sync settings to server")
            }
            saveToLocalStorage(localSettings)
          } else {
            // No local settings either - use defaults and save to server
            console.log("[Settings] Using defaults, saving to server...")
            setSettings(DEFAULT_SETTINGS)
            await saveToServer(DEFAULT_SETTINGS)
            saveToLocalStorage(DEFAULT_SETTINGS)
            setLastSynced(Date.now())
          }
        }
      } else {
        // Not logged in - use localStorage only
        const localSettings = loadFromLocalStorage()
        if (localSettings) {
          setSettings(localSettings)
          console.log("[Settings] Loaded from localStorage (offline)")
        } else {
          setSettings(DEFAULT_SETTINGS)
          saveToLocalStorage(DEFAULT_SETTINGS)
          console.log("[Settings] Using defaults (offline)")
        }
      }

      setIsLoading(false)
    }

    initialize()
  }, [isAuthenticated, authLoading, fetchFromServer, saveToServer, loadFromLocalStorage, saveToLocalStorage])

  // ============================================
  // Update Handlers (save immediately to avoid race conditions)
  // ============================================

  const updateSetting = useCallback(
    <K extends keyof Settings>(key: K, value: Settings[K]) => {
      setSettings((prev) => {
        const newSettings = { ...prev, [key]: value }

        // Save to localStorage immediately (avoid race condition)
        saveToLocalStorage(newSettings)

        // Mark as having unsaved changes (for server sync)
        setHasUnsavedChanges(true)

        return newSettings
      })
    },
    [saveToLocalStorage]
  )

  const updateSettings = useCallback(
    (updates: Partial<Settings>) => {
      setSettings((prev) => {
        const newSettings = { ...prev, ...updates }

        // Save to localStorage immediately
        saveToLocalStorage(newSettings)

        // Mark as having unsaved changes
        setHasUnsavedChanges(true)

        return newSettings
      })
    },
    [saveToLocalStorage]
  )

  // ============================================
  // Server Sync
  // ============================================

  const syncToServer = useCallback(async (): Promise<boolean> => {
    if (!isAuthenticated) {
      setError("Not authenticated")
      return false
    }

    setIsSyncing(true)
    setError(null)

    const success = await saveToServer(settings)

    setIsSyncing(false)

    if (success) {
      setHasUnsavedChanges(false)
      setLastSynced(Date.now())
      return true
    } else {
      setError("Failed to save settings")
      return false
    }
  }, [isAuthenticated, settings, saveToServer])

  // Auto-sync on change (debounced)
  useEffect(() => {
    if (!hasUnsavedChanges || !isAuthenticated) return

    const timeout = setTimeout(() => {
      syncToServer()
    }, 2000) // 2 second debounce

    return () => clearTimeout(timeout)
  }, [hasUnsavedChanges, isAuthenticated, syncToServer])

  // ============================================
  // Reset
  // ============================================

  const resetToDefaults = useCallback(() => {
    setSettings(DEFAULT_SETTINGS)
    saveToLocalStorage(DEFAULT_SETTINGS)
    setHasUnsavedChanges(true)
  }, [saveToLocalStorage])

  // ============================================
  // Context Value
  // ============================================

  const value = useMemo<SettingsContextValue>(
    () => ({
      settings,
      isLoading,
      isSyncing,
      lastSynced,
      hasUnsavedChanges,
      error,
      updateSetting,
      updateSettings,
      syncToServer,
      resetToDefaults,
    }),
    [
      settings,
      isLoading,
      isSyncing,
      lastSynced,
      hasUnsavedChanges,
      error,
      updateSetting,
      updateSettings,
      syncToServer,
      resetToDefaults,
    ]
  )

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>
}

// ============================================
// Hook
// ============================================

export function useSettings(): SettingsContextValue {
  const context = useContext(SettingsContext)
  if (!context) {
    throw new Error("useSettings must be used within SettingsProvider")
  }
  return context
}

// ============================================
// Exports
// ============================================

export { SettingsContext }
export type { SettingsContextValue }
