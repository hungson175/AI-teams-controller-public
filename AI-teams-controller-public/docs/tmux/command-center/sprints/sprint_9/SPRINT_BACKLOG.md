# Sprint 9 Backlog - File Browser CRUD Complete

**Sprint Goal:** Complete CRUD operations for File Browser
**Start Date:** 2026-01-02
**Owner:** Developers (TL, FE, BE, QA)
**Status:** PLANNING

---

## Sprint Overview

This sprint completes the File Browser feature set by implementing the remaining CRUD operations and improving UX with keyboard shortcuts and path pre-filling.

**Total Stories:** 4
**Estimated Effort:** ~1 sprint (Medium)
**Expected Value:** High - completes core file management functionality

---

## Sprint Backlog Items

### Story 9.1: Pre-fill Path in Add File/Folder Dialog
**Priority:** P1
**Size:** XS
**Status:** TODO
**Source:** Sprint 8 Retrospective minor finding

**User Story:**
As a user adding a file/folder,
I want the current directory path pre-filled in the dialog,
So that I don't have to type the full path every time.

**Current Behavior:**
- Dialog shows static placeholder: `docs/new-file.txt or docs/new-folder/`
- User must type full path from project root
- No context awareness of currently selected directory

**Expected Behavior:**
- Dialog pre-fills with current directory path when opened
- If user has a folder selected in tree, pre-fill with that folder's path
- If user has a file selected, pre-fill with that file's parent directory path
- User can edit the pre-filled path or clear it
- Works for both file and folder creation

**Acceptance Criteria:**
- [ ] Dialog pre-fills current directory path when opened
- [ ] User can edit the pre-filled path
- [ ] Works for both file and folder creation
- [ ] Pre-filled path updates based on currently selected folder/file in tree
- [ ] If nothing selected, pre-fill with project root or empty

**Technical Notes:**
- `FileTree.tsx` component needs to track current selected directory
- Pass current directory path to dialog when opening
- Set `newPath` state with pre-filled value instead of empty string
- Consider UX: pre-fill should help, not force - user should be able to clear easily

**Files to Modify:**
- `frontend/components/file-browser/FileTree.tsx` (dialog state management)

---

### Story 9.2: Delete File/Folder
**Priority:** P2
**Size:** S
**Status:** TODO

**User Story:**
As a user managing project files,
I want to delete files and folders from the file browser,
So that I can clean up my project without using terminal commands.

**Current Behavior:**
- Right-click menu shows: Copy Path, Copy Content
- No delete option available
- User must use terminal or external tools to delete files

**Expected Behavior:**
- Right-click on file/folder shows "Delete" option in context menu
- Confirmation dialog appears before deletion (prevent accidents)
- File/folder deleted via backend API
- Tree refreshes automatically after deletion
- Toast notification confirms deletion success
- Error handling for permission issues or non-existent files

**Acceptance Criteria:**
- [ ] Right-click on file/folder shows "Delete" option in context menu
- [ ] Confirmation dialog appears before deletion (with file/folder name shown)
- [ ] File/folder deleted via backend API endpoint
- [ ] Tree refreshes after successful deletion
- [ ] Toast notification confirms deletion ("File deleted successfully")
- [ ] Error handling displays user-friendly message on failure
- [ ] Deletion blocked for project root or critical system folders

