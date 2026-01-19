"use client"

import {
  File,
  FileCode,
  FileJson,
  FileText,
  FileType,
  Image,
  Settings,
  Database,
  FileArchive,
  Film,
  Music,
  Lock,
  Braces,
} from "lucide-react"
import { cn } from "@/lib/utils"

export interface FileIconConfig {
  icon: React.ComponentType<{ className?: string }>
  colorClass: string
}

/** Get icon configuration for a file based on its name/extension */
export function getFileIcon(fileName: string): FileIconConfig {
  const ext = fileName.split(".").pop()?.toLowerCase() || ""
  const lowerName = fileName.toLowerCase()

  // TypeScript/JavaScript - Blue/Yellow
  if (["ts", "tsx"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-blue-500" }
  }
  if (["js", "jsx", "mjs", "cjs"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-yellow-500" }
  }

  // Python - Green
  if (["py", "pyw", "pyi"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-green-500" }
  }

  // Markdown - Purple
  if (["md", "mdx", "markdown"].includes(ext)) {
    return { icon: FileText, colorClass: "text-purple-500" }
  }

  // JSON/YAML/Config - Orange
  if (["json", "yaml", "yml", "toml"].includes(ext)) {
    return { icon: FileJson, colorClass: "text-orange-500" }
  }

  // Config files - Gray
  if (
    lowerName.startsWith(".") ||
    ["config", "conf", "ini", "env", "gitignore", "dockerignore", "eslintrc", "prettierrc"].some(
      (c) => lowerName.includes(c)
    ) ||
    ["lock", "cfg"].includes(ext)
  ) {
    return { icon: Settings, colorClass: "text-muted-foreground" }
  }

  // HTML/CSS/SCSS - Orange/Pink
  if (["html", "htm"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-orange-600" }
  }
  if (["css", "scss", "sass", "less"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-pink-500" }
  }

  // Shell scripts - Green
  if (["sh", "bash", "zsh", "fish", "ps1"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-green-600" }
  }

  // Go - Cyan
  if (ext === "go") {
    return { icon: FileCode, colorClass: "text-cyan-500" }
  }

  // Rust - Orange
  if (ext === "rs") {
    return { icon: FileCode, colorClass: "text-orange-700" }
  }

  // Java/Kotlin - Red/Purple
  if (ext === "java") {
    return { icon: FileCode, colorClass: "text-red-500" }
  }
  if (["kt", "kts"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-purple-600" }
  }

  // C/C++ - Blue
  if (["c", "h"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-blue-600" }
  }
  if (["cpp", "hpp", "cc", "cxx"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-blue-700" }
  }

  // Ruby - Red
  if (["rb", "rake", "gemspec"].includes(ext)) {
    return { icon: FileCode, colorClass: "text-red-600" }
  }

  // PHP - Indigo
  if (ext === "php") {
    return { icon: FileCode, colorClass: "text-indigo-500" }
  }

  // SQL - Blue
  if (ext === "sql") {
    return { icon: Database, colorClass: "text-blue-400" }
  }

  // GraphQL - Pink
  if (["graphql", "gql"].includes(ext)) {
    return { icon: Braces, colorClass: "text-pink-600" }
  }

  // Images - Red (blocked)
  if (["png", "jpg", "jpeg", "gif", "svg", "ico", "webp", "bmp", "tiff"].includes(ext)) {
    return { icon: Image, colorClass: "text-red-400" }
  }

  // Video - Red (blocked)
  if (["mp4", "mov", "avi", "mkv", "webm"].includes(ext)) {
    return { icon: Film, colorClass: "text-red-400" }
  }

  // Audio - Red (blocked)
  if (["mp3", "wav", "ogg", "flac", "m4a"].includes(ext)) {
    return { icon: Music, colorClass: "text-red-400" }
  }

  // Archives - Red (blocked)
  if (["zip", "tar", "gz", "rar", "7z", "bz2"].includes(ext)) {
    return { icon: FileArchive, colorClass: "text-red-400" }
  }

  // Binary/Executables - Red (blocked)
  if (["exe", "dll", "so", "dylib", "bin", "o", "a"].includes(ext)) {
    return { icon: Lock, colorClass: "text-red-400" }
  }

  // Fonts - Gray
  if (["woff", "woff2", "ttf", "otf", "eot"].includes(ext)) {
    return { icon: FileType, colorClass: "text-muted-foreground" }
  }

  // Default - Muted
  return { icon: File, colorClass: "text-muted-foreground" }
}

interface FileIconProps {
  fileName: string
  className?: string
}

/** Render a file icon with appropriate color based on file type */
export function FileIcon({ fileName, className }: FileIconProps) {
  const { icon: Icon, colorClass } = getFileIcon(fileName)
  return <Icon className={cn("h-4 w-4 shrink-0", colorClass, className)} />
}
