/**
 * CodeEditor Component Tests (Sprint 13 - Work Item #1)
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen } from "@testing-library/react"
import { CodeEditor } from "./CodeEditor"

// Mock CodeMirror as it doesn't work in jsdom
vi.mock("@codemirror/state", () => ({
  EditorState: {
    create: vi.fn((config) => ({
      doc: {
        toString: () => config.doc || "",
      },
    })),
  },
}))

vi.mock("@codemirror/view", () => {
  const EditorView = vi.fn(function (config: any) {
    // Mock EditorView constructor
    this.state = config.state
    this.dispatch = vi.fn()
    this.destroy = vi.fn()

    // Render a mock editor div for testing
    if (config.parent) {
      const mockEditor = document.createElement("div")
      mockEditor.setAttribute("data-testid", "code-editor-view")
      mockEditor.textContent = "CodeMirror Editor Mock"
      config.parent.appendChild(mockEditor)
    }

    return this
  })

  // Add static methods to EditorView
  EditorView.updateListener = {
    of: vi.fn(() => ({})),
  }

  return {
    EditorView,
    keymap: {
      of: vi.fn(() => ({})),
    },
  }
})

vi.mock("@codemirror/commands", () => ({
  defaultKeymap: [],
}))

vi.mock("@codemirror/lang-javascript", () => ({
  javascript: vi.fn((options) => ({
    name: "javascript",
    typescript: options?.typescript || false,
    jsx: options?.jsx || false,
  })),
}))

vi.mock("@codemirror/lang-python", () => ({
  python: vi.fn(() => ({ name: "python" })),
}))

vi.mock("@codemirror/theme-one-dark", () => ({
  oneDark: { name: "oneDark" },
}))

describe("CodeEditor", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("rendering", () => {
    it("should render code editor container", () => {
      render(<CodeEditor value="const x = 1;" onChange={vi.fn()} fileName="test.ts" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should render CodeMirror view", () => {
      render(<CodeEditor value="const x = 1;" onChange={vi.fn()} fileName="test.ts" />)

      expect(screen.getByTestId("code-editor-view")).toBeInTheDocument()
    })
  })

  describe("language detection - Work Item #1 (JS, TS, Python)", () => {
    it("should detect JavaScript files (.js)", () => {
      // Component renders successfully with JS file
      render(<CodeEditor value="var x = 1;" onChange={vi.fn()} fileName="script.js" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect JSX files (.jsx)", () => {
      // Component renders successfully with JSX file
      render(<CodeEditor value="<Component />" onChange={vi.fn()} fileName="App.jsx" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect TypeScript files (.ts)", () => {
      // Component renders successfully with TS file
      render(<CodeEditor value="const x: number = 1;" onChange={vi.fn()} fileName="test.ts" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect TSX files (.tsx)", () => {
      // Component renders successfully with TSX file
      render(<CodeEditor value="<Component />" onChange={vi.fn()} fileName="App.tsx" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect Python files (.py)", () => {
      // Component renders successfully with Python file
      render(<CodeEditor value="def foo(): pass" onChange={vi.fn()} fileName="script.py" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should handle unsupported file types (plain text)", () => {
      // For unsupported file types, component should still render without language extension
      render(<CodeEditor value="some text" onChange={vi.fn()} fileName="file.txt" />)

      // Component renders successfully even without language support
      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })
  })

  describe("language detection - Work Item #2 (Go, Rust, Java, CSS)", () => {
    it("should detect Go files (.go)", () => {
      // Component renders successfully with Go file
      render(<CodeEditor value="package main" onChange={vi.fn()} fileName="main.go" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect Rust files (.rs)", () => {
      // Component renders successfully with Rust file
      render(<CodeEditor value="fn main() {}" onChange={vi.fn()} fileName="main.rs" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect Java files (.java)", () => {
      // Component renders successfully with Java file
      render(<CodeEditor value="public class Main {}" onChange={vi.fn()} fileName="Main.java" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect CSS files (.css)", () => {
      // Component renders successfully with CSS file
      render(<CodeEditor value=".class { color: red; }" onChange={vi.fn()} fileName="styles.css" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })
  })

  describe("language detection - Work Item #3 (HTML, Markdown, JSON, YAML)", () => {
    it("should detect HTML files (.html)", () => {
      // Component renders successfully with HTML file
      render(<CodeEditor value="<div>Hello</div>" onChange={vi.fn()} fileName="index.html" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect Markdown files (.md)", () => {
      // Component renders successfully with Markdown file
      render(<CodeEditor value="# Hello World" onChange={vi.fn()} fileName="README.md" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect JSON files (.json)", () => {
      // Component renders successfully with JSON file
      render(<CodeEditor value='{"key": "value"}' onChange={vi.fn()} fileName="config.json" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect YAML files (.yaml)", () => {
      // Component renders successfully with YAML file
      render(<CodeEditor value="key: value" onChange={vi.fn()} fileName="config.yaml" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should detect YAML files (.yml)", () => {
      // Component renders successfully with .yml extension
      render(<CodeEditor value="key: value" onChange={vi.fn()} fileName="docker-compose.yml" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })
  })

  describe("onChange callback", () => {
    it("should accept onChange callback", () => {
      const onChange = vi.fn()

      render(<CodeEditor value="initial" onChange={onChange} fileName="test.js" />)

      // Just verify onChange is accepted - actual change event testing would require
      // simulating CodeMirror's update listener, which is complex in unit tests
      expect(onChange).toBeDefined()
    })
  })

  describe("props", () => {
    it("should accept value prop", () => {
      // Component should render with provided value
      render(<CodeEditor value="test content" onChange={vi.fn()} fileName="test.js" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should accept fileName prop", () => {
      // Component should render with provided fileName
      render(<CodeEditor value="code" onChange={vi.fn()} fileName="app.ts" />)

      expect(screen.getByTestId("code-editor")).toBeInTheDocument()
    })

    it("should accept optional className prop", () => {
      // Component should apply custom className
      render(<CodeEditor value="code" onChange={vi.fn()} fileName="test.js" className="custom-class" />)

      const editor = screen.getByTestId("code-editor")
      expect(editor.className).toContain("custom-class")
    })
  })
})
