"use client"

import { useCallback, useMemo } from "react"
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  Connection,
  Node,
  Edge,
  BackgroundVariant,
  OnNodesChange,
  OnEdgesChange,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import { edgeTypes, EdgeMarkers } from "./edges"
import { nodeTypes } from "./nodes"
import { CommunicationEdgeData, TeamCreatorMode, RoleStatus } from "@/lib/team-creator/types"

// ============================================
// Types
// ============================================

interface RoleStatusMap {
  [roleId: string]: RoleStatus
}

// ============================================
// Props
// ============================================

interface TeamFlowCanvasProps {
  nodes: Node[]
  edges: Edge[]
  onNodesChange: OnNodesChange<Node>
  onEdgesChange: OnEdgesChange<Edge>
  setEdges: React.Dispatch<React.SetStateAction<Edge[]>>
  // Sprint 32: Monitor mode props
  mode?: TeamCreatorMode
  statusMap?: RoleStatusMap
}

export function TeamFlowCanvas({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  setEdges,
  mode = "design",
  statusMap = {},
}: TeamFlowCanvasProps) {
  // Transform nodes for Monitor mode - use custom RoleNode type and inject status
  const displayNodes = useMemo(() => {
    if (mode === "design") {
      return nodes
    }

    // Monitor mode: Transform to role nodes with status
    return nodes.map((node) => ({
      ...node,
      type: "role",
      data: {
        ...node.data,
        status: statusMap[node.id],
      },
    }))
  }, [nodes, mode, statusMap])

  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge: Edge = {
        ...params,
        id: `e-${Date.now()}`,
        type: "communication",
        data: { type: "command" } as CommunicationEdgeData,
      }
      setEdges((eds) => addEdge(newEdge, eds))
    },
    [setEdges]
  )

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={displayNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        defaultEdgeOptions={{
          type: "communication",
          data: { type: "command" },
        }}
        fitView
        attributionPosition="bottom-left"
      >
        <EdgeMarkers />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <Controls />
        <MiniMap
          nodeStrokeWidth={3}
          zoomable
          pannable
        />
      </ReactFlow>
    </div>
  )
}
