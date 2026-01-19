"use client"

import { useMemo } from "react"
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  BackgroundVariant,
  Position,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"

// Role definitions with colors
const ROLES = [
  { id: "boss", label: "Boss", color: "#fbbf24" },    // Amber
  { id: "pm", label: "PM", color: "#8b5cf6" },        // Purple
  { id: "sa", label: "SA", color: "#3b82f6" },        // Blue
  { id: "be", label: "BE", color: "#f97316" },        // Orange
  { id: "fe", label: "FE", color: "#22c55e" },        // Green
  { id: "cr", label: "CR", color: "#ef4444" },        // Red
  { id: "dk", label: "DK", color: "#6b7280" },        // Gray
] as const

// Step definitions - which roles are active at each step
const STEPS = [
  { step: 1, name: "Ideas", active: ["boss", "pm"], description: "Boss -> PM (idea)" },
  { step: 2, name: "Architecture", active: ["pm", "sa"], description: "PM -> SA (design)" },
  { step: 3, name: "ADR", active: ["sa", "pm"], description: "SA -> PM (ADR finalized)" },
  { step: 4, name: "Assignment", active: ["pm", "be", "fe"], description: "PM -> BE/FE (sprint)" },
  { step: 5, name: "Implementation", active: ["be", "fe"], description: "BE/FE work" },
  { step: 6, name: "Clarify (1)", active: ["be", "fe", "pm"], description: "BE/FE -> PM (questions)" },
  { step: 7, name: "Clarify (2)", active: ["pm", "sa"], description: "PM <-> SA (answers)" },
  { step: 8, name: "Completion", active: ["be", "fe", "pm"], description: "BE/FE -> PM (done)" },
  { step: 9, name: "Review Req", active: ["pm", "cr"], description: "PM -> CR (review)" },
  { step: 10, name: "Code Review", active: ["cr", "be", "fe"], description: "CR reviews + feedback" },
] as const

// Edge definitions - flows between steps
const FLOW_EDGES = [
  // Step 1: Boss -> PM
  { source: "boss-1", target: "pm-1", label: "idea" },
  // Step 2: PM -> SA
  { source: "pm-1", target: "pm-2" },
  { source: "pm-2", target: "sa-2", label: "design" },
  // Step 3: SA -> PM
  { source: "sa-2", target: "sa-3" },
  { source: "sa-3", target: "pm-3", label: "ADR" },
  // Step 4: PM -> BE/FE
  { source: "pm-3", target: "pm-4" },
  { source: "pm-4", target: "be-4", label: "assign" },
  { source: "pm-4", target: "fe-4" },
  // Step 5: BE/FE implementation
  { source: "be-4", target: "be-5" },
  { source: "fe-4", target: "fe-5" },
  // Step 6: BE/FE -> PM questions
  { source: "be-5", target: "be-6" },
  { source: "fe-5", target: "fe-6" },
  { source: "be-6", target: "pm-6", label: "?" },
  { source: "fe-6", target: "pm-6" },
  // Step 7: PM <-> SA clarify
  { source: "pm-6", target: "pm-7" },
  { source: "pm-7", target: "sa-7", label: "?" },
  { source: "sa-7", target: "pm-7", animated: true },
  // Step 8: BE/FE -> PM completion
  { source: "be-6", target: "be-8" },
  { source: "fe-6", target: "fe-8" },
  { source: "be-8", target: "pm-8", label: "done" },
  { source: "fe-8", target: "pm-8" },
  // Step 9: PM -> CR
  { source: "pm-8", target: "pm-9" },
  { source: "pm-9", target: "cr-9", label: "review" },
  // Step 10: CR reviews, feedback to BE/FE
  { source: "cr-9", target: "cr-10" },
  { source: "cr-10", target: "be-10", animated: true },
  { source: "cr-10", target: "fe-10", animated: true },
]

// Layout constants
const NODE_WIDTH = 60
const NODE_HEIGHT = 40
const COL_SPACING = 100
const ROW_SPACING = 70
const HEADER_HEIGHT = 40
const LEFT_MARGIN = 80

