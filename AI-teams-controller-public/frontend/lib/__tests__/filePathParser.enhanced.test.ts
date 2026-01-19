/**
 * Tests for Enhanced Path Detection Regex (Story 1)
 *
 * Sprint: Terminal File Path Click Popup (Phase 2)
 * Coverage target: 90% (regex parsing)
 */

import { detectFilePaths, FilePath } from "../filePathParser"

describe("detectFilePaths - Enhanced Path Detection (Story 1)", () => {
  describe("AC1: Detect absolute paths", () => {
    it("should detect absolute path with leading slash", () => {
      const text = "Error in /home/user/project/src/file.ts at line 10"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("/home/user/project/src/file.ts")
      expect(paths[0].fullMatch).toBe("/home/user/project/src/file.ts")
    })
  })

  describe("AC2: Detect relative paths", () => {
    it("should detect relative path with ./", () => {
      const text = "Import from ./components/Button.tsx failed"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("./components/Button.tsx")
    })

    it("should detect relative path with ../", () => {
      const text = "Loading ../lib/utils.ts"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("../lib/utils.ts")
    })
  })

  describe("AC3: Detect paths with line numbers", () => {
    it("should detect path with line number", () => {
      const text = "Error at src/app.ts:42"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("src/app.ts")
      expect(paths[0].lineNumber).toBe(42)
      expect(paths[0].fullMatch).toBe("src/app.ts:42")
    })

    it("should detect path with line and column numbers", () => {
      const text = "Error at src/app.ts:42:10"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("src/app.ts")
      expect(paths[0].lineNumber).toBe(42)
      expect(paths[0].columnNumber).toBe(10)
      expect(paths[0].fullMatch).toBe("src/app.ts:42:10")
    })
  })

  describe("AC4: Handle wrapped long paths", () => {
    it("should detect path split across wrapped lines", () => {
      // Simulating terminal line wrap - path appears as continuous text
      const text = "File: frontend/components/terminal/TerminalFileLink.tsx modified"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toContain("TerminalFileLink.tsx")
    })
  })

  describe("AC5: Ignore false positives", () => {
    it("should NOT detect URLs", () => {
      const text = "Visit https://example.com/page.html for docs"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(0)
    })

    it("should NOT detect command flags", () => {
      const text = "Run with --config file.json --output result.txt"
      const paths = detectFilePaths(text)

      // Should detect file.json and result.txt, but NOT --config or --output
      const pathStrings = paths.map(p => p.path)
      expect(pathStrings).not.toContain("--config")
      expect(pathStrings).not.toContain("--output")
    })

    it("should NOT detect flags that look like paths", () => {
      const text = "Use flag --src/config.ts to override"
      const paths = detectFilePaths(text)

      // Should not detect --src/config.ts (has -- prefix)
      expect(paths).toHaveLength(0)
    })
  })

  describe("Edge Case: Paths without prefix (NO-PREFIX PATHS)", () => {
    it("should detect path without ./ or / prefix", () => {
      const text = "Error in src/components/Button.tsx"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("src/components/Button.tsx")
    })

    it("should detect path with subdirectories but no prefix", () => {
      const text = "Modified: frontend/lib/utils/helper.ts"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toBe("frontend/lib/utils/helper.ts")
    })
  })

  describe("Edge Case: Paths with hyphens and underscores", () => {
    it("should detect path with hyphens in filename", () => {
      const text = "See file-browser-utils.ts for details"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toContain("file-browser-utils.ts")
    })

    it("should detect path with underscores in filename", () => {
      const text = "Check test_utils.py module"
      const paths = detectFilePaths(text)

      expect(paths).toHaveLength(1)
      expect(paths[0].path).toContain("test_utils.py")
    })
  })
})
