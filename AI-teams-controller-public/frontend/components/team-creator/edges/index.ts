/**
 * Edge component exports and registry
 */

export { CommunicationEdge } from "./CommunicationEdge"
export { EdgeMarkers } from "./EdgeMarkers"

import { EdgeTypes } from "@xyflow/react"
import { CommunicationEdge } from "./CommunicationEdge"

/**
 * Custom edge types for React Flow
 */
export const edgeTypes: EdgeTypes = {
  communication: CommunicationEdge,
}
