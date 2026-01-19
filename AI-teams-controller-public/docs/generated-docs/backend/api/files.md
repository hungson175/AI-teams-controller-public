# File Browser API

Endpoints for browsing project files.

## Endpoints

### Get Directory Tree

```http
GET /api/files/{team_id}/tree?path=/&depth=1&show_hidden=false
```

Returns directory structure with lazy loading.

**Parameters:**
- `path` - Directory path (default: root)
- `depth` - Levels to expand (default: 1)
- `show_hidden` - Include dotfiles (default: false)

**Response:**
```json
{
  "tree": [
    {
      "name": "src",
      "path": "/src",
      "type": "directory",
      "children": null
    },
    {
      "name": "package.json",
      "path": "/package.json",
      "type": "file",
      "size": 1234
    }
  ]
}
```

### Get File Content

```http
GET /api/files/{team_id}/content?path=/src/index.ts
```

Returns file content with viewer type suggestion.

**Response:**
```json
{
  "content": "import React from 'react';\n...",
  "viewer": "code",
  "language": "typescript",
  "size": 2048,
  "truncated": false
}
```

**Viewer types:** `code`, `markdown`, `binary`, `large`

### List All Files (Search)

```http
GET /api/files/{team_id}/list?limit=10000&show_hidden=false
```

Returns flat file list for Cmd+P fuzzy search.

**Response:**
```json
{
  "files": [
    "/src/index.ts",
    "/src/components/App.tsx"
  ],
  "total": 1234,
  "truncated": false
}
```

Skips: `node_modules`, `__pycache__`, `.git`, `venv`

## Security

- JWT authentication required
- Path sanitization (blocks `..` traversal)
- Symlink resolution (within project only)
- Large files truncated (>1MB)
- Binary files detected and marked
