"use client"

/**
 * SVG marker definitions for edge arrows
 * Must be rendered once inside ReactFlow container
 */
export function EdgeMarkers() {
  return (
    <svg style={{ position: "absolute", width: 0, height: 0 }}>
      <defs>
        {/* Forward arrow - command (slate) */}
        <marker
          id="arrow"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path
            d="M 0 0 L 10 5 L 0 10 z"
            fill="#64748b"
            className="react-flow__edge-marker"
          />
        </marker>

        {/* Reverse arrow (for bidirectional - violet) */}
        <marker
          id="arrow-reverse"
          viewBox="0 0 10 10"
          refX="2"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path
            d="M 10 0 L 0 5 L 10 10 z"
            fill="#8b5cf6"
            className="react-flow__edge-marker"
          />
        </marker>

        {/* Advisory arrow (blue) */}
        <marker
          id="arrow-advisory"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path
            d="M 0 0 L 10 5 L 0 10 z"
            fill="#3b82f6"
            className="react-flow__edge-marker"
          />
        </marker>

        {/* Review arrow (red) */}
        <marker
          id="arrow-review"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path
            d="M 0 0 L 10 5 L 0 10 z"
            fill="#ef4444"
            className="react-flow__edge-marker"
          />
        </marker>

        {/* Bidirectional forward arrow (violet) */}
        <marker
          id="arrow-bidirectional"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path
            d="M 0 0 L 10 5 L 0 10 z"
            fill="#8b5cf6"
            className="react-flow__edge-marker"
          />
        </marker>
      </defs>
    </svg>
  )
}
