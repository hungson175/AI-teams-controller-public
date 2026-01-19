"use client"

import { useEffect, useRef, useState, useMemo, memo, type ReactNode } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeHighlight from "rehype-highlight"
import { ScrollArea } from "@/components/ui/scroll-area"
import mermaid from "mermaid"

// Initialize mermaid once on module load
let mermaidInitialized = false
if (!mermaidInitialized) {
  mermaid.initialize({
    startOnLoad: false,
    theme: "dark",
    securityLevel: "loose",
  })
  mermaidInitialized = true
}

// Counter for stable IDs (persists across renders)
let mermaidIdCounter = 0

interface MarkdownViewerProps {
  /** Markdown content to render */
  content: string
}

interface MermaidDiagramProps {
  code: string
}

/**
 * MermaidDiagram Component
 * Renders mermaid diagrams from code blocks
 * Memoized to prevent re-renders on scroll
 */
const MermaidDiagram = memo(function MermaidDiagram({ code }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>("")
  const [error, setError] = useState<string | null>(null)
  // Use stable ID based on code hash, not random
  const idRef = useRef<string>(`mermaid-${++mermaidIdCounter}`)

  useEffect(() => {
    let isMounted = true

    const renderDiagram = async () => {
      if (!containerRef.current) return

      try {
        const { svg } = await mermaid.render(idRef.current, code)
        if (isMounted) {
          setSvg(svg)
          setError(null)
        }
      } catch (err) {
        console.error("[MermaidDiagram] Render error:", err)
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to render diagram")
        }
      }
    }

    renderDiagram()

    return () => {
      isMounted = false
    }
  }, [code])

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/30 rounded-md p-3 my-4">
        <p className="text-sm text-destructive font-medium">Mermaid diagram error:</p>
        <p className="text-xs text-muted-foreground mt-1">{error}</p>
        <pre className="text-xs mt-2 bg-muted p-2 rounded overflow-x-auto">{code}</pre>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className="my-4 flex justify-center overflow-x-auto"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
})

/**
 * Code block component - handles mermaid diagrams and regular code
 * Memoized to prevent re-renders
 */
const CodeBlock = memo(function CodeBlock({ children, className }: { children?: ReactNode; className?: string }) {
  const match = /language-(\w+)/.exec(className || "")
  const language = match ? match[1] : ""
  const codeString = String(children).replace(/\n$/, "")

  // Render mermaid diagrams
  if (language === "mermaid") {
    return <MermaidDiagram code={codeString} />
  }

  // Check if this is an inline code or block code
  const isInline = !className
  if (isInline) {
    return (
      <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono">
        {children}
      </code>
    )
  }

  return <code className="font-mono text-sm">{children}</code>
})

/**
 * Pre block component - skips wrapper for mermaid diagrams
 * Memoized to prevent re-renders
 */
const PreBlock = memo(function PreBlock({ children, node }: { children?: ReactNode; node?: { children?: Array<{ type?: string; tagName?: string; properties?: { className?: string[] } }> } }) {
  // Check if this pre contains a mermaid code block
  const codeChild = node?.children?.[0]
  if (codeChild?.type === "element" && codeChild.tagName === "code") {
    const className = codeChild.properties?.className
    if (Array.isArray(className) && className.some((c: string) => c.includes("mermaid"))) {
      // Return children directly (MermaidDiagram handles its own wrapper)
      return <>{children}</>
    }
  }
  return (
    <pre className="bg-muted p-3 rounded-md overflow-x-auto text-sm">
      {children}
    </pre>
  )
})

// Memoized table components
const TableWrapper = memo(function TableWrapper({ children }: { children?: ReactNode }) {
  return (
    <div className="overflow-x-auto my-4">
      <table className="min-w-full border-collapse border border-border">
        {children}
      </table>
    </div>
  )
})