**Technical Notes:**
- Backend API endpoint: `DELETE /api/files/{team_id}/{path}`
- Frontend: Add "Delete" option to context menu in `FileTreeItem.tsx`
- Use shadcn/ui AlertDialog for confirmation
- Implement safety checks (can't delete `.git`, project root, etc.)

**Files to Modify:**
- `frontend/components/file-browser/FileTreeItem.tsx` (context menu)
- `backend/app/api/file_routes.py` (DELETE endpoint - may already exist)

---

### Story 9.3: Rename File/Folder
**Priority:** P2
**Size:** S
**Status:** TODO

**User Story:**
As a user managing project files,
I want to rename files and folders from the file browser,
So that I can organize my project without using terminal commands.

**Current Behavior:**
- Right-click menu shows: Copy Path, Copy Content
- No rename option available
- User must use terminal or external tools to rename files

**Expected Behavior:**
- Right-click on file/folder shows "Rename" option in context menu
- Dialog or inline edit appears with current name pre-filled
- User edits name and confirms
- Backend API handles rename operation
- Tree refreshes automatically after rename
- Error handling for invalid names (path traversal, special chars, duplicates)

**Acceptance Criteria:**
- [ ] Right-click on file/folder shows "Rename" option in context menu
- [ ] Dialog shows input with current filename/foldername pre-filled
- [ ] User can edit name and confirm or cancel
- [ ] Backend API handles rename operation
- [ ] Tree refreshes after successful rename
- [ ] Error handling for:
  - Invalid names (path traversal, special characters)
  - Name conflicts (file/folder already exists)
  - Permission errors
- [ ] Toast notification confirms success/failure

**Technical Notes:**
- Backend API endpoint: `PUT /api/files/{team_id}/rename` or `PATCH /api/files/{team_id}/{path}`
- Frontend: Add "Rename" option to context menu
- Use shadcn/ui Dialog with Input for rename
- Validation: no `../`, no special chars that break file systems
- Handle both files and folders

**Files to Modify:**
- `frontend/components/file-browser/FileTreeItem.tsx` (context menu)
- `backend/app/api/file_routes.py` (rename endpoint - may need to add)

---

### Story 9.4: Escape to Close Dialogs
**Priority:** P2
**Size:** XS
**Status:** TODO

**User Story:**
As a user navigating the application,
I want to press Escape to close any open dialog/modal,
So that I can quickly dismiss dialogs without reaching for the mouse.

**Current Behavior:**
- Dialogs can only be closed by clicking "Cancel" button or X button
- Escape key does nothing
- Forces mouse usage for dismissal

**Expected Behavior:**
- Pressing Escape closes any open dialog/modal
- Works for ALL dialogs:
  - File Search (Cmd+P dialog)
  - Create File/Folder dialog
  - Directory Picker dialog
  - Delete confirmation dialog
  - Rename dialog
- Focus returns to previous element after close
- Escape only closes if not currently editing text (to allow Escape in inputs)

**Acceptance Criteria:**
- [ ] Pressing Escape closes any open dialog/modal
- [ ] Works for all dialogs: file search, create file, directory picker, delete confirmation, rename
- [ ] Focus returns to previous element after close
- [ ] Escape behavior is consistent across all dialogs
- [ ] Does not interfere with Escape key in input fields (e.g., clearing autocomplete)

**Technical Notes:**
- shadcn/ui Dialog component may already support Escape (check default behavior)
- If not built-in, add global keyboard listener or per-dialog escape handlers
- Ensure Escape handler doesn't conflict with other keyboard shortcuts
- Test all dialog types to ensure consistent behavior

**Files to Modify:**
- `frontend/components/file-browser/FileTree.tsx` (Create dialog)
- `frontend/components/file-browser/FileSearch.tsx` (Search dialog)
- `frontend/components/file-browser/FileTreeItem.tsx` (Delete/Rename dialogs)
- Possibly add global keyboard handler in parent component

---

## Sprint Workflow

| Step | Owner | Task | Status |
|------|-------|------|--------|
| 1 | PO | Define sprint backlog | ✅ DONE |
| 2 | TL | Create technical specs for all 4 stories | ⏳ TODO |
| 3 | SM | Assign work to FE/BE based on TL specs | ⏳ TODO |
| 4 | FE | Implement all 4 stories (TDD) | ⏳ TODO |
| 5 | BE | Implement backend endpoints (Delete, Rename) if needed | ⏳ TODO |
| 6 | TL | Code review | ⏳ TODO |
| 7 | QA | Blackbox testing - all acceptance criteria | ⏳ TODO |
| 8 | PO | Accept/reject, demo to Boss | ⏳ TODO |

---

## Technical Context

### File Browser Architecture

**Frontend:**
- `FileTree.tsx` - Main tree component, handles create dialog
- `FileTreeItem.tsx` - Individual file/folder items, context menu
- `FileSearch.tsx` - Cmd+P file search dialog

**Backend:**
- `file_routes.py` - File operation endpoints
- Existing endpoints: GET (list/read), POST (create)
- Needed: DELETE, PUT/PATCH (rename)

**API Endpoints:**

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/files/{team}/list` | GET | List all files | ✅ Exists |
| `/api/files/{team}/{path}` | GET | Read file content | ✅ Exists |
| `/api/files/{team}/create` | POST | Create file/folder | ✅ Exists |
| `/api/files/{team}/delete` | DELETE | Delete file/folder | ❓ TBD |
| `/api/files/{team}/rename` | PUT/PATCH | Rename file/folder | ❓ TBD |

---

## Definition of Done

Sprint 9 is DONE when:
- [ ] All 4 stories implemented
- [ ] TDD followed for all frontend changes (tests written FIRST)
- [ ] Code reviewed and approved by TL
- [ ] All acceptance criteria verified by QA (blackbox testing)
- [ ] QA report: ALL tests PASS
- [ ] PO accepts sprint
- [ ] Boss approves sprint
- [ ] Changes committed and pushed to remote

---

## Notes

**Why File Browser CRUD?**
- Sprint 8 delivered "Create" - users can add files/folders
- Sprint 9 completes the CRUD operations with Delete and Rename
- This makes the file browser a fully functional file manager
- High user value - eliminates need to switch to terminal for basic file operations

**UX Focus:**
- Pre-fill path (Story 9.1) - reduces typing, context-aware
- Confirmation dialogs (Story 9.2) - prevents accidental deletions
- Keyboard shortcuts (Story 9.4) - faster navigation
- All contribute to a polished, professional file browser experience
