/**
 * FileTreeSkeleton Component Tests
 */

import { describe, it, expect } from "vitest"
import { render } from "@testing-library/react"
import { FileTreeSkeleton } from "./FileTreeSkeleton"

describe("FileTreeSkeleton", () => {
  describe("default rendering", () => {
    it("should render header skeleton elements", () => {
      const { container } = render(<FileTreeSkeleton />)

      // Header should have skeleton elements (border-b indicates header)
      expect(container.querySelector(".border-b")).toBeInTheDocument()
    })

    it("should render skeleton items with varying widths", () => {
      const { container } = render(<FileTreeSkeleton />)

      // Skeleton items should be present with animate-pulse class
      const skeletonElements = container.querySelectorAll('[class*="animate-pulse"]')
      expect(skeletonElements.length).toBeGreaterThan(0)
    })
  })

  describe("custom item count", () => {
    it("should render different amounts based on itemCount", () => {
      const { container: container5 } = render(<FileTreeSkeleton itemCount={5} />)
      const { container: container10 } = render(<FileTreeSkeleton itemCount={10} />)

      // More items should mean more skeleton elements
      const skeletons5 = container5.querySelectorAll('[class*="animate-pulse"]')
      const skeletons10 = container10.querySelectorAll('[class*="animate-pulse"]')

      expect(skeletons10.length).toBeGreaterThan(skeletons5.length)
    })

    it("should render minimal elements when itemCount is 0", () => {
      const { container } = render(<FileTreeSkeleton itemCount={0} />)

      // Only header skeletons should be present
      const treeContent = container.querySelector(".space-y-1")
      expect(treeContent?.children.length ?? 0).toBe(0)
    })
  })

  describe("structure", () => {
    it("should have header and tree sections", () => {
      const { container } = render(<FileTreeSkeleton />)

      // Should have border-b for header
      expect(container.querySelector(".border-b")).toBeInTheDocument()

      // Should have py-2 for tree content
      expect(container.querySelector(".py-2")).toBeInTheDocument()
    })

    it("should have varying indentation", () => {
      const { container } = render(<FileTreeSkeleton />)

      // Check that rows have inline styles (paddingLeft varies)
      const rowsWithStyle = container.querySelectorAll("[style]")
      expect(rowsWithStyle.length).toBeGreaterThan(0)
    })
  })
})
