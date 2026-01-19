"use client"

import { useEffect, useRef } from "react"
import { EditorState } from "@codemirror/state"
import { EditorView, keymap } from "@codemirror/view"
import { defaultKeymap } from "@codemirror/commands"
import { javascript } from "@codemirror/lang-javascript"
import { python } from "@codemirror/lang-python"
import { go } from "@codemirror/lang-go"
import { rust } from "@codemirror/lang-rust"
import { java } from "@codemirror/lang-java"
import { css } from "@codemirror/lang-css"
import { html } from "@codemirror/lang-html"
import { markdown } from "@codemirror/lang-markdown"
import { json } from "@codemirror/lang-json"
import { yaml } from "@codemirror/lang-yaml"
import { oneDark } from "@codemirror/theme-one-dark"

interface CodeEditorProps {
  /** Initial value of the editor */
  value: string
  /** Callback when content changes */
  onChange: (value: string) => void
  /** Filename for language detection */
  fileName: string
  /** Additional CSS classes */
  className?: string
}

/**
 * Get CodeMirror language extension based on file extension
 */
function getLanguageExtension(fileName: string) {
  const ext = fileName.split(".").pop()?.toLowerCase() || ""

  switch (ext) {
    // Work Item #1: JavaScript, TypeScript, Python
    case "js":
    case "jsx":
      return javascript({ jsx: true })
    case "ts":
    case "tsx":
      return javascript({ typescript: true, jsx: true })
    case "py":
      return python()

    // Work Item #2: Go, Rust, Java, CSS
    case "go":
      return go()
    case "rs":
      return rust()
    case "java":
      return java()
    case "css":
      return css()

    // Work Item #3: HTML, Markdown, JSON, YAML
    case "html":
      return html()
    case "md":
    case "mdx":
    case "markdown":
      return markdown()
    case "json":
      return json()
    case "yaml":
    case "yml":
      return yaml()

    default:
      return null // Plain text for unsupported types
  }
}

/**
 * CodeEditor Component (Sprint 13)
 *
 * Professional code editor with syntax highlighting using CodeMirror 6.
 * Supports JavaScript, TypeScript, and Python in Work Item #1.
 */
export function CodeEditor({ value, onChange, fileName, className = "" }: CodeEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null)
  const viewRef = useRef<EditorView | null>(null)

  useEffect(() => {
    if (!editorRef.current) return

    const languageExtension = getLanguageExtension(fileName)
    const extensions = [
      keymap.of(defaultKeymap),
      oneDark,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          const newValue = update.state.doc.toString()
          onChange(newValue)
        }
      }),
    ]

    // Add language support if available
    if (languageExtension) {
      extensions.push(languageExtension)
    }

    const startState = EditorState.create({
      doc: value,
      extensions,
    })

    const view = new EditorView({
      state: startState,
      parent: editorRef.current,
    })

    viewRef.current = view

    return () => {
      view.destroy()
      viewRef.current = null
    }
  }, [fileName]) // Re-create editor when fileName changes (language detection)

  // Update editor content when value prop changes externally
  useEffect(() => {
    if (viewRef.current) {
      const currentValue = viewRef.current.state.doc.toString()
      if (currentValue !== value) {
        viewRef.current.dispatch({
          changes: {
            from: 0,
            to: currentValue.length,
            insert: value,
          },
        })
      }
    }
  }, [value])

  return (
    <div
      ref={editorRef}
      className={`w-full h-full overflow-auto ${className}`}
      data-testid="code-editor"
    />
  )
}
