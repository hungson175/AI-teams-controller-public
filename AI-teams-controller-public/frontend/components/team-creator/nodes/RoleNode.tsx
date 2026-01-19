"use client"

import { memo } from "react"
import { Handle, Position, NodeProps } from "@xyflow/react"
import { RoleStatus } from "@/lib/team-creator/types"

// ============================================
// Types
// ============================================

interface RoleNodeData {
  label: string
  status?: RoleStatus // "idle" | "active" | undefined
}

// ============================================
// Component
// ============================================

function RoleNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as unknown as RoleNodeData
  const status = nodeData.status

  return (
    <div
      className={`relative px-4 py-2 rounded-md min-w-[60px] text-center shadow-md transition-all ${
        selected ? "ring-2 ring-primary ring-offset-2" : ""
      }`}
    >
      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-2 h-2 !bg-muted-foreground"
      />

      {/* Label */}
      <span className="font-semibold text-sm">{nodeData.label}</span>

      {/* Status dot - only show when status is defined */}
      {status && (
        <div
          className={`absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-background ${
            status === "active"
              ? "bg-green-500 animate-pulse"
              : "bg-gray-400"
          }`}
          title={status === "active" ? "Active" : "Idle"}
        />
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="w-2 h-2 !bg-muted-foreground"
      />
    </div>
  )
}

export const RoleNode = memo(RoleNodeComponent)
