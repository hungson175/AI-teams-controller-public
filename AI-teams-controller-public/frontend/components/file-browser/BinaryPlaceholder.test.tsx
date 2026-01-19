/**
 * BinaryPlaceholder Component Tests
 */

import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { BinaryPlaceholder } from "./BinaryPlaceholder"

describe("BinaryPlaceholder", () => {
  describe("rendering", () => {
    it("should render file name", () => {
      render(<BinaryPlaceholder fileName="image.png" size={1024} />)

      expect(screen.getByText("image.png")).toBeInTheDocument()
    })

    it("should render default message when no message provided", () => {
      render(<BinaryPlaceholder fileName="binary.bin" size={2048} />)

      expect(screen.getByText("Cannot display binary file")).toBeInTheDocument()
    })

    it("should render custom message when provided", () => {
      render(
        <BinaryPlaceholder
          fileName="large.zip"
          size={5000000}
          message="File too large to display"
        />
      )

      expect(screen.getByText("File too large to display")).toBeInTheDocument()
    })
  })

  describe("file size formatting", () => {
    it("should format bytes correctly", () => {
      render(<BinaryPlaceholder fileName="small.bin" size={512} />)

      expect(screen.getByText("512 B")).toBeInTheDocument()
    })

    it("should format kilobytes correctly", () => {
      render(<BinaryPlaceholder fileName="medium.bin" size={2048} />)

      expect(screen.getByText("2 KB")).toBeInTheDocument()
    })

    it("should format megabytes correctly", () => {
      render(<BinaryPlaceholder fileName="large.bin" size={5242880} />)

      expect(screen.getByText("5 MB")).toBeInTheDocument()
    })

    it("should format gigabytes correctly", () => {
      render(<BinaryPlaceholder fileName="huge.bin" size={2147483648} />)

      expect(screen.getByText("2 GB")).toBeInTheDocument()
    })

    it("should handle zero size", () => {
      render(<BinaryPlaceholder fileName="empty.bin" size={0} />)

      expect(screen.getByText("0 B")).toBeInTheDocument()
    })
  })
})
