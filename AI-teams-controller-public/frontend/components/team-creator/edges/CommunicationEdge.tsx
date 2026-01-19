"use client"

import { memo, useState } from "react"
import {
  BaseEdge,
  EdgeProps,
  EdgeLabelRenderer,
  getBezierPath,
  useReactFlow,
} from "@xyflow/react"
import { X, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"
import {
  CommunicationEdgeData,
  EdgeCommunicationType,
  EDGE_TYPE_CONFIGS,
} from "@/lib/team-creator/types"

/**
 * Get marker ID based on edge type
 */
function getMarkerId(type: EdgeCommunicationType, isStart: boolean): string {
  if (isStart) {
    return "url(#arrow-reverse)"
  }
  switch (type) {
    case "bidirectional":
      return "url(#arrow-bidirectional)"
    case "advisory":
      return "url(#arrow-advisory)"
    case "review":
      return "url(#arrow-review)"
    default:
      return "url(#arrow)"
  }
}

/**
 * CommunicationEdge - Custom edge component for team communication visualization
 *
 * Features:
 * - Multiple edge types (command, bidirectional, advisory, review)
 * - Styled arrows and line patterns
 * - Hover controls for type change and deletion
 * - Optional edge labels
 */
export const CommunicationEdge = memo(function CommunicationEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}: EdgeProps) {
  const { setEdges } = useReactFlow()
  const [showControls, setShowControls] = useState(false)

  // Get edge configuration
  const edgeData = (data as CommunicationEdgeData) || { type: "command" }
  const config = EDGE_TYPE_CONFIGS[edgeData.type]

  // Calculate bezier path
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  })

  // Handle edge type change
  const handleTypeChange = (newType: EdgeCommunicationType) => {
    setEdges((edges) =>
      edges.map((edge) =>
        edge.id === id
          ? { ...edge, data: { ...edgeData, type: newType } }
          : edge
      )
    )
  }

  // Handle edge deletion
  const handleDelete = () => {
    setEdges((edges) => edges.filter((edge) => edge.id !== id))
  }

  // Toggle bidirectional
  const handleToggleBidirectional = () => {
    const newType = edgeData.type === "bidirectional" ? "command" : "bidirectional"
    handleTypeChange(newType)
  }

  return (
    <>
      {/* Edge path */}
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          ...config.style,
          cursor: "pointer",
        }}
        markerEnd={config.markerEnd ? getMarkerId(edgeData.type, false) : undefined}
        markerStart={config.markerStart ? getMarkerId(edgeData.type, true) : undefined}
      />

      {/* Edge label and controls */}
      <EdgeLabelRenderer>
        <div
          className={cn(
            "absolute pointer-events-auto nodrag nopan",
            "transform -translate-x-1/2 -translate-y-1/2"
          )}
          style={{
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
          }}
          onMouseEnter={() => setShowControls(true)}
          onMouseLeave={() => setShowControls(false)}
        >
          {/* Edge label */}
          {edgeData.label && (
            <div className="px-2 py-0.5 bg-background border rounded text-xs mb-1 text-center">
              {edgeData.label}
            </div>
          )}

          {/* Type indicator and controls (visible when selected or hovered) */}
          {(selected || showControls) && (
            <div className="flex items-center gap-1 bg-background border rounded p-1 shadow-md">
              {/* Type selector */}
              <Select
                value={edgeData.type}
                onValueChange={(v) => handleTypeChange(v as EdgeCommunicationType)}
              >
                <SelectTrigger className="h-6 w-24 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.values(EDGE_TYPE_CONFIGS).map((cfg) => (
                    <SelectItem key={cfg.type} value={cfg.type}>
                      {cfg.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Toggle bidirectional */}
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={handleToggleBidirectional}
                title="Toggle bidirectional"
              >
                <RotateCcw className="h-3 w-3" />
              </Button>

              {/* Delete button */}
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-destructive hover:text-destructive"
                onClick={handleDelete}
                title="Delete edge"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          )}
        </div>
      </EdgeLabelRenderer>
    </>
  )
})

export default CommunicationEdge