const TableHeader = memo(function TableHeader({ children }: { children?: ReactNode }) {
  return (
    <th className="border border-border px-3 py-2 bg-muted text-left font-medium">
      {children}
    </th>
  )
})

const TableCell = memo(function TableCell({ children }: { children?: ReactNode }) {
  return (
    <td className="border border-border px-3 py-2">
      {children}
    </td>
  )
})

/**
 * MarkdownViewer Component
 *
 * Renders markdown content with proper styling.
 * Uses remark-gfm for GitHub Flavored Markdown (tables, strikethrough, autolinks, task lists)
 * Uses rehype-highlight for syntax highlighting in code blocks
 * Renders mermaid diagrams from ```mermaid code blocks
 *
 * Performance optimizations:
 * - All component renderers are memoized to prevent re-renders on scroll
 * - MermaidDiagram uses stable IDs to prevent re-rendering
 * - Components object is memoized to maintain referential equality
 */
export function MarkdownViewer({ content }: MarkdownViewerProps) {
  // Memoize components object to prevent re-renders
  const components = useMemo(() => ({
    pre: PreBlock,
    code: CodeBlock,
    table: TableWrapper,
    th: TableHeader,
    td: TableCell,
    // Style links
    a: ({ href, children }: { href?: string; children?: ReactNode }) => (
      <a
        href={href}
        className="text-primary hover:underline"
        target="_blank"
        rel="noopener noreferrer"
      >
        {children}
      </a>
    ),
    // Style headings
    h1: ({ children }: { children?: ReactNode }) => (
      <h1 className="text-2xl font-bold mt-6 mb-4 pb-2 border-b">
        {children}
      </h1>
    ),
    h2: ({ children }: { children?: ReactNode }) => (
      <h2 className="text-xl font-semibold mt-5 mb-3 pb-1 border-b">
        {children}
      </h2>
    ),
    h3: ({ children }: { children?: ReactNode }) => (
      <h3 className="text-lg font-semibold mt-4 mb-2">{children}</h3>
    ),
    h4: ({ children }: { children?: ReactNode }) => (
      <h4 className="text-base font-semibold mt-3 mb-1">{children}</h4>
    ),
    // Style blockquotes
    blockquote: ({ children }: { children?: ReactNode }) => (
      <blockquote className="border-l-4 border-muted-foreground/30 pl-4 italic my-4 text-muted-foreground">
        {children}
      </blockquote>
    ),
    // Style lists
    ul: ({ children }: { children?: ReactNode }) => (
      <ul className="list-disc list-inside my-2 space-y-1">{children}</ul>
    ),
    ol: ({ children }: { children?: ReactNode }) => (
      <ol className="list-decimal list-inside my-2 space-y-1">{children}</ol>
    ),
    // Style list items (fix nested content)
    li: ({ children }: { children?: ReactNode }) => (
      <li className="leading-relaxed">{children}</li>
    ),
    // Style horizontal rule
    hr: () => <hr className="my-6 border-border" />,
    // Style paragraphs
    p: ({ children }: { children?: ReactNode }) => (
      <p className="my-3 leading-relaxed">{children}</p>
    ),
    // Style strong/bold
    strong: ({ children }: { children?: ReactNode }) => (
      <strong className="font-semibold">{children}</strong>
    ),
    // Style emphasis/italic
    em: ({ children }: { children?: ReactNode }) => (
      <em className="italic">{children}</em>
    ),
  }), [])

  // Memoize plugins arrays
  const remarkPlugins = useMemo(() => [remarkGfm], [])
  const rehypePlugins = useMemo(() => [rehypeHighlight], [])

  return (
    <ScrollArea className="h-full">
      <div className="prose prose-sm dark:prose-invert max-w-none p-4">
        <ReactMarkdown
          remarkPlugins={remarkPlugins}
          rehypePlugins={rehypePlugins}
          components={components}
        >
          {content}
        </ReactMarkdown>
      </div>
    </ScrollArea>
  )
}
