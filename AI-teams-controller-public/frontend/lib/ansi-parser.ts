import AnsiToHtml from 'ansi-to-html'

// Create singleton converter with our color scheme
const converter = new AnsiToHtml({
  fg: '#e5e5e5',      // Default foreground (matches --foreground)
  bg: 'transparent',  // Transparent background
  escapeXML: true,    // Escape HTML entities for security (XSS prevention)
  stream: false,      // Not streaming mode
})

/**
 * Parse ANSI escape sequences to HTML
 *
 * Converts terminal ANSI codes (colors, bold, underline, etc.) to HTML spans
 * with inline styles for rendering in the web UI.
 *
 * Security: HTML entities are escaped to prevent XSS attacks.
 *
 * @param text - Raw text with ANSI escape sequences
 * @returns HTML string with styled spans
 */
export function parseAnsiToHtml(text: string): string {
  return converter.toHtml(text)
}

/**
 * Strip ANSI escape codes from text
 * Used before regex-based path detection
 */
export function stripAnsi(text: string): string {
  // eslint-disable-next-line no-control-regex
  return text.replace(/\x1b\[[0-9;]*m/g, '')
}
