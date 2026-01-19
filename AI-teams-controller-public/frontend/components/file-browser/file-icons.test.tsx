/**
 * File Icons Tests
 */

import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { FileIcon, getFileIcon } from "./file-icons"

describe("getFileIcon", () => {
  describe("TypeScript files", () => {
    it("should return blue color for .ts files", () => {
      const config = getFileIcon("app.ts")
      expect(config.colorClass).toBe("text-blue-500")
    })

    it("should return blue color for .tsx files", () => {
      const config = getFileIcon("Component.tsx")
      expect(config.colorClass).toBe("text-blue-500")
    })
  })

  describe("JavaScript files", () => {
    it("should return yellow color for .js files", () => {
      const config = getFileIcon("script.js")
      expect(config.colorClass).toBe("text-yellow-500")
    })

    it("should return yellow color for .jsx files", () => {
      const config = getFileIcon("Component.jsx")
      expect(config.colorClass).toBe("text-yellow-500")
    })
  })

  describe("Python files", () => {
    it("should return green color for .py files", () => {
      const config = getFileIcon("main.py")
      expect(config.colorClass).toBe("text-green-500")
    })
  })

  describe("JSON files", () => {
    it("should return orange color for .json files", () => {
      const config = getFileIcon("package.json")
      expect(config.colorClass).toBe("text-orange-500")
    })
  })

  describe("Markdown files", () => {
    it("should return purple color for .md files", () => {
      const config = getFileIcon("README.md")
      expect(config.colorClass).toBe("text-purple-500")
    })

    it("should return purple color for .mdx files", () => {
      const config = getFileIcon("doc.mdx")
      expect(config.colorClass).toBe("text-purple-500")
    })
  })

  describe("CSS files", () => {
    it("should return pink color for .css files", () => {
      const config = getFileIcon("styles.css")
      expect(config.colorClass).toBe("text-pink-500")
    })
  })

  describe("Config files", () => {
    it("should return orange color for .yaml files", () => {
      const config = getFileIcon("config.yaml")
      expect(config.colorClass).toBe("text-orange-500")
    })

    it("should return orange color for .toml files", () => {
      const config = getFileIcon("pyproject.toml")
      expect(config.colorClass).toBe("text-orange-500")
    })

    it("should return muted color for .env files", () => {
      const config = getFileIcon(".env")
      expect(config.colorClass).toBe("text-muted-foreground")
    })
  })

  describe("Image files", () => {
    it("should return red color for .png files (blocked binary)", () => {
      const config = getFileIcon("image.png")
      expect(config.colorClass).toBe("text-red-400")
    })

    it("should return red color for .svg files (blocked binary)", () => {
      const config = getFileIcon("icon.svg")
      expect(config.colorClass).toBe("text-red-400")
    })
  })

  describe("Unknown files", () => {
    it("should return muted color for unknown extensions", () => {
      const config = getFileIcon("file.xyz")
      expect(config.colorClass).toBe("text-muted-foreground")
    })

    it("should return muted color for files without extension", () => {
      const config = getFileIcon("Makefile")
      expect(config.colorClass).toBe("text-muted-foreground")
    })
  })
})

describe("FileIcon", () => {
  it("should render with correct color class", () => {
    const { container } = render(<FileIcon fileName="app.ts" />)
    const svg = container.querySelector("svg")
    expect(svg).toHaveClass("text-blue-500")
  })

  it("should apply custom className", () => {
    const { container } = render(<FileIcon fileName="app.ts" className="custom-class" />)
    const svg = container.querySelector("svg")
    expect(svg).toHaveClass("custom-class")
  })

  it("should have default size classes", () => {
    const { container } = render(<FileIcon fileName="app.ts" />)
    const svg = container.querySelector("svg")
    expect(svg).toHaveClass("h-4")
    expect(svg).toHaveClass("w-4")
  })
})
