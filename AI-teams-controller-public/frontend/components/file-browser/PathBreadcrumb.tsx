"use client"

import { Home } from "lucide-react"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbEllipsis,
} from "@/components/ui/breadcrumb"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface PathBreadcrumbProps {
  /** Full file path relative to project root */
  filePath: string
  /** Project root name to display as first segment */
  projectName: string
  /** Callback when a path segment is clicked */
  onNavigate: (path: string) => void
  /** Maximum segments to show before truncating */
  maxSegments?: number
}

/**
 * PathBreadcrumb Component
 *
 * Displays a clickable breadcrumb path for file navigation.
 * Truncates middle segments on narrow screens.
 */
export function PathBreadcrumb({
  filePath,
  projectName,
  onNavigate,
  maxSegments = 4,
}: PathBreadcrumbProps) {
  const segments = filePath.split("/").filter(Boolean)

  // Build cumulative paths for each segment
  const pathSegments = segments.map((name, index) => ({
    name,
    path: segments.slice(0, index + 1).join("/"),
  }))

  // Determine if we need to truncate
  const shouldTruncate = pathSegments.length > maxSegments
  const visibleStart = shouldTruncate ? 1 : pathSegments.length // Show first segment
  const hiddenSegments = shouldTruncate
    ? pathSegments.slice(1, pathSegments.length - (maxSegments - 2))
    : []
  const visibleEnd = shouldTruncate
    ? pathSegments.slice(pathSegments.length - (maxSegments - 2))
    : pathSegments

  return (
    <Breadcrumb>
      <BreadcrumbList className="flex-nowrap">
        {/* Project root */}
        <BreadcrumbItem>
          <BreadcrumbLink
            href="#"
            onClick={(e) => {
              e.preventDefault()
              onNavigate("")
            }}
            className="flex items-center gap-1 text-xs"
          >
            <Home className="h-3 w-3" />
            <span className="hidden sm:inline">{projectName}</span>
          </BreadcrumbLink>
        </BreadcrumbItem>

        {pathSegments.length > 0 && <BreadcrumbSeparator />}

        {/* Truncated segments with dropdown */}
        {shouldTruncate && (
          <>
            {/* First visible segment */}
            <BreadcrumbItem>
              <BreadcrumbLink
                href="#"
                onClick={(e) => {
                  e.preventDefault()
                  onNavigate(pathSegments[0].path)
                }}
                className="text-xs"
              >
                {pathSegments[0].name}
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />

            {/* Ellipsis with dropdown for hidden segments */}
            <BreadcrumbItem>
              <DropdownMenu>
                <DropdownMenuTrigger className="flex items-center gap-1">
                  <BreadcrumbEllipsis className="h-4 w-4" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  {hiddenSegments.map((segment) => (
                    <DropdownMenuItem
                      key={segment.path}
                      onClick={() => onNavigate(segment.path)}
                    >
                      {segment.name}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </BreadcrumbItem>
            <BreadcrumbSeparator />

            {/* Visible end segments */}
            {visibleEnd.map((segment, index) => (
              <BreadcrumbItem key={segment.path}>
                {index > 0 && <BreadcrumbSeparator />}
                {index === visibleEnd.length - 1 ? (
                  <BreadcrumbPage className="text-xs font-medium truncate max-w-[150px]">
                    {segment.name}
                  </BreadcrumbPage>
                ) : (
                  <BreadcrumbLink
                    href="#"
                    onClick={(e) => {
                      e.preventDefault()
                      onNavigate(segment.path)
                    }}
                    className="text-xs"
                  >
                    {segment.name}
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            ))}
          </>
        )}

        {/* Non-truncated segments */}
        {!shouldTruncate &&
          pathSegments.map((segment, index) => (
            <BreadcrumbItem key={segment.path}>
              {index > 0 && <BreadcrumbSeparator />}
              {index === pathSegments.length - 1 ? (
                <BreadcrumbPage className="text-xs font-medium truncate max-w-[150px]">
                  {segment.name}
                </BreadcrumbPage>
              ) : (
                <BreadcrumbLink
                  href="#"
                  onClick={(e) => {
                    e.preventDefault()
                    onNavigate(segment.path)
                  }}
                  className="text-xs"
                >
                  {segment.name}
                </BreadcrumbLink>
              )}
            </BreadcrumbItem>
          ))}
      </BreadcrumbList>
    </Breadcrumb>
  )
}
