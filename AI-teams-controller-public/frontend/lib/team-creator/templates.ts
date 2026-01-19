/**
 * Team Creator Templates
 *
 * Pre-built team configurations for common workflows.
 */

import { Node, Edge } from "@xyflow/react"
import { CommunicationEdgeData, RoleNodeData } from "./types"

// ============================================
// Types
// ============================================

export interface TeamTemplate {
  id: string
  name: string
  description: string
  nodes: Node[]
  edges: Edge[]
  version: number // For migration support
}

// Current template version - increment when making breaking changes
export const TEMPLATE_VERSION = 1

// ============================================
// Template Definitions
// ============================================

/**
 * Full Stack Team - PM, SA, FE, BE, CR
 * Standard development team with all roles
 */
const fullStackTeam: TeamTemplate = {
  id: "full-stack",
  name: "Full Stack Team",
  description: "PM + SA + FE + BE + CR - Standard development team",
  version: TEMPLATE_VERSION,
  nodes: [
    {
      id: "pm-1",
      type: "default",
      position: { x: 250, y: 50 },
      data: { label: "PM" },
      style: { background: "#8b5cf6", color: "white", border: "none" },
    },
    {
      id: "sa-1",
      type: "default",
      position: { x: 450, y: 50 },
      data: { label: "SA" },
      style: { background: "#3b82f6", color: "white", border: "none" },
    },
    {
      id: "fe-1",
      type: "default",
      position: { x: 150, y: 200 },
      data: { label: "FE" },
      style: { background: "#22c55e", color: "white", border: "none" },
    },
    {
      id: "be-1",
      type: "default",
      position: { x: 350, y: 200 },
      data: { label: "BE" },
      style: { background: "#f97316", color: "white", border: "none" },
    },
    {
      id: "cr-1",
      type: "default",
      position: { x: 250, y: 350 },
      data: { label: "CR" },
      style: { background: "#ef4444", color: "white", border: "none" },
    },
  ],
  edges: [
    {
      id: "e1",
      source: "pm-1",
      target: "sa-1",
      type: "communication",
      data: { type: "bidirectional", label: "Architecture" } as CommunicationEdgeData,
    },
    {
      id: "e2",
      source: "pm-1",
      target: "fe-1",
      type: "communication",
      data: { type: "command" } as CommunicationEdgeData,
    },
    {
      id: "e3",
      source: "pm-1",
      target: "be-1",
      type: "communication",
      data: { type: "command" } as CommunicationEdgeData,
    },
    {
      id: "e4",
      source: "sa-1",
      target: "fe-1",
      type: "communication",
      data: { type: "advisory" } as CommunicationEdgeData,
    },
    {
      id: "e5",
      source: "sa-1",
      target: "be-1",
      type: "communication",
      data: { type: "advisory" } as CommunicationEdgeData,
    },
    {
      id: "e6",
      source: "fe-1",
      target: "be-1",
      type: "communication",
      data: { type: "bidirectional" } as CommunicationEdgeData,
    },
    {
      id: "e7",
      source: "fe-1",
      target: "cr-1",
      type: "communication",
      data: { type: "review" } as CommunicationEdgeData,
    },
    {
      id: "e8",
      source: "be-1",
      target: "cr-1",
      type: "communication",
      data: { type: "review" } as CommunicationEdgeData,
    },
  ],
}

/**
 * Full Team with DK - Adds Document Keeper
 */
const fullTeamWithDK: TeamTemplate = {
  id: "full-team-dk",
  name: "Full Team + DK",
  description: "PM + SA + FE + BE + CR + DK - Complete team with documentation",
  version: TEMPLATE_VERSION,
  nodes: [
    ...fullStackTeam.nodes,
    {
      id: "dk-1",
      type: "default",
      position: { x: 550, y: 200 },
      data: { label: "DK" },
      style: { background: "#06b6d4", color: "white", border: "none" },
    },
  ],
  edges: [
    ...fullStackTeam.edges,
    {
      id: "e9",
      source: "pm-1",
      target: "dk-1",
      type: "communication",
      data: { type: "command" } as CommunicationEdgeData,
    },
    {
      id: "e10",
      source: "cr-1",
      target: "dk-1",
      type: "communication",
      data: { type: "advisory" } as CommunicationEdgeData,
    },
  ],
}

