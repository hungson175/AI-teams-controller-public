/**
 * Tests for Improved Path Resolution with Scoring (Story 2)
 *
 * Sprint: Terminal File Path Click Popup (Phase 2)
 * Coverage target: 85% (scoring algorithm)
 */

import { resolveFilePathWithScoring } from "../usePathResolver"

describe("resolveFilePathWithScoring - Improved Scoring Algorithm (Story 2)", () => {
  const fileList = [
    "frontend/components/Button.tsx",
    "backend/components/Button.tsx",
    "frontend/components/ui/Button.tsx",
    "frontend/lib/utils/button-helper.ts",
    "tests/Button.test.tsx",
    "src/components/form/Button.tsx",
  ]

  describe("AC1: Prefer exact filename matches", () => {
    it("should rank exact filename match highest", () => {
      const matches = resolveFilePathWithScoring("Button.tsx", fileList)

      // All have "Button.tsx" filename, but should prefer exact match
      expect(matches.length).toBeGreaterThan(0)
      expect(matches[0].path).toContain("Button.tsx")
    })

    it("should rank exact basename higher than partial match", () => {
      const matches = resolveFilePathWithScoring("button-helper.ts", fileList)

      // "button-helper.ts" (exact) should rank higher than "Button.tsx" (different)
      expect(matches[0].path).toBe("frontend/lib/utils/button-helper.ts")
    })
  })

  describe("AC2: Consider directory context from terminal output", () => {
    it("should prefer path with more matching directory segments", () => {
      const fileListWithContext = [
        "frontend/components/ui/Button.tsx",
        "components/Button.tsx",
        "Button.tsx",
      ]

      const matches = resolveFilePathWithScoring(
        "frontend/components/ui/Button.tsx",
        fileListWithContext
      )

      // Exact path match should rank highest
      expect(matches[0].path).toBe("frontend/components/ui/Button.tsx")
    })

    it("should score segment overlap correctly", () => {
      const matches = resolveFilePathWithScoring(
        "components/Button.tsx",
        fileList
      )

      // Paths with "components" in them should rank higher
      const topMatch = matches[0]
      expect(topMatch.path).toContain("components")
      expect(topMatch.score).toBeGreaterThan(100) // Filename match + segment overlap
    })
  })

  describe("AC3: Shorter paths preferred (length penalty)", () => {
    it("should prefer shorter path when filenames are same", () => {
      const matches = resolveFilePathWithScoring("Button.tsx", [
        "Button.tsx",
        "components/Button.tsx",
        "frontend/components/ui/Button.tsx",
      ])

      // "Button.tsx" (2 segments) should beat longer paths
      // Even though all have exact filename match
      expect(matches[0].path).toBe("Button.tsx")
    })

    it("should apply length penalty to longer paths", () => {
      const matches = resolveFilePathWithScoring("Button.tsx", [
        "frontend/components/ui/Button.tsx", // 4 segments
        "components/Button.tsx", // 2 segments
      ])

      // Shorter path should have higher score despite both matching filename
      expect(matches[0].path).toBe("components/Button.tsx")
      expect(matches[0].score).toBeGreaterThan(matches[1].score)
    })
  })

  describe("AC4: Match confidence scoring", () => {
    it("should return match with score", () => {
      const matches = resolveFilePathWithScoring("Button.tsx", fileList)

      expect(matches[0]).toHaveProperty("path")
      expect(matches[0]).toHaveProperty("score")
      expect(typeof matches[0].score).toBe("number")
    })

    it("should calculate score correctly for exact match", () => {
      const matches = resolveFilePathWithScoring(
        "frontend/components/Button.tsx",
        ["frontend/components/Button.tsx"]
      )

      // Exact filename match (+100) + all segments match (+60 for 3 segments * 20) + no length penalty
      expect(matches[0].score).toBeGreaterThanOrEqual(160)
    })

    it("should order matches by score descending", () => {
      const matches = resolveFilePathWithScoring("Button.tsx", fileList)

      // Verify scores are in descending order
      for (let i = 0; i < matches.length - 1; i++) {
        expect(matches[i].score).toBeGreaterThanOrEqual(matches[i + 1].score)
      }
    })
  })

  describe("Edge Cases", () => {
    it("should handle empty file list", () => {
      const matches = resolveFilePathWithScoring("Button.tsx", [])
      expect(matches).toEqual([])
    })

    it("should handle empty parsed path", () => {
      const matches = resolveFilePathWithScoring("", fileList)
      expect(matches).toEqual([])
    })

    it("should handle no matches", () => {
      const matches = resolveFilePathWithScoring("NonExistent.tsx", fileList)
      expect(matches).toEqual([])
    })
  })
})
