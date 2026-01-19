import { describe, it, expect } from "vitest"
import { parseAnsiToHtml, stripAnsi } from "./ansi-parser"

describe("ansi-parser", () => {
  describe("parseAnsiToHtml", () => {
    it("should return plain text unchanged", () => {
      const input = "Hello world"
      const result = parseAnsiToHtml(input)
      expect(result).toBe("Hello world")
    })

    it("should parse bold text", () => {
      // ANSI bold: \x1b[1m ... \x1b[0m
      const input = "\x1b[1mBold\x1b[0m"
      const result = parseAnsiToHtml(input)
      // ansi-to-html wraps bold text with <b> tag
      expect(result).toContain("Bold")
      expect(result).toContain("<b>")
      expect(result).toContain("</b>")
    })

    it("should parse basic foreground colors (red)", () => {
      // ANSI red foreground: \x1b[31m ... \x1b[0m
      const input = "\x1b[31mRed\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Red")
      // Should contain color styling (ansi-to-html uses inline style)
      expect(result).toContain("color:")
    })

    it("should parse green foreground color", () => {
      // ANSI green foreground: \x1b[32m
      const input = "\x1b[32mGreen\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Green")
      expect(result).toContain("color:")
    })

    it("should parse 24-bit RGB foreground colors", () => {
      // ANSI 24-bit RGB: \x1b[38;2;R;G;Bm
      const input = "\x1b[38;2;255;128;0mOrange\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Orange")
      // ansi-to-html converts to hex color like #ff8000
      expect(result.toLowerCase()).toMatch(/#ff8000|rgb\(255,\s*128,\s*0\)/)
    })

    it("should escape HTML entities for security (XSS prevention)", () => {
      // Security test: HTML in input should be escaped
      const input = "<script>alert('xss')</script>"
      const result = parseAnsiToHtml(input)
      // Should NOT contain raw script tag
      expect(result).not.toContain("<script>")
      // Should contain escaped entities
      expect(result).toContain("&lt;script&gt;")
      expect(result).toContain("&lt;/script&gt;")
    })

    it("should escape HTML entities mixed with ANSI codes", () => {
      // Security test: HTML inside ANSI styled text
      const input = "\x1b[31m<div onclick='evil()'>Click me</div>\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).not.toContain("<div onclick=")
      expect(result).toContain("&lt;div")
    })

    it("should handle nested styles (bold + color)", () => {
      // Bold green text
      const input = "\x1b[1m\x1b[32mBold Green\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Bold Green")
      // Should have both bold tag and color styling
      expect(result).toContain("<b>")
      expect(result).toContain("color:")
    })

    it("should handle background colors", () => {
      // ANSI background color: \x1b[41m (red background)
      const input = "\x1b[41mRed Background\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Red Background")
      expect(result).toContain("background-color:")
    })

    it("should handle reset codes correctly", () => {
      // Text after reset should not be styled
      const input = "\x1b[31mRed\x1b[0m Normal"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Red")
      expect(result).toContain("Normal")
      // Normal text should not be in the styled span
    })

    it("should handle empty string", () => {
      const input = ""
      const result = parseAnsiToHtml(input)
      expect(result).toBe("")
    })

    it("should handle text with newlines", () => {
      const input = "Line 1\nLine 2\n\x1b[32mColored Line 3\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Line 1")
      expect(result).toContain("Line 2")
      expect(result).toContain("Colored Line 3")
      expect(result).toContain("\n")
    })

    it("should handle underline style", () => {
      // ANSI underline: \x1b[4m
      const input = "\x1b[4mUnderlined\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Underlined")
      // ansi-to-html uses <u> tag for underline
      expect(result).toContain("<u>")
      expect(result).toContain("</u>")
    })

    it("should handle dim/faint text", () => {
      // ANSI dim: \x1b[2m
      const input = "\x1b[2mDim text\x1b[0m"
      const result = parseAnsiToHtml(input)
      expect(result).toContain("Dim text")
    })
  })

  describe("stripAnsi", () => {
    it("should strip ANSI color codes from text", () => {
      const input = "Error in \x1b[34msrc/file.ts\x1b[0m at line 10"
      const result = stripAnsi(input)
      expect(result).toBe("Error in src/file.ts at line 10")
    })
  })
})
