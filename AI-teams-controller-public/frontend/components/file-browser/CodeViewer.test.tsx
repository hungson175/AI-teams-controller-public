/**
 * CodeViewer Component Tests
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen } from "@testing-library/react"
import { CodeViewer } from "./CodeViewer"

// Mock Monaco Editor as it doesn't work in jsdom
vi.mock("@monaco-editor/react", () => ({
  default: ({ value, language }: { value: string; language: string }) => (
    <div data-testid="monaco-editor" data-language={language}>
      {value}
    </div>
  ),
}))

describe("CodeViewer", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("rendering", () => {
    it("should render code content", () => {
      render(<CodeViewer content="const x = 1;" fileName="test.ts" />)

      expect(screen.getByTestId("monaco-editor")).toHaveTextContent("const x = 1;")
    })
  })

  describe("language detection", () => {
    it("should detect TypeScript files", () => {
      render(<CodeViewer content="const x: number = 1;" fileName="test.ts" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "typescript")
    })

    it("should detect TSX files", () => {
      render(<CodeViewer content="<Component />" fileName="App.tsx" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "typescript")
    })

    it("should detect JavaScript files", () => {
      render(<CodeViewer content="var x = 1;" fileName="script.js" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "javascript")
    })

    it("should detect Python files", () => {
      render(<CodeViewer content="def foo(): pass" fileName="script.py" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "python")
    })

    it("should detect JSON files", () => {
      render(<CodeViewer content='{"key": "value"}' fileName="config.json" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "json")
    })

    it("should detect YAML files", () => {
      render(<CodeViewer content="key: value" fileName="config.yaml" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "yaml")
    })

    it("should detect HTML files", () => {
      render(<CodeViewer content="<html></html>" fileName="index.html" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "html")
    })

    it("should detect CSS files", () => {
      render(<CodeViewer content=".class {}" fileName="styles.css" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "css")
    })

    it("should detect Go files", () => {
      render(<CodeViewer content="package main" fileName="main.go" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "go")
    })

    it("should detect Rust files", () => {
      render(<CodeViewer content="fn main() {}" fileName="main.rs" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "rust")
    })

    it("should detect shell files", () => {
      render(<CodeViewer content="#!/bin/bash" fileName="script.sh" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "shell")
    })

    it("should detect SQL files", () => {
      render(<CodeViewer content="SELECT * FROM users" fileName="query.sql" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "sql")
    })

    it("should detect Dockerfile", () => {
      render(<CodeViewer content="FROM node:18" fileName="Dockerfile" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "dockerfile")
    })

    it("should detect Makefile", () => {
      render(<CodeViewer content="build:" fileName="Makefile" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "makefile")
    })

    it("should fallback to plaintext for unknown extensions", () => {
      render(<CodeViewer content="some content" fileName="file.unknown" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "plaintext")
    })

    it("should handle .env files as plaintext", () => {
      render(<CodeViewer content="KEY=value" fileName=".env" />)

      expect(screen.getByTestId("monaco-editor")).toHaveAttribute("data-language", "plaintext")
    })
  })
})
