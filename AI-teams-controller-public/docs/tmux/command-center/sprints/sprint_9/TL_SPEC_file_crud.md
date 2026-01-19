# Technical Spec: Sprint 9 - File Browser CRUD

**Author**: TL | **Date**: 2026-01-03 | **Status**: READY

---

## Story Status Summary

| Story | Status | Action |
|-------|--------|--------|
| 9.1 Pre-fill Path | ✅ ALREADY DONE | QA verify only (FileTree.tsx:75-87, 167-171) |
| 9.2 Delete | TODO | BE + FE implement |
| 9.3 Rename | TODO | BE + FE implement |
| 9.4 Escape Close | ✅ LIKELY DONE | QA verify (shadcn default behavior) |

---

## API Endpoints

### DELETE `/api/files/{team_id}/delete`

**Request**: `{ "path": "docs/old-file.txt" }`
**Response**: `{ "success": true, "path": "...", "type": "file|folder", "message": "..." }`
**Errors**: 400 (traversal/protected), 404 (not found)

### PATCH `/api/files/{team_id}/rename`

**Request**: `{ "old_path": "docs/old.txt", "new_name": "new.txt" }`
**Response**: `{ "success": true, "old_path": "...", "new_path": "...", "type": "file|folder", "message": "..." }`
**Errors**: 400 (traversal/invalid chars/exists), 404 (not found)

---

## Security Requirements

1. **Path traversal blocked**: Reject any path containing `..`
2. **Protected paths**: Block `.git`, `node_modules`, `__pycache__`, `.venv`, project root
3. **Name validation**: Block `/`, `\`, `<>:"|?*` and null bytes in new_name
4. **Existence checks**: 404 if source doesn't exist, 400 if target already exists

---

## Key Design Decisions

1. **Rename takes name only**: `new_name` is just filename, not full path. Backend computes new path from old path's parent directory.
2. **Recursive folder delete**: Use `shutil.rmtree()` for folders
3. **Confirmation required**: Frontend shows AlertDialog before delete
4. **Context menu integration**: Add Delete/Rename to existing right-click menu
5. **Tree refresh via callback**: Pass `onRefresh` prop to FileTreeItem

---

## Files to Modify

### Backend
- `backend/app/api/file_routes.py` - Add DELETE + PATCH endpoints

### Frontend
- `frontend/components/file-browser/FileTreeItem.tsx` - Add context menu items, dialogs, handlers
- `frontend/components/file-browser/FileTree.tsx` - Pass `onRefresh` callback to FileTreeItem

---

## Test Cases

**Delete**: existing file ✓, existing folder ✓, not found → 404, traversal → 400, protected → 400
**Rename**: file ✓, folder ✓, not found → 404, traversal → 400, invalid chars → 400, exists → 400
