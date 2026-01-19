/**
 * Team Creator TypeScript Types
 *
 * Types for the team creation canvas, role nodes, and drag-drop functionality.
 */

// ============================================
// Role Types
// ============================================

/**
 * Available role types for team members
 */
export type RoleType = "PM" | "SA" | "BE" | "FE" | "CR" | "DK"

/**
 * Role activity status
 */
export type RoleStatus = "idle" | "active"

/**
 * Team Creator mode
 */
export type TeamCreatorMode = "design" | "monitor"

/**
 * Monitor connection status
 */
export type MonitorConnectionStatus = "disconnected" | "connecting" | "connected" | "error"

/**
 * Node visual status for monitor mode
 * - idle: Gray dot
 * - active: Green pulsing dot
 * - unmapped: Orange warning dot (no paneId)
 * - unknown: No status (design mode)
 */
export type NodeVisualStatus = "idle" | "active" | "unmapped" | "unknown"

/**
 * Role configuration with display properties
 */
export interface RoleConfig {
  type: RoleType
  label: string
  description: string
  color: string // Tailwind color class or hex
}

/**
 * Role configurations for all team members
 */
export const ROLE_CONFIGS: Record<RoleType, RoleConfig> = {
  PM: {
    type: "PM",
    label: "Project Manager",
    description: "Coordinates team and manages sprints",
    color: "#8b5cf6", // violet-500
  },
  SA: {
    type: "SA",
    label: "Solution Architect",
    description: "Designs system architecture",
    color: "#3b82f6", // blue-500
  },
  BE: {
    type: "BE",
    label: "Backend Engineer",
    description: "Implements backend services",
    color: "#f97316", // orange-500
  },
  FE: {
    type: "FE",
    label: "Frontend Engineer",
    description: "Builds user interfaces",
    color: "#22c55e", // green-500
  },
  CR: {
    type: "CR",
    label: "Code Reviewer",
    description: "Reviews code quality",
    color: "#ef4444", // red-500
  },
  DK: {
    type: "DK",
    label: "Document Keeper",
    description: "Maintains documentation",
    color: "#06b6d4", // cyan-500
  },
}

// ============================================
// React Flow Node Types
// ============================================

/**
 * Data payload for RoleNode custom node
 */
export interface RoleNodeData {
  role: RoleType
  label: string
  status: RoleStatus
  paneId?: string // Optional tmux pane ID for real integration
}

/**
 * Get role configuration by type
 */
export function getRoleConfig(role: RoleType): RoleConfig {
  return ROLE_CONFIGS[role]
}

/**
 * Get all role types
 */
export function getAllRoleTypes(): RoleType[] {
  return Object.keys(ROLE_CONFIGS) as RoleType[]
}

// ============================================
// Edge Types (S3)
// ============================================

/**
 * Edge communication types
 */
export type EdgeCommunicationType = "command" | "bidirectional" | "advisory" | "review"

/**
 * Edge data payload for CommunicationEdge
 */
export interface CommunicationEdgeData {
  type: EdgeCommunicationType
  label?: string
  animated?: boolean
}

/**
 * Edge configuration with display properties
 */
export interface EdgeTypeConfig {
  type: EdgeCommunicationType
  label: string
  description: string
  style: {
    stroke: string
    strokeWidth: number
    strokeDasharray?: string
  }
  markerEnd: boolean
  markerStart: boolean // For bidirectional
}

/**
 * Edge type configurations
 */
export const EDGE_TYPE_CONFIGS: Record<EdgeCommunicationType, EdgeTypeConfig> = {
  command: {
    type: "command",
    label: "Command",
    description: "Task delegation and direct orders",
    style: { stroke: "#64748b", strokeWidth: 2 }, // slate-500
    markerEnd: true,
    markerStart: false,
  },
  bidirectional: {
    type: "bidirectional",
    label: "Bidirectional",
    description: "Two-way communication and discussion",
    style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, // violet-500
    markerEnd: true,
    markerStart: true,
  },
  advisory: {
    type: "advisory",
    label: "Advisory",
    description: "Guidance and recommendations",
    style: { stroke: "#3b82f6", strokeWidth: 2, strokeDasharray: "5,5" }, // blue-500
    markerEnd: true,
    markerStart: false,
  },
  review: {
    type: "review",
    label: "Review",
    description: "Code review requests",
    style: { stroke: "#ef4444", strokeWidth: 2, strokeDasharray: "2,2" }, // red-500
    markerEnd: true,
    markerStart: false,
  },
}

/**
 * Get edge configuration by type
 */
export function getEdgeConfig(type: EdgeCommunicationType): EdgeTypeConfig {
  return EDGE_TYPE_CONFIGS[type]
}

/**
 * Get all edge types
 */
export function getAllEdgeTypes(): EdgeCommunicationType[] {
  return Object.keys(EDGE_TYPE_CONFIGS) as EdgeCommunicationType[]
}
