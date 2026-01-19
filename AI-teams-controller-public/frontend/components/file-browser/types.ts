/**
 * File Browser Types
 *
 * Types matching the backend API schema from ADR-FILE-BROWSER.md
 */

/** A node in the file tree (file or directory) */
export interface FileNode {
  /** File or directory name */
  name: string
  /** Relative path from project root */
  path: string
  /** Node type */
  type: "file" | "directory"
  /** File size in bytes (null for directories) */
  size: number | null
  /** Children nodes (for directories only) */
  children?: FileNode[]
}

/** Response from GET /api/files/{team_id}/tree */
export interface TreeResponse {
  /** Absolute path to project root (for display) */
  project_root: string
  /** Tree structure */
  tree: FileNode[]
}

/** Response from GET /api/files/{team_id}/content */
export interface FileContent {
  /** Relative path to file */
  path: string
  /** File name */
  name: string
  /** File size in bytes */
  size: number
  /** MIME type */
  mime_type: string
  /** File content (null if binary or too large) */
  content: string | null
  /** Whether file is binary */
  is_binary: boolean
  /** Whether content was truncated due to size */
  is_truncated: boolean
  /** Error message if any */
  error: string | null
}

/** File browser view mode */
export type ViewMode = "monitor" | "browse" | "terminal"
