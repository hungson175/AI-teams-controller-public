"use client"

import { Skeleton } from "@/components/ui/skeleton"

interface FileTreeSkeletonProps {
  /** Number of skeleton items to show */
  itemCount?: number
}

/**
 * FileTreeSkeleton Component
 *
 * Skeleton loader for the file tree while loading.
 */
export function FileTreeSkeleton({ itemCount = 8 }: FileTreeSkeletonProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header skeleton */}
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-6 w-6 rounded" />
      </div>

      {/* Tree items skeleton */}
      <div className="py-2 space-y-1 px-2">
        {Array.from({ length: itemCount }).map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-2 px-2 py-1"
            style={{ paddingLeft: `${(i % 3) * 16 + 8}px` }}
          >
            {/* Chevron placeholder */}
            <Skeleton className="h-4 w-4 shrink-0" />
            {/* Icon placeholder */}
            <Skeleton className="h-4 w-4 shrink-0" />
            {/* Name placeholder - varying widths */}
            <Skeleton
              className="h-4"
              style={{ width: `${60 + (i * 17) % 80}px` }}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
