/**
 * Team Creator Storage
 *
 * localStorage helpers for saving and loading team configurations.
 * Follows best practices: save in handlers (not useEffect), include version for migrations.
 */

import { Node, Edge } from "@xyflow/react"
import { TEMPLATE_VERSION, TeamTemplate } from "./templates"

// ============================================
// Constants
// ============================================

const STORAGE_KEY = "team-creator-configs"
const CURRENT_CONFIG_KEY = "team-creator-current"

// ============================================
// Types
// ============================================

export interface SavedTeamConfig {
  id: string
  name: string
  description: string
  nodes: Node[]
  edges: Edge[]
  version: number
  createdAt: number
  updatedAt: number
}

interface StorageData {
  configs: Record<string, SavedTeamConfig>
  version: number
}

// ============================================
// Migration
// ============================================

/**
 * Check if stored data needs migration
 */
function needsMigration(data: StorageData): boolean {
  return data.version < TEMPLATE_VERSION
}

/**
 * Migrate data to current version
 */
function migrateData(data: StorageData): StorageData {
  let migrated = { ...data }

  // Version 0 -> 1: Add version field to configs
  if (data.version < 1) {
    const configs: Record<string, SavedTeamConfig> = {}
    for (const [id, config] of Object.entries(data.configs)) {
      configs[id] = {
        ...config,
        version: 1,
        createdAt: config.createdAt || Date.now(),
        updatedAt: config.updatedAt || Date.now(),
      }
    }
    migrated = { configs, version: 1 }
  }

  // Future migrations go here...
  // if (data.version < 2) { ... }

  return migrated
}

// ============================================
// Storage Operations
// ============================================

/**
 * Load all saved configurations from localStorage
 */
export function loadAllConfigs(): Record<string, SavedTeamConfig> {
  if (typeof window === "undefined") return {}

  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return {}

    const data: StorageData = JSON.parse(raw)

    // Apply migrations if needed
    if (needsMigration(data)) {
      const migrated = migrateData(data)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(migrated))
      return migrated.configs
    }

    return data.configs
  } catch (error) {
    console.error("[TeamCreator] Failed to load configs:", error)
    return {}
  }
}

/**
 * Save a team configuration to localStorage
 * Call this directly in event handlers, NOT in useEffect
 */
export function saveConfig(config: Omit<SavedTeamConfig, "createdAt" | "updatedAt" | "version">): SavedTeamConfig {
  const configs = loadAllConfigs()
  const existing = configs[config.id]

  const savedConfig: SavedTeamConfig = {
    ...config,
    version: TEMPLATE_VERSION,
    createdAt: existing?.createdAt || Date.now(),
    updatedAt: Date.now(),
  }

  configs[config.id] = savedConfig

  const data: StorageData = {
    configs,
    version: TEMPLATE_VERSION,
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  return savedConfig
}

/**
 * Delete a saved configuration
 */
export function deleteConfig(id: string): boolean {
  const configs = loadAllConfigs()
  if (!configs[id]) return false

  delete configs[id]

  const data: StorageData = {
    configs,
    version: TEMPLATE_VERSION,
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  return true
}

/**
 * Load a specific configuration by ID
 */
export function loadConfig(id: string): SavedTeamConfig | undefined {
  const configs = loadAllConfigs()
  return configs[id]
}

// ============================================
// Current Config (Working State)
// ============================================

/**
 * Save the current working configuration (unsaved changes)
 */
export function saveCurrentConfig(nodes: Node[], edges: Edge[]): void {
  if (typeof window === "undefined") return

  const data = {
    nodes,
    edges,
    updatedAt: Date.now(),
  }

  localStorage.setItem(CURRENT_CONFIG_KEY, JSON.stringify(data))
}

/**
 * Load the current working configuration
 */
export function loadCurrentConfig(): { nodes: Node[]; edges: Edge[] } | null {
  if (typeof window === "undefined") return null

  try {
    const raw = localStorage.getItem(CURRENT_CONFIG_KEY)
    if (!raw) return null

    const data = JSON.parse(raw)
    return {
      nodes: data.nodes || [],
      edges: data.edges || [],
    }
  } catch (error) {
    console.error("[TeamCreator] Failed to load current config:", error)
    return null
  }
}

/**
 * Clear the current working configuration
 */
export function clearCurrentConfig(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem(CURRENT_CONFIG_KEY)
}

// ============================================
// Import/Export
// ============================================

/**
 * Export configuration to JSON string
 */
export function exportToJson(config: SavedTeamConfig): string {
  return JSON.stringify(config, null, 2)
}

/**
 * Import configuration from JSON string
 */
export function importFromJson(json: string): SavedTeamConfig {
  const parsed = JSON.parse(json)

  // Validate structure
  if (!parsed.nodes || !Array.isArray(parsed.nodes)) {
    throw new Error("Invalid config: missing nodes array")
  }
  if (!parsed.edges || !Array.isArray(parsed.edges)) {
    throw new Error("Invalid config: missing edges array")
  }

  return {
    id: parsed.id || `imported-${Date.now()}`,
    name: parsed.name || "Imported Team",
    description: parsed.description || "",
    nodes: parsed.nodes,
    edges: parsed.edges,
    version: TEMPLATE_VERSION,
    createdAt: parsed.createdAt || Date.now(),
    updatedAt: Date.now(),
  }
}

/**
 * Download configuration as JSON file
 */
export function downloadAsJson(config: SavedTeamConfig): void {
  const json = exportToJson(config)
  const blob = new Blob([json], { type: "application/json" })
  const url = URL.createObjectURL(blob)

  const a = document.createElement("a")
  a.href = url
  a.download = `${config.name.toLowerCase().replace(/\s+/g, "-")}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/**
 * Get saved config count
 */
export function getSavedConfigCount(): number {
  const configs = loadAllConfigs()
  return Object.keys(configs).length
}
