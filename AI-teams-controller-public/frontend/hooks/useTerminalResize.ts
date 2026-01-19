import { useRef, useState, useEffect, useCallback } from "react"

/**
 * Options for the useTerminalResize hook
 */
export interface UseTerminalResizeOptions {
  /** Debounce delay in milliseconds (default: 250) */
  debounceMs?: number
}

/**
 * Return type for the useTerminalResize hook
 */
export interface UseTerminalResizeReturn {
  /** Ref to attach to the container element */
  containerRef: React.RefObject<HTMLDivElement | null>
  /** Calculated number of columns based on container width */
  columns: number
  /** Current container width in pixels */
  width: number
}

/** Minimum columns to return even for small/zero width containers */
const MIN_COLUMNS = 40

/** Default columns when width cannot be determined */
const DEFAULT_COLUMNS = 80

/**
 * Measure character width using a hidden monospace span
 */
const measureCharWidth = (element: HTMLElement): number => {
  const span = document.createElement("span")
  span.style.fontFamily = "monospace"
  span.style.fontSize = getComputedStyle(element).fontSize || "14px"
  span.style.visibility = "hidden"
  span.style.position = "absolute"
  span.style.whiteSpace = "pre"
  span.textContent = "M" // Use 'M' for accurate monospace measurement
  document.body.appendChild(span)
  const width = span.getBoundingClientRect().width
  document.body.removeChild(span)
  return width || 8 // Fallback to 8px if measurement fails
}

/**
 * Debounce utility function
 */
const debounce = <T extends (...args: unknown[]) => void>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  return (...args: Parameters<T>) => {
    if (timeoutId) clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

/**
 * Hook for tracking terminal container resize and calculating columns
 *
 * Uses ResizeObserver to track container width changes and calculates
 * the number of terminal columns based on monospace character width.
 *
 * @param options - Configuration options
 * @returns Container ref, column count, and width
 *
 * @example
 * ```tsx
 * const { containerRef, columns, width } = useTerminalResize({ debounceMs: 200 })
 *
 * return (
 *   <div ref={containerRef}>
 *     {`Terminal: ${columns} columns (${width}px)`}
 *   </div>
 * )
 * ```
 */
export function useTerminalResize(
  options: UseTerminalResizeOptions = {}
): UseTerminalResizeReturn {
  const { debounceMs = 250 } = options

  const containerRef = useRef<HTMLDivElement | null>(null)
  const [dimensions, setDimensions] = useState({ columns: DEFAULT_COLUMNS, width: 0 })

  // Calculate columns from width
  const calculateColumns = useCallback((element: HTMLElement, newWidth: number): number => {
    if (newWidth <= 0) {
      return MIN_COLUMNS
    }

    const charWidth = measureCharWidth(element)
    const columns = Math.floor(newWidth / charWidth)

    return Math.max(columns, MIN_COLUMNS)
  }, [])

  useEffect(() => {
    const element = containerRef.current
    if (!element) return

    // Create debounced update function
    const debouncedUpdate = debounce((width: number) => {
      const columns = calculateColumns(element, width)
      setDimensions({ columns, width })
    }, debounceMs)

    // Create ResizeObserver
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const width = entry.contentRect.width
        debouncedUpdate(width)
      }
    })

    // Start observing
    resizeObserver.observe(element)

    // Initial measurement
    const initialWidth = element.getBoundingClientRect().width
    if (initialWidth > 0) {
      const columns = calculateColumns(element, initialWidth)
      setDimensions({ columns, width: initialWidth })
    }

    // Cleanup
    return () => {
      resizeObserver.disconnect()
    }
  }, [calculateColumns, debounceMs])

  return {
    containerRef,
    columns: dimensions.columns,
    width: dimensions.width,
  }
}
