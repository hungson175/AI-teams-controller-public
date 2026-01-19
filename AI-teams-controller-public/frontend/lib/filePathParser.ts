/**
 * File Path Parser (Sprint 13 - Work Item #4)
 *
 * Detects and parses file paths in terminal output for clickable links
 */

export interface FilePath {
  /** The file path without line/column numbers */
  path: string
  /** Line number if present (e.g., file.ts:123) */
  lineNumber?: number
  /** Column number if present (e.g., file.ts:123:45) */
  columnNumber?: number
  /** Start index in original text */
  startIndex: number
  /** End index in original text */
  endIndex: number
  /** Full matched text (including line:col) */
  fullMatch: string
}

/**
 * Common code file extensions to detect
 */
const CODE_EXTENSIONS = [
  "ts", "tsx", "js", "jsx",      // JavaScript/TypeScript
  "py",                          // Python
  "go",                          // Go
  "rs",                          // Rust
  "java",                        // Java
  "css", "scss", "sass",         // CSS
  "html", "htm",                 // HTML
  "json",                        // JSON
  "yaml", "yml",                 // YAML
  "md", "mdx", "markdown",       // Markdown
  "sh", "bash",                  // Shell
  "sql",                         // SQL
  "c", "cpp", "h", "hpp",        // C/C++
  "rb",                          // Ruby
  "php",                         // PHP
  "swift",                       // Swift
  "kt", "kts",                   // Kotlin
]

/**
 * Regex pattern to detect file paths
 *
 * Matches:
 * - Absolute paths: /path/to/file.ext
 * - Relative paths: ./file.ext, ../file.ext
 * - Paths with directories: src/components/Button.tsx
 * - Line numbers: file.ts:123
 * - Line + column: file.ts:123:45
 *
 * Does NOT match:
 * - URLs (http://, https://)
 * - Plain numbers
 */
function createFilePathRegex(): RegExp {
  const extPattern = CODE_EXTENSIONS.join("|")

  // Pattern components:
  // 1. Optional: ./ or ../ or /
  // 2. Path segments: word chars, dots, hyphens, underscores, slashes
  // 3. Required: file extension
  // 4. Optional: :lineNumber or :lineNumber:columnNumber

  return new RegExp(
    `(?:^|\\s|["'(\`])` + // Word boundary (start, space, or quote)
    `(?!--)` + // Negative lookahead: reject if starts with --
    `(` + // Start capture group
    `(?:\\./|\\.\\./|/)?` + // Optional: ./ or ../ or / prefix (? makes it optional)
    `[\\w.-]+(?:/[\\w.-]+)*` + // Path segments: word chars, dots, hyphens (proper segment matching)
    `\\.(?:${extPattern})` + // File extension
    `(?::(\\d+))?` + // Optional :lineNumber
    `(?::(\\d+))?` + // Optional :columnNumber
    `)` + // End capture group
    `(?=\\s|$|["')\`])`, // Word boundary (space, end, or quote)
    "g"
  )
}

/**
 * Detect all file paths in the given text
 *
 * @param text Terminal output text to parse
 * @returns Array of detected file paths with metadata
 */
export function detectFilePaths(text: string): FilePath[] {
  if (!text) return []

  const regex = createFilePathRegex()
  const paths: FilePath[] = []
  let match: RegExpExecArray | null

  while ((match = regex.exec(text)) !== null) {
    const fullMatch = match[1] // The captured path (without prefix whitespace)
    const lineNumber = match[2] ? parseInt(match[2], 10) : undefined
    const columnNumber = match[3] ? parseInt(match[3], 10) : undefined

    // Extract just the path (remove :line:col suffix)
    let path = fullMatch
    if (lineNumber !== undefined) {
      path = path.replace(/:(\d+)(?::(\d+))?$/, "")
    }

    // Calculate actual indices in the original text
    // match.index points to the start of the whole match (including prefix)
    // We need to find where the actual path starts
    const prefixMatch = text.substring(match.index).match(/^[\s"'(`]/)
    const prefixLength = prefixMatch ? prefixMatch[0].length : 0
    const startIndex = match.index + prefixLength
    const endIndex = startIndex + fullMatch.length

    paths.push({
      path,
      lineNumber,
      columnNumber,
      startIndex,
      endIndex,
      fullMatch,
    })
  }

  return paths
}