/**
 * Minimal Team - PM + Implementer
 * Simple two-person team for quick tasks
 */
const minimalTeam: TeamTemplate = {
  id: "minimal",
  name: "Minimal Team",
  description: "PM + Implementer - Simple two-person team",
  version: TEMPLATE_VERSION,
  nodes: [
    {
      id: "pm-1",
      type: "default",
      position: { x: 200, y: 100 },
      data: { label: "PM" },
      style: { background: "#8b5cf6", color: "white", border: "none" },
    },
    {
      id: "fe-1",
      type: "default",
      position: { x: 200, y: 250 },
      data: { label: "FE" },
      style: { background: "#22c55e", color: "white", border: "none" },
    },
  ],
  edges: [
    {
      id: "e1",
      source: "pm-1",
      target: "fe-1",
      type: "communication",
      data: { type: "bidirectional" } as CommunicationEdgeData,
    },
  ],
}

/**
 * Backend Focus Team - PM + SA + BE + CR
 * For backend-heavy projects
 */
const backendFocusTeam: TeamTemplate = {
  id: "backend-focus",
  name: "Backend Focus",
  description: "PM + SA + BE + CR - Backend-heavy projects",
  version: TEMPLATE_VERSION,
  nodes: [
    {
      id: "pm-1",
      type: "default",
      position: { x: 250, y: 50 },
      data: { label: "PM" },
      style: { background: "#8b5cf6", color: "white", border: "none" },
    },
    {
      id: "sa-1",
      type: "default",
      position: { x: 450, y: 50 },
      data: { label: "SA" },
      style: { background: "#3b82f6", color: "white", border: "none" },
    },
    {
      id: "be-1",
      type: "default",
      position: { x: 350, y: 200 },
      data: { label: "BE" },
      style: { background: "#f97316", color: "white", border: "none" },
    },
    {
      id: "cr-1",
      type: "default",
      position: { x: 350, y: 350 },
      data: { label: "CR" },
      style: { background: "#ef4444", color: "white", border: "none" },
    },
  ],
  edges: [
    {
      id: "e1",
      source: "pm-1",
      target: "sa-1",
      type: "communication",
      data: { type: "bidirectional" } as CommunicationEdgeData,
    },
    {
      id: "e2",
      source: "pm-1",
      target: "be-1",
      type: "communication",
      data: { type: "command" } as CommunicationEdgeData,
    },
    {
      id: "e3",
      source: "sa-1",
      target: "be-1",
      type: "communication",
      data: { type: "advisory" } as CommunicationEdgeData,
    },
    {
      id: "e4",
      source: "be-1",
      target: "cr-1",
      type: "communication",
      data: { type: "review" } as CommunicationEdgeData,
    },
  ],
}

// ============================================
// Exports
// ============================================

/**
 * All available templates
 */
export const TEMPLATES: Record<string, TeamTemplate> = {
  "full-stack": fullStackTeam,
  "full-team-dk": fullTeamWithDK,
  minimal: minimalTeam,
  "backend-focus": backendFocusTeam,
}

/**
 * Default template ID
 */
export const DEFAULT_TEMPLATE_ID = "full-stack"

/**
 * Get template by ID
 */
export function getTemplate(id: string): TeamTemplate | undefined {
  return TEMPLATES[id]
}

/**
 * Get all template IDs
 */
export function getTemplateIds(): string[] {
  return Object.keys(TEMPLATES)
}

/**
 * Get all templates as array
 */
export function getAllTemplates(): TeamTemplate[] {
  return Object.values(TEMPLATES)
}
