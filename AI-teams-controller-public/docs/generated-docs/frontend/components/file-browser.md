# FileBrowser Component

File browser for viewing project files.

## Overview

Split-panel file browser with tree view and content viewers.

**Location:** `frontend/components/file-browser/`

## Components

| Component | Purpose |
|-----------|---------|
| `FileBrowser.tsx` | Main container, split panels |
| `FileTree.tsx` | Directory tree with lazy loading |
| `FileTreeItem.tsx` | File/folder item with icon |
| `FileViewer.tsx` | Content viewer container |
| `CodeViewer.tsx` | Monaco editor (syntax highlighting) |
| `MarkdownViewer.tsx` | GFM markdown with Mermaid |
| `BinaryPlaceholder.tsx` | Placeholder for binary files |
| `FileSearch.tsx` | Cmd+P fuzzy search dialog |

## Features

| Feature | Description |
|---------|-------------|
| **Responsive** | Split panels (desktop) / tabs (mobile) |
| **Lazy Loading** | Directories load on expand |
| **Color-coded Icons** | TS (blue), JS (yellow), Python (green) |
| **Mermaid Diagrams** | Renders inline in markdown |
| **Syntax Highlighting** | 40+ languages |
| **File Search** | Cmd+P fuzzy search |

## Usage

```tsx
<FileBrowser teamId="command-center" />
```

## API Endpoints Used

```
GET /api/files/{team}/tree     # Directory structure
GET /api/files/{team}/content  # File content
GET /api/files/{team}/list     # Flat list for search
```

## Viewer Types

| Type | Component | Use Case |
|------|-----------|----------|
| `code` | CodeViewer | Source files (.ts, .py, .js) |
| `markdown` | MarkdownViewer | .md files with GFM |
| `binary` | BinaryPlaceholder | Images, executables |
| `large` | BinaryPlaceholder | Files > 1MB |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Cmd+P` / `Ctrl+P` | Open file search |
| `↑` `↓` | Navigate search results |
| `Enter` | Open selected file |
| `Esc` | Close search dialog |
