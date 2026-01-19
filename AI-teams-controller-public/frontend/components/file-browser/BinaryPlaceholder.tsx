"use client"

import { FileWarning } from "lucide-react"

interface BinaryPlaceholderProps {
  /** File name */
  fileName: string
  /** File size in bytes */
  size: number
  /** Optional message */
  message?: string
}

/**
 * Format file size for display
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B"

  const units = ["B", "KB", "MB", "GB"]
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${units[i]}`
}

/**
 * BinaryPlaceholder Component
 *
 * Displayed when a file cannot be shown as text (binary files, large files).
 */
export function BinaryPlaceholder({ fileName, size, message }: BinaryPlaceholderProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4 text-muted-foreground">
      <FileWarning className="h-16 w-16" />
      <div className="text-center space-y-2">
        <p className="font-medium">{message || "Cannot display binary file"}</p>
        <p className="text-sm">{fileName}</p>
        <p className="text-xs">{formatFileSize(size)}</p>
      </div>
    </div>
  )
}
