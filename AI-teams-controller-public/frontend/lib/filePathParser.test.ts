/**
 * File Path Parser Tests (Sprint 13 - Work Item #4)
 *
 * Tests for detecting and parsing file paths in terminal output
 */

import { describe, it, expect } from "vitest"
import { detectFilePaths, type FilePath } from "./filePathParser"

describe("filePathParser", () => {
  describe("detectFilePaths", () => {
    it("should detect absolute Unix paths", () => {
      const text = "Error in /home/user/project/src/App.tsx at line 42"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("/home/user/project/src/App.tsx")
      expect(paths[0].lineNumber).toBeUndefined()
    })

    it("should detect relative paths with ./", () => {
      const text = "File not found: ./components/Button.tsx"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("./components/Button.tsx")
    })

    it("should detect relative paths with ../", () => {
      const text = "Import from ../utils/helpers.ts failed"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("../utils/helpers.ts")
    })

    it("should detect paths with line numbers (file.py:123)", () => {
      const text = "TypeError at backend/app/main.py:45"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("backend/app/main.py")
      expect(paths[0].lineNumber).toBe(45)
    })

    it("should detect paths with line and column numbers (file.ts:123:45)", () => {
      const text = "Error: frontend/lib/auth.ts:123:45 - Type error"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("frontend/lib/auth.ts")
      expect(paths[0].lineNumber).toBe(123)
      expect(paths[0].columnNumber).toBe(45)
    })

    it("should detect multiple paths in same line", () => {
      const text = "Comparing src/old.js with src/new.js"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(2)
      expect(paths[0].path).toBe("src/old.js")
      expect(paths[1].path).toBe("src/new.js")
    })

    it("should ignore non-file strings", () => {
      const text = "URL: https://example.com:8080/api/endpoint"
      const paths = detectFilePaths(text)

      // Should not detect URLs as file paths
      expect(paths).toHaveLength(0)
    })

    it("should ignore plain numbers", () => {
      const text = "Process ID: 12345, Port: 3000"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(0)
    })

    it("should detect common code file extensions", () => {
      const extensions = [".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java", ".css", ".html", ".json", ".yaml", ".yml", ".md"]

      extensions.forEach(ext => {
        const text = `Error in file${ext}`
        const paths = detectFilePaths(text)
        expect(paths).toHaveLength(1)
        expect(paths[0].path).toBe(`file${ext}`)
      })
    })

    it("should preserve start and end indices for replacement", () => {
      const text = "Error at src/App.tsx:42"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].startIndex).toBeGreaterThanOrEqual(0)
      expect(paths[0].endIndex).toBeGreaterThan(paths[0].startIndex)

      // Verify we can extract the exact match
      const match = text.substring(paths[0].startIndex, paths[0].endIndex)
      expect(match).toBe("src/App.tsx:42")
    })

    it("should handle empty string", () => {
      const paths = detectFilePaths("")
      expect(paths).toHaveLength(0)
    })

    it("should handle string with no paths", () => {
      const text = "This is just plain text with no file references"
      const paths = detectFilePaths(text)
      expect(paths).toHaveLength(0)
    })
  })
})
