"use client"

import { useEffect, useState } from "react"
import Editor from "@monaco-editor/react"
import { Loader2 } from "lucide-react"

interface CodeViewerProps {
  /** File content to display */
  content: string
  /** File name (used to detect language) */
  fileName: string
}

/** Map file extensions to Monaco language IDs */
function getLanguageFromFileName(fileName: string): string {
  const ext = fileName.split(".").pop()?.toLowerCase() || ""

  const languageMap: Record<string, string> = {
    // JavaScript/TypeScript
    js: "javascript",
    jsx: "javascript",
    ts: "typescript",
    tsx: "typescript",
    mjs: "javascript",
    cjs: "javascript",

    // Web
    html: "html",
    htm: "html",
    css: "css",
    scss: "scss",
    less: "less",

    // Data
    json: "json",
    yaml: "yaml",
    yml: "yaml",
    xml: "xml",
    toml: "ini",

    // Programming
    py: "python",
    rb: "ruby",
    go: "go",
    rs: "rust",
    java: "java",
    kt: "kotlin",
    scala: "scala",
    c: "c",
    cpp: "cpp",
    h: "c",
    hpp: "cpp",
    cs: "csharp",
    php: "php",
    swift: "swift",

    // Shell
    sh: "shell",
    bash: "shell",
    zsh: "shell",
    fish: "shell",
    ps1: "powershell",

    // Config
    dockerfile: "dockerfile",
    makefile: "makefile",
    gitignore: "plaintext",
    env: "plaintext",

    // Docs
    md: "markdown",
    mdx: "markdown",
    txt: "plaintext",
    log: "plaintext",

    // SQL
    sql: "sql",
  }

  // Handle special file names
  const lowerFileName = fileName.toLowerCase()
  if (lowerFileName === "dockerfile") return "dockerfile"
  if (lowerFileName === "makefile") return "makefile"
  if (lowerFileName.startsWith(".env")) return "plaintext"

  return languageMap[ext] || "plaintext"
}

/**
 * CodeViewer Component
 *
 * Displays code with syntax highlighting using Monaco editor.
 * Read-only mode with automatic language detection.
 */
export function CodeViewer({ content, fileName }: CodeViewerProps) {
  const [mounted, setMounted] = useState(false)
  const language = getLanguageFromFileName(fileName)

  // Avoid SSR issues with Monaco
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <Editor
      height="100%"
      language={language}
      value={content}
      theme="vs-dark"
      options={{
        readOnly: true,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        fontSize: 13,
        lineNumbers: "on",
        wordWrap: "on",
        folding: true,
        renderLineHighlight: "none",
        selectionHighlight: true,
        occurrencesHighlight: "off",
        cursorStyle: "line-thin",
        scrollbar: {
          vertical: "auto",
          horizontal: "auto",
        },
      }}
      loading={
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      }
    />
  )
}
