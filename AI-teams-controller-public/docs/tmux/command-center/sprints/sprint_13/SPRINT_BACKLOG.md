# Sprint 13 Backlog - Mini IDE Sprint 2

**Sprint Goal:** Syntax Highlighting + Terminal Quick View

**Epic:** Mini Online IDE (P1) - Sprint 2 of 4
**Start Date:** 2026-01-04
**Sprint Duration:** 1-2 days (estimated)
**Team:** FE (Frontend Engineer)

---

## Sprint Overview

**What Boss Can Do After This Sprint:**
- ✅ Everything from Sprint 12 (edit + save files)
- ✅ **NEW**: Professional code editing with syntax highlighting
- ✅ **NEW**: Click file paths in terminal output → quick view popup
- ✅ **STILL USABLE**: Better editing experience with professional editor!

**Value Delivered:**
- Sprint 12: 40% of Mini IDE Epic (basic file editing)
- Sprint 13: **70% of Mini IDE Epic** (professional editing + quick view)
- **30% value jump** with syntax highlighting alone

---

## Product Context

### Why CodeMirror 6?
- **Lightweight**: ~200KB (vs Monaco's ~3MB)
- **Modern**: Built for React/Next.js
- **Extensible**: Modular language support
- **Professional**: Used by Observable, Replit, CodeSandbox

### Progressive Implementation Strategy
Following **product-oriented development** pattern from coder-memory:
- Each work item delivers **fully working feature**, not infrastructure
- Languages added progressively (not all at once)
- UI-first approach: working editor → add languages → add features

---

## Work Items

### Work Item #1: CodeMirror 6 + Core Languages (JS, TS, Python)

**Goal:** Replace textarea with professional code editor supporting 3 most common languages.

**Tasks:**
1. Install CodeMirror 6 dependencies (`@codemirror/state`, `@codemirror/view`, `@codemirror/commands`)
2. Create `CodeEditor` component wrapper (replaces textarea in FileViewer)
3. Implement language auto-detection from file extension (`.js`, `.ts`, `.py`)
4. Add syntax highlighting for:
   - JavaScript (`@codemirror/lang-javascript`)
   - TypeScript (`@codemirror/lang-javascript`)
   - Python (`@codemirror/lang-python`)
5. Apply VS Code-style theme (`@codemirror/theme-one-dark` or similar)
6. Preserve Sprint 12 functionality:
   - Save button still works
   - Cmd+S / Ctrl+S still works
   - Cancel button still works
   - Toast notifications still work
7. **TDD**: Write tests for CodeEditor component

**Acceptance Criteria:**
- [ ] `.js` files open with JavaScript syntax highlighting
- [ ] `.ts` files open with TypeScript syntax highlighting
- [ ] `.py` files open with Python syntax highlighting
- [ ] All Sprint 12 features still work (Save, Cmd+S, Cancel, Toasts)
- [ ] Editor has professional theme (dark mode with syntax colors)
- [ ] Tests: CodeEditor renders, highlights correctly

**Files Modified:**
- `frontend/package.json` (add CodeMirror deps)
- `frontend/components/file-browser/CodeEditor.tsx` (new component)
- `frontend/components/file-browser/FileViewer.tsx` (use CodeEditor instead of textarea)
- `frontend/components/file-browser/CodeEditor.test.tsx` (new tests)

**Size:** M (Medium - similar to Sprint 12 Work Items #2-4)

---

### Work Item #2: Additional Languages (Go, Rust, Java, CSS)

**Goal:** Expand syntax highlighting to cover backend and web languages.

**Tasks:**
1. Add Go language support (`@codemirror/lang-go` or equivalent)
2. Add Rust language support (`@codemirror/lang-rust`)
3. Add Java language support (`@codemirror/lang-java`)
4. Add CSS language support (`@codemirror/lang-css`)
5. Update language auto-detection for `.go`, `.rs`, `.java`, `.css` extensions
6. Verify theme consistency across all languages
7. **TDD**: Add tests for new language highlighting

**Acceptance Criteria:**
- [ ] `.go` files open with Go syntax highlighting
- [ ] `.rs` files open with Rust syntax highlighting
- [ ] `.java` files open with Java syntax highlighting
- [ ] `.css` files open with CSS syntax highlighting
- [ ] All previous languages (JS, TS, Python) still work
- [ ] Theme consistent across all languages

**Files Modified:**
- `frontend/package.json` (add language packages)
- `frontend/components/file-browser/CodeEditor.tsx` (add language imports + detection)
- `frontend/components/file-browser/CodeEditor.test.tsx` (add tests)

**Size:** S (Small - straightforward language additions)

---

### Work Item #3: Final Languages (HTML, Markdown, JSON, YAML)

**Goal:** Complete syntax highlighting for all document and config file types.

**Tasks:**
1. Add HTML language support (`@codemirror/lang-html`)
2. Add Markdown language support (`@codemirror/lang-markdown`)
3. Add JSON language support (`@codemirror/lang-json`)
4. Add YAML language support (`@codemirror/lang-yaml`)
5. Update language auto-detection for `.html`, `.md`, `.json`, `.yaml`, `.yml`
6. Verify all 11 languages work correctly
7. **TDD**: Add tests for final languages

**Acceptance Criteria:**
- [ ] `.html` files open with HTML syntax highlighting
- [ ] `.md` files open with Markdown syntax highlighting
- [ ] `.json` files open with JSON syntax highlighting
- [ ] `.yaml` / `.yml` files open with YAML syntax highlighting
- [ ] **All 11 languages supported**: JS, TS, Python, Go, Rust, Java, CSS, HTML, Markdown, JSON, YAML
- [ ] Tests confirm all languages highlight correctly

**Files Modified:**
- `frontend/package.json` (add final language packages)
- `frontend/components/file-browser/CodeEditor.tsx` (add final languages)
- `frontend/components/file-browser/CodeEditor.test.tsx` (add tests)

**Size:** S (Small - final language additions)

---

### Work Item #4: Terminal File Path Quick View

**Goal:** Parse terminal output for file paths, make them clickable, show quick view popup.

**Tasks:**
1. Create file path regex parser (detect patterns: `/path/to/file.ext`, `./relative/file.js`, `file.py:123`)
2. Create `TerminalFileLink` component:
   - Detects file paths in terminal output
   - Renders as clickable links
   - Handles click → fetch file content
3. Create `QuickViewPopup` modal component:
   - Shows file path as header
   - Renders file content with CodeEditor (syntax highlighting)
   - ESC key to close
   - Click outside to close
4. Integrate with existing terminal output component
5. **TDD**: Write tests for path detection, click behavior, popup

**Acceptance Criteria:**
- [ ] Terminal output shows file paths as clickable links (styled differently)
- [ ] Clicking file path opens quick view popup
- [ ] Popup shows file content with correct syntax highlighting
- [ ] Popup header shows file path
- [ ] ESC key closes popup
- [ ] Click outside popup closes it
- [ ] Tests: Path detection, popup open/close, content display

**Files Modified:**
- `frontend/components/terminal/TerminalFileLink.tsx` (new component)
- `frontend/components/terminal/QuickViewPopup.tsx` (new modal)
- `frontend/components/terminal/TerminalOutput.tsx` (integrate file links)
- `frontend/components/terminal/TerminalFileLink.test.tsx` (new tests)
- `frontend/lib/filePathParser.ts` (new utility for path detection)
- `frontend/lib/filePathParser.test.ts` (new tests)

**Size:** M (Medium - new feature with UI components)

---

## Acceptance Criteria (Sprint Level)

### Core Functionality
- [ ] **AC1**: Files open with syntax highlighting based on extension
- [ ] **AC2**: All 11 languages supported (JS, TS, Python, Go, Rust, Java, CSS, HTML, Markdown, JSON, YAML)
- [ ] **AC3**: CodeMirror editor has professional theme
- [ ] **AC4**: All Sprint 12 features still work (Save, Cmd+S, Cancel, Toasts)

### Terminal Quick View
- [ ] **AC5**: File paths in terminal output are clickable
- [ ] **AC6**: Clicking file path opens popup with file content
- [ ] **AC7**: Popup has syntax highlighting matching file type
- [ ] **AC8**: ESC or click-outside closes popup

### Boss Can Use
- [ ] **AC9**: Boss can edit files with professional syntax highlighting
- [ ] **AC10**: Boss can click terminal file paths to quickly view files
- [ ] **OVERALL**: Professional code editing experience delivered!

---

## Technical Notes

### CodeMirror 6 Architecture
- **State**: Document content, selections, syntax tree
- **View**: Rendering, event handling, UI
- **Extensions**: Language support, themes, commands

### Language Auto-Detection Strategy
```typescript
const getLanguageExtension = (filename: string) => {
  const ext = filename.split('.').pop()?.toLowerCase()

  switch(ext) {
    case 'js': return javascript()
    case 'ts': return javascript({ typescript: true })
    case 'py': return python()
    case 'go': return go()
    // ... etc
    default: return null // plain text
  }
}
```

### File Path Detection Pattern
```typescript
// Matches: /path/to/file.ext, ./relative/file.js, file.py:123
const filePathRegex = /(?:\.\/|\/)?[\w\-\.\/]+\.\w+(?::\d+)?/g
```

---

## Testing Strategy

### Unit Tests
- CodeEditor component renders
- Language detection works correctly
- File path parser detects patterns
- Popup opens/closes on interactions

### Integration Tests
- Full edit flow: Open file → Edit → Save → Verify highlighting
- Terminal click flow: Click path → Popup opens → Shows content → Close

### Manual Testing Checklist
- [ ] Test all 11 languages for highlighting
- [ ] Test Sprint 12 features (Save, Cmd+S, Cancel)
- [ ] Test terminal file path detection
- [ ] Test popup interactions (ESC, click-outside)
- [ ] Test on different file types

---

## Success Metrics

**Sprint 12 Delivered:**
- Basic file editing (40% of epic value)

**Sprint 13 Will Deliver:**
- Professional syntax highlighting (adds 25% value)
- Terminal quick view (adds 5% value)
- **Total: 70% of Mini IDE Epic**

**Remaining for Future Sprints:**
- Sprint 14: Keyboard shortcuts + .env access (adds 15% value)
- Sprint 15: Unsaved changes indicator + auto-save (adds 15% value)

---

## Dependencies

**Frontend:**
- CodeMirror 6 core packages
- Language-specific packages (11 total)
- Theme package

**Backend:**
- No changes required (Sprint 12 PUT endpoint already exists)

---

## Risk Mitigation

**Risk #1: CodeMirror bundle size**
- Mitigation: Use tree-shaking, lazy load language packages
- Fallback: If bundle too large, reduce language count

**Risk #2: Terminal file path parsing false positives**
- Mitigation: Strict regex patterns, validate file exists before showing link
- Fallback: Simple pattern matching, accept some false positives

**Risk #3: All Sprint 12 features break**
- Mitigation: TDD approach, test Sprint 12 features after CodeMirror integration
- Fallback: Keep textarea as backup if CodeMirror causes issues

---

## Definition of Done

- [ ] All 4 work items complete
- [ ] All 10 acceptance criteria PASS
- [ ] TL code review: PASS
- [ ] QA testing: PASS
- [ ] No regressions from Sprint 12
- [ ] Boss demo: Professional editing experience confirmed
- [ ] Git committed and pushed
- [ ] Retrospective complete

---

**Created By:** SM (Scrum Master)
**Date:** 2026-01-04
**Status:** DRAFT (awaiting TL review)
