# Sprint 12 Backlog - Mini IDE Sprint 1: Edit + Save (Simplest Complete Flow)

**Sprint Goal**: Boss can edit and save files directly in browser - NO MORE external editors!

**Epic**: Mini Online IDE - Transform File Browser (P1)
**Started**: 2026-01-03
**Status**: READY TO START

---

## Context

**Epic Reference:** BACKLOG.md lines 571-782 (4 progressive sprints)

**Why Sprint 12:**
- File browser currently supports view-only + CRUD operations (create/delete/rename)
- Users CANNOT edit file contents - must use external editors
- This sprint delivers basic edit + save functionality (simplest complete flow)

**Product-Oriented Approach:**
- Boss has working editor AFTER Sprint 12 (not Sprint 15)
- Start simple (plain text edit), add features later
- Each sprint delivers complete, usable value

---

## What Boss Can Do After This Sprint

- ✅ Click "Edit" button on any file
- ✅ Edit file content in basic text editor
- ✅ Click "Save" button (or Cmd+S / Ctrl+S)
- ✅ Changes persist to disk
- ✅ **ACTUALLY USABLE** - Can edit files without leaving browser!

**Deliberately OUT OF SCOPE (Save for Later Sprints):**
- ❌ NO syntax highlighting yet (plain text - simpler)
- ❌ NO auto-save yet (manual save only - simpler)
- ❌ NO unsaved changes indicator yet (simpler)
- ❌ NO fancy editor features yet (simpler)

**Why This Approach:**
- **Product-Oriented**: Boss has working editor after Sprint 12, not Sprint 15
- **Progressive**: Start simple (plain text edit), add features in Sprint 13-15
- **Risk Reduction**: Validate save workflow early

---

## Work Items

### 1. Backend: File Save Endpoint (BE - Size S)

**File**: `backend/app/api/file_routes.py`

**Requirements:**
- New endpoint: `PUT /api/files/{team}/{path}`
- Request body: File content (text/plain)
- Validate path (no path traversal, protected paths)
- Write content to disk
- Return success/error response

**API Contract:**

**Request:**
```http
PUT /api/files/command-center/docs/test.md
Content-Type: text/plain
Authorization: Bearer {token}

This is the new file content.
Multiple lines supported.
```

**Response (Success):**
```json
{
  "success": true,
  "message": "File saved successfully",
  "path": "docs/test.md",
  "size": 58
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Path traversal detected"
}
```

**Security Requirements:**
- Block path traversal (`../`, absolute paths)
- Block protected paths (`.git/`, `node_modules/`)
- Validate team exists
- File size limit (e.g., 10MB max)
- Proper error handling

**Test Cases (TDD):**
1. Save valid file → 200 OK, file updated on disk
2. Path traversal attempt → 400 Bad Request
3. Protected path attempt → 403 Forbidden
4. File too large → 413 Payload Too Large
5. Invalid team → 404 Not Found

**Acceptance Criteria:**
- [ ] PUT /api/files/{team}/{path} endpoint exists
- [ ] File content written to disk correctly
- [ ] Security validations work (path traversal, protected paths)
- [ ] Proper error messages
- [ ] Tests pass before implementation commit

---

### 2. Frontend: Edit Mode Toggle (FE - Size S)

**File**: `frontend/components/file-browser/FileViewer.tsx`

**Requirements:**
- Add "Edit" button in FileViewer toolbar
- Toggle between view mode and edit mode
- Edit mode shows textarea (plain text for now)
- View mode shows CodeViewer (existing syntax highlighting)
- State management for edit mode boolean

**UI States:**

| Mode | UI Elements | Description |
|------|-------------|-------------|
| View | CodeViewer + "Edit" button | Read-only with syntax highlighting |
| Edit | Textarea + "Save" + "Cancel" buttons | Editable plain text |

**Component State:**
```typescript
const [isEditMode, setIsEditMode] = useState(false);
const [editContent, setEditContent] = useState("");
```

**Test Cases:**
1. Click "Edit" button → switches to edit mode
2. Edit mode shows textarea with file content
3. Click "Cancel" → returns to view mode, discards changes
4. View mode shows original CodeViewer

**Acceptance Criteria:**
- [ ] "Edit" button visible in view mode
- [ ] Click "Edit" → switches to edit mode
- [ ] Edit mode shows textarea with file content
- [ ] "Cancel" button returns to view mode
- [ ] View mode unchanged (still has syntax highlighting)

---

### 3. Frontend: Save Functionality (FE - Size M)

**File**: `frontend/components/file-browser/FileViewer.tsx` (continued)

**Requirements:**
- "Save" button calls PUT /api/files/{team}/{path}
- Keyboard shortcut: Cmd+S / Ctrl+S (only in edit mode)
- Loading state during save
- Toast notification on success/failure
- Return to view mode after successful save

**Save Workflow:**
1. User clicks "Save" or presses Cmd+S
2. Show loading state (disable buttons, show spinner)
3. Call PUT /api/files/{team}/{path} with textarea content
4. On success:
   - Show toast: "File saved successfully"
   - Return to view mode
   - Refresh file content in CodeViewer
5. On error:
   - Show toast with error message
   - Stay in edit mode
   - Allow user to retry