export function WorkflowMatrix() {
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = []
    const edges: Edge[] = []

    // Create step header nodes (column labels)
    STEPS.forEach((step, colIdx) => {
      nodes.push({
        id: `step-header-${step.step}`,
        type: "default",
        position: { x: LEFT_MARGIN + colIdx * COL_SPACING, y: 0 },
        data: { label: `Step ${step.step}` },
        style: {
          background: "#374151",
          color: "#9ca3af",
          border: "none",
          fontSize: "10px",
          width: NODE_WIDTH,
          height: 25,
          borderRadius: 4,
        },
        draggable: false,
        selectable: false,
      })

      // Step name below header
      nodes.push({
        id: `step-name-${step.step}`,
        type: "default",
        position: { x: LEFT_MARGIN + colIdx * COL_SPACING, y: 28 },
        data: { label: step.name },
        style: {
          background: "transparent",
          color: "#6b7280",
          border: "none",
          fontSize: "9px",
          width: NODE_WIDTH,
          height: 15,
        },
        draggable: false,
        selectable: false,
      })
    })

    // Create role label nodes (row labels)
    ROLES.forEach((role, rowIdx) => {
      nodes.push({
        id: `role-label-${role.id}`,
        type: "default",
        position: { x: 0, y: HEADER_HEIGHT + 15 + rowIdx * ROW_SPACING },
        data: { label: role.label },
        style: {
          background: role.color,
          color: "white",
          border: "none",
          fontSize: "11px",
          fontWeight: "bold",
          width: 50,
          height: 30,
          borderRadius: 6,
        },
        draggable: false,
        selectable: false,
        sourcePosition: Position.Right,
      })
    })

    // Create matrix cells - nodes for active roles at each step
    STEPS.forEach((step, colIdx) => {
      ROLES.forEach((role, rowIdx) => {
        const isActive = step.active.includes(role.id as typeof step.active[number])
        const nodeId = `${role.id}-${step.step}`

        nodes.push({
          id: nodeId,
          type: "default",
          position: {
            x: LEFT_MARGIN + colIdx * COL_SPACING,
            y: HEADER_HEIGHT + 15 + rowIdx * ROW_SPACING,
          },
          data: { label: isActive ? role.label : "" },
          style: {
            background: isActive ? role.color : "#1f2937",
            color: isActive ? "white" : "#374151",
            border: isActive ? `2px solid ${role.color}` : "1px dashed #374151",
            fontSize: "10px",
            fontWeight: isActive ? "bold" : "normal",
            width: NODE_WIDTH,
            height: 30,
            borderRadius: 6,
            opacity: isActive ? 1 : 0.3,
          },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
        })
      })
    })

    // Create edges for flow
    FLOW_EDGES.forEach((edge, idx) => {
      edges.push({
        id: `flow-${idx}`,
        source: edge.source,
        target: edge.target,
        animated: edge.animated || false,
        label: edge.label,
        labelStyle: { fontSize: 8, fill: "#9ca3af" },
        labelBgStyle: { fill: "#111827", fillOpacity: 0.8 },
        style: {
          stroke: "#4b5563",
          strokeWidth: edge.animated ? 2 : 1,
        },
        type: "smoothstep",
      })
    })

    return { nodes, edges }
  }, [])

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        attributionPosition="bottom-left"
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        panOnDrag={true}
        zoomOnScroll={true}
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#374151" />
        <Controls showInteractive={false} />
      </ReactFlow>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-card/90 backdrop-blur-sm border border-border rounded-lg p-3 text-xs">
        <div className="font-semibold mb-2 text-foreground">10-Step Workflow</div>
        <div className="space-y-1 text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#fbbf24]" />
            <span>Boss - Project owner</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#8b5cf6]" />
            <span>PM - Coordinator hub</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#3b82f6]" />
            <span>SA - Architecture</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#f97316]" />
            <span>BE - Backend</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#22c55e]" />
            <span>FE - Frontend</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#ef4444]" />
            <span>CR - Code Review</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-border">
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-[#4b5563]" />
            <span>Normal flow</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-[#4b5563] animate-pulse" />
            <span>Bidirectional</span>
          </div>
        </div>
      </div>
    </div>
  )
}
