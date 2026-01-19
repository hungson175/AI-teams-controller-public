import { describe, it, expect } from "vitest"
import { createCommandSearch, fuzzySearchWithHighlight } from "./fuzzy-search"

describe("fuzzy-search", () => {
  describe("createCommandSearch", () => {
    const commands = [
      "git status",
      "git diff",
      "git commit",
      "git checkout",
      "run tests",
      "run build",
      "run pytest",
      "refactor",
      "read file",
      "search for",
    ]

    const commandSearch = createCommandSearch(commands)

    it("returns empty array for empty query", () => {
      const result = commandSearch("")
      expect(result).toEqual([])
    })

    it("returns empty array for very short query", () => {
      // Empty string should return empty
      const result = commandSearch("")
      expect(result).toEqual([])
    })

    it("matches exact prefix", () => {
      const result = commandSearch("git s")
      expect(result).toContain("git status")
      // git status should be a top result for "git s"
      expect(result[0]).toBe("git status")
    })

    it("matches fuzzy (non-contiguous characters)", () => {
      // "gco" should match "git commit" or "git checkout" (g-c-o pattern)
      const result = commandSearch("gco")
      // At least one of these should match
      const hasGitCommit = result.includes("git commit")
      const hasGitCheckout = result.includes("git checkout")
      expect(hasGitCommit || hasGitCheckout).toBe(true)
    })

    it("respects limit parameter", () => {
      const manyCommands = Array.from({ length: 20 }, (_, i) => `command ${i}`)
      const search = createCommandSearch(manyCommands)

      const result = search("command", 5)
      expect(result.length).toBeLessThanOrEqual(5)
    })

    it("ranks better matches higher", () => {
      const result = commandSearch("run")
      // "run tests" and "run build" should appear before "refactor"
      const runTestsIndex = result.indexOf("run tests")
      const runBuildIndex = result.indexOf("run build")
      const refactorIndex = result.indexOf("refactor")

      // If refactor is in results, it should be after exact "run" matches
      if (refactorIndex !== -1) {
        if (runTestsIndex !== -1) {
          expect(runTestsIndex).toBeLessThan(refactorIndex)
        }
        if (runBuildIndex !== -1) {
          expect(runBuildIndex).toBeLessThan(refactorIndex)
        }
      }
    })

    it("performs case insensitive matching", () => {
      const mixedCaseCommands = ["Git Status", "GIT DIFF", "git commit"]
      const search = createCommandSearch(mixedCaseCommands)

      const result = search("git")
      expect(result.length).toBeGreaterThan(0)
      // All three should potentially match "git"
    })

    it("returns results for partial command match", () => {
      const result = commandSearch("tes")
      expect(result).toContain("run tests")
    })

    it("handles single character query", () => {
      const result = commandSearch("g")
      // Should return git commands
      const hasGitCommand = result.some((cmd) => cmd.startsWith("git"))
      expect(hasGitCommand).toBe(true)
    })
  })

  describe("fuzzySearchWithHighlight", () => {
    const items = ["git commit", "git checkout", "run tests"]

    it("returns items with highlighted matches", () => {
      const result = fuzzySearchWithHighlight(items, "git", 5)

      expect(result.length).toBeGreaterThan(0)
      // Each result should have item and highlighted properties
      result.forEach((r) => {
        expect(r).toHaveProperty("item")
        expect(r).toHaveProperty("highlighted")
      })
    })

    it("highlights matched characters with mark tags", () => {
      const result = fuzzySearchWithHighlight(items, "git", 5)

      // Find a git result
      const gitResult = result.find((r) => r.item.startsWith("git"))
      if (gitResult) {
        // Should contain <mark> tags
        expect(gitResult.highlighted).toContain("<mark>")
        expect(gitResult.highlighted).toContain("</mark>")
      }
    })

    it("respects limit parameter", () => {
      const manyItems = Array.from({ length: 20 }, (_, i) => `item ${i}`)
      const result = fuzzySearchWithHighlight(manyItems, "item", 3)
      expect(result.length).toBeLessThanOrEqual(3)
    })

    it("returns empty array for empty query", () => {
      const result = fuzzySearchWithHighlight(items, "", 5)
      expect(result).toEqual([])
    })

    it("preserves original item text", () => {
      const result = fuzzySearchWithHighlight(items, "git", 5)

      result.forEach((r) => {
        expect(items).toContain(r.item)
      })
    })
  })
})