**API Integration:**
```typescript
const handleSave = async () => {
  setIsSaving(true);
  try {
    const response = await fetch(`/api/files/${team}/${path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'text/plain' },
      body: editContent
    });

    if (response.ok) {
      toast.success("File saved successfully");
      setIsEditMode(false);
      // Refresh file content
    } else {
      const error = await response.json();
      toast.error(error.error || "Failed to save file");
    }
  } catch (error) {
    toast.error("Network error: Could not save file");
  } finally {
    setIsSaving(false);
  }
};
```

**Keyboard Shortcut:**
```typescript
useEffect(() => {
  if (!isEditMode) return;

  const handleKeyDown = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      handleSave();
    }
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [isEditMode, editContent]);
```

**Test Cases:**
1. Click "Save" → API called, file saved, returns to view mode
2. Cmd+S / Ctrl+S → same as "Save" button
3. Save fails → error toast shown, stays in edit mode
4. Network error → error toast shown
5. Loading state → buttons disabled during save

**Acceptance Criteria:**
- [ ] "Save" button calls PUT /api/files/{team}/{path}
- [ ] Cmd+S / Ctrl+S works (only in edit mode)
- [ ] Loading state during save (disabled buttons)
- [ ] Success toast on successful save
- [ ] Error toast on failure
- [ ] Returns to view mode after successful save
- [ ] File content refreshed in view mode

---

### 4. Frontend: Cancel Functionality (FE - Size XS)

**File**: `frontend/components/file-browser/FileViewer.tsx` (continued)

**Requirements:**
- "Cancel" button discards changes
- Returns to view mode
- No API call (just local state reset)

**Implementation:**
```typescript
const handleCancel = () => {
  setIsEditMode(false);
  setEditContent(""); // Reset to original content
};
```

**Test Cases:**
1. Edit content → Click "Cancel" → changes discarded
2. Returns to view mode with original content

**Acceptance Criteria:**
- [ ] "Cancel" button discards changes
- [ ] Returns to view mode
- [ ] Original file content shown in view mode

---

## Test Strategy

### Backend Tests (pytest)
- Unit tests for PUT endpoint
- Security validation tests (path traversal, protected paths)
- File write tests (verify content on disk)
- Error handling tests

### Frontend Tests (Jest + React Testing Library)
- Component render tests (view mode, edit mode)
- Button click tests (Edit, Save, Cancel)
- Keyboard shortcut test (Cmd+S)
- API integration tests (mock fetch)
- Toast notification tests

### Manual Testing (QA)
- Edit file in browser
- Save via button and Cmd+S
- Verify changes persist (refresh page)
- Test error scenarios (invalid paths, network errors)
- Test Cancel button (discard changes)

---

## Acceptance Criteria (Sprint 12)

### AC1: Edit Button Available ✅
- [ ] "Edit" button visible in FileViewer (view mode)
- [ ] Click "Edit" → switches to edit mode

### AC2: Edit Mode Functional ✅
- [ ] Edit mode shows textarea with file content
- [ ] User can type and modify content
- [ ] Textarea pre-filled with current file content

### AC3: Save Button Works ✅
- [ ] "Save" button calls PUT /api/files/{team}/{path}
- [ ] File content persisted to disk
- [ ] Success toast shown on save

### AC4: Keyboard Shortcut Works ✅
- [ ] Cmd+S / Ctrl+S saves file (only in edit mode)
- [ ] Shortcut does NOT trigger in view mode

### AC5: Cancel Button Works ✅
- [ ] "Cancel" button discards changes
- [ ] Returns to view mode
- [ ] No API call on cancel

### AC6: Error Handling ✅
- [ ] Network errors show error toast
- [ ] Invalid paths blocked (400 Bad Request)
- [ ] Protected paths blocked (403 Forbidden)
- [ ] User stays in edit mode on error (can retry)

### AC7: Boss Can Use It ✅
- [ ] Boss can click "Edit" on any file
- [ ] Boss can modify content
- [ ] Boss can save with "Save" button or Cmd+S
- [ ] Changes persist (refresh page shows new content)
- [ ] No crashes, clean UX

---

## Dependencies

**No new dependencies required** ✅
- Frontend: Existing React, fetch API, toast library
- Backend: Existing FastAPI, file system access

---

## Team Assignments

| Role | Assigned Work | Status |
|------|--------------|--------|
| BE | Work Item #1: PUT /api/files/{team}/{path} endpoint | ⏳ READY |
| FE | Work Items #2-4: Edit mode, Save, Cancel | ⏳ READY |
| TL | Code review when BE/FE complete | ⏳ READY |
| QA | Blackbox testing | ⏳ READY |

---

## Timeline Estimate

| Task | Effort | Notes |
|------|--------|-------|
| Backend PUT endpoint | S | Standard CRUD endpoint with validation |
| Frontend edit mode toggle | S | Basic state management |
| Frontend save functionality | M | API integration + keyboard shortcuts |
| Frontend cancel button | XS | Simple state reset |

**Total Estimate**: S-M sprint (smaller than Sprint 11 Android)

---

## Definition of Done

- [ ] All 7 acceptance criteria met
- [ ] Backend tests passing (PUT endpoint + security)
- [ ] Frontend tests passing (edit mode, save, cancel)
- [ ] TL code review passed
- [ ] QA blackbox testing passed
- [ ] Boss can edit and save files in browser
- [ ] No external editor needed
- [ ] Code committed to git (progressive commits)
- [ ] Changes pushed to remote after Boss acceptance

---

## Reference

**Epic**: BACKLOG.md lines 571-782 (Mini Online IDE - 4 progressive sprints)
**Sprint 1 Details**: BACKLOG.md lines 597-637

**Next Sprints in Epic:**
- Sprint 13 (Mini IDE Sprint 2): Syntax highlighting + terminal file links quick view
- Sprint 14 (Mini IDE Sprint 3): Keyboard shortcuts + .env file access
- Sprint 15 (Mini IDE Sprint 4): Polish + production ready (unsaved changes, auto-save, line numbers)

---

**Sprint 12 Ready for Execution**
