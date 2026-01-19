# Technical Specs: Sprint 1 - UI/UX Polish

**Author**: TL (Tech Lead)
**Date**: 2025-12-29
**Sprint**: 1 - UI/UX Polish

---

## Story 1: Responsive Tmux Width

### Overview
Recalculate terminal pane width dynamically based on container width to fix line wrapping issues. Currently, lines wrap at 3-4 characters because the backend's tmux capture uses a fixed column width that doesn't match the web UI width.

### Problem Analysis

**Root Cause**: The backend captures pane content with `-J` flag which joins wrapped lines, but tmux wraps based on its internal column width (often 80 chars default). When the web UI container is narrower or wider, text appears incorrectly wrapped.

**Current State** (`TerminalPanel.tsx:421`):
```tsx
<pre className="whitespace-pre-wrap break-words text-foreground/90">
```
- `whitespace-pre-wrap` preserves newlines but wraps at container edge
- No explicit column/width calculation
- No ResizeObserver for dynamic updates

### Architecture

#### Frontend Changes

**File**: `frontend/components/controller/TerminalPanel.tsx`

1. **Add ResizeObserver hook** to track container width
2. **Calculate terminal columns** based on:
   - Container width (pixels)
   - Character width (measure monospace char via hidden span)
   - Formula: `columns = Math.floor(containerWidth / charWidth)`
3. **Debounce resize events** (200-300ms) to prevent excessive recalculations
4. **Expose columns via callback** to parent for backend sync (optional optimization)

**New hook**: `frontend/hooks/useTerminalResize.ts`
```typescript
interface UseTerminalResizeOptions {
  debounceMs?: number  // default: 250
}

interface UseTerminalResizeReturn {
  containerRef: React.RefObject<HTMLDivElement>
  columns: number
  width: number
}

function useTerminalResize(options?: UseTerminalResizeOptions): UseTerminalResizeReturn
```

**Implementation approach**:
```typescript
// Measure character width using a hidden monospace span
const measureCharWidth = (element: HTMLElement): number => {
  const span = document.createElement('span')
  span.style.fontFamily = 'monospace'
  span.style.fontSize = getComputedStyle(element).fontSize
  span.style.visibility = 'hidden'
  span.style.position = 'absolute'
  span.textContent = 'M'  // Use 'M' for accurate monospace measurement
  document.body.appendChild(span)
  const width = span.getBoundingClientRect().width
  document.body.removeChild(span)
  return width
}
```

**Debounce implementation**:
```typescript
// Custom debounce or use lodash.debounce
const debounce = <T extends (...args: unknown[]) => void>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout | null = null
  return (...args: Parameters<T>) => {
    if (timeoutId) clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}
```

#### CSS Changes

**File**: `frontend/components/controller/TerminalPanel.tsx`

Replace current `<pre>` styling:
```tsx
// BEFORE
<pre className="whitespace-pre-wrap break-words text-foreground/90">

// AFTER
<pre
  className="whitespace-pre font-mono text-foreground/90"
  style={{
    overflowX: 'auto',
    wordBreak: 'normal',
    overflowWrap: 'normal'
  }}
>
```

Key changes:
- `whitespace-pre` (not pre-wrap) - preserves all whitespace exactly
- `overflowX: auto` - horizontal scroll if content exceeds width
- Remove `break-words` - don't force word breaks

### API Contract

No backend changes required for Story 1. Frontend-only changes.

**Optional Future Enhancement**: Pass calculated columns to backend via WebSocket to have tmux resize the pane dynamically. Not in scope for Story 1.

### Test Cases (TDD)

#### Unit Tests (`useTerminalResize.test.ts`)

1. **calculates columns based on container width**
   - Mock container with 800px width
   - Mock char width as 8px
   - Expect columns = 100

2. **debounces resize events**
   - Trigger multiple resize events rapidly
   - Verify callback only fires once after debounce delay

3. **updates columns on window resize**
   - Initial: 800px width
   - Resize to 600px
   - Verify columns updated after debounce

4. **handles zero/small container width gracefully**
   - Container with 0px width
   - Should return minimum columns (e.g., 40)

5. **cleans up ResizeObserver on unmount**
   - Mount component, trigger resize
   - Unmount component
   - Verify no memory leaks (observer disconnected)

#### Integration Tests (`TerminalPanel.test.tsx`)

6. **renders terminal content without forced wrapping**
   - Long line of text (100 chars)
   - Verify horizontal scroll appears, no mid-word breaks

7. **preserves newlines in terminal output**
   - Multi-line output with explicit `\n`
   - Each line on separate line in DOM

### Acceptance Criteria

- [ ] Lines no longer wrap at 3-4 characters
- [ ] Long lines show horizontal scroll instead of breaking
- [ ] Resize events are debounced (no lag during resize)
- [ ] Terminal output respects natural line breaks from tmux
- [ ] Works on mobile (narrower viewport)

---

## Story 2: Beautiful Terminal Display (ANSI Colors)

### Overview
Render ANSI escape sequences (colors, bold, etc.) in terminal output to match real tmux appearance.

### Problem Analysis

**Root Cause**: Backend `tmux_service.py` uses `capture-pane -p -J -S` but **missing `-e` flag** which preserves escape sequences.

**Current Backend** (`backend/app/services/tmux_service.py:320`):
```python
success, output = self._run_tmux([
    "capture-pane",
    "-t", target,
    "-p",       # Print to stdout
    "-J",       # Join wrapped lines
    "-S", f"-{self.capture_lines}",
])
```

**With `-e` flag**, tmux output includes:
- `\x1b[1m` - Bold
- `\x1b[0m` - Reset
- `\x1b[38;2;R;G;Bm` - 24-bit RGB foreground color
- `\x1b[48;2;R;G;Bm` - 24-bit RGB background color
- `\x1b[31m` to `\x1b[37m` - Basic foreground colors
- And many more...

### Architecture

#### Backend Changes

**File**: `backend/app/services/tmux_service.py`

Add `-e` flag to capture-pane commands:

```python
# In get_pane_state() - line ~320
success, output = self._run_tmux([
    "capture-pane",
    "-t", target,
    "-p",       # Print to stdout
    "-e",       # NEW: Include escape sequences
    "-J",       # Join wrapped lines
    "-S", f"-{self.capture_lines}",
])

# In _check_pane_activity() - line ~238
success, output = self._run_tmux([
    "capture-pane", "-t", target, "-p", "-e", "-J", "-S", f"-{self.capture_lines}"
])
```

#### Frontend Changes

**Option A: Use `ansi-to-html` library (RECOMMENDED)**

**New dependency**: `pnpm add ansi-to-html`

This is a lightweight, well-tested library specifically for converting ANSI to HTML.

**File**: `frontend/lib/ansi-parser.ts`
```typescript
import AnsiToHtml from 'ansi-to-html'

// Create singleton converter with our color scheme
const converter = new AnsiToHtml({
  fg: '#e5e5e5',      // Default foreground (matches --foreground)
  bg: 'transparent',  // Transparent background
  escapeXML: true,    // Escape HTML entities for security
  stream: false,      // Not streaming mode
})

export function parseAnsiToHtml(text: string): string {
  return converter.toHtml(text)
}
```

**File**: `frontend/components/controller/TerminalPanel.tsx`

Update `renderOutput` function:
```tsx
import { parseAnsiToHtml } from '@/lib/ansi-parser'

const renderOutput = (output: string, highlightText?: string | null): ReactNode => {
  // Parse ANSI codes to HTML
  const htmlContent = parseAnsiToHtml(output)

  // If highlighting needed, apply after ANSI parsing
  const finalContent = highlightText
    ? htmlContent.replace(
        new RegExp(escapeRegex(highlightText), 'g'),
        `<span class="highlight-message bg-yellow-500/20 text-yellow-200 px-1 rounded">${highlightText}</span>`
      )
    : htmlContent

  // Use dangerouslySetInnerHTML since ansi-to-html escapes content
  return (
    <span dangerouslySetInnerHTML={{ __html: finalContent }} />
  )
}
```

**Option B: Custom ANSI parser (NOT recommended)**

More work, more bugs. Only if external dependency is blocked.

#### CSS Additions

**File**: `frontend/app/globals.css` or inline in TerminalPanel

```css
/* Terminal ANSI color classes generated by ansi-to-html */
.ansi-bright-black { color: #666666; }
.ansi-bright-red { color: #ff5555; }
.ansi-bright-green { color: #55ff55; }
.ansi-bright-yellow { color: #ffff55; }
.ansi-bright-blue { color: #5555ff; }
.ansi-bright-magenta { color: #ff55ff; }
.ansi-bright-cyan { color: #55ffff; }
.ansi-bright-white { color: #ffffff; }

/* ansi-to-html uses inline styles, but we might need overrides */
.terminal-output span[style*="font-weight: bold"] {
  font-weight: 600;
}
```

### API Contract

**Backend Response** (unchanged structure, updated content):

```json
{
  "output": "\u001b[1mBold text\u001b[0m and \u001b[32mgreen text\u001b[0m",
  "lastUpdated": "2025-12-29T10:48:00Z",
  "isActive": true
}
```

The `output` field now contains raw ANSI escape sequences instead of stripped text.

### Test Cases (TDD)

#### Backend Tests (`test_tmux_service.py`)

1. **get_pane_state captures ANSI sequences**
   - Mock tmux output with ANSI codes
   - Verify output string contains escape sequences

2. **ANSI sequences pass through WebSocket unchanged**
   - Send state with ANSI via WebSocket
   - Verify client receives intact escape sequences

#### Frontend Tests (`ansi-parser.test.ts`)

3. **parses bold text**
   - Input: `"\x1b[1mBold\x1b[0m"`
   - Output contains: `<span style="font-weight:bold">Bold</span>`

4. **parses basic foreground colors**
   - Input: `"\x1b[31mRed\x1b[0m"`
   - Output contains styled span with red color

5. **parses 24-bit RGB colors**
   - Input: `"\x1b[38;2;255;128;0mOrange\x1b[0m"`
   - Output contains span with rgb(255,128,0)

6. **escapes HTML entities** (SECURITY)
   - Input: `"<script>alert('xss')</script>"`
   - Output: `&lt;script&gt;...`

7. **handles nested styles**
   - Input: `"\x1b[1m\x1b[32mBold Green\x1b[0m"`
   - Both bold and color applied

#### Integration Tests (`TerminalPanel.test.tsx`)

8. **renders colored terminal output**
   - Provide output with ANSI color codes
   - Verify colored spans in DOM

9. **preserves user request highlighting with ANSI**
   - Line starting with `>` should be highlighted
   - ANSI colors within highlighted line still work

### Acceptance Criteria

- [ ] Terminal shows colors matching real tmux
- [ ] Bold text appears bold
- [ ] 24-bit colors (RGB) render correctly
- [ ] No XSS vulnerabilities from ANSI parsing
- [ ] Text search/highlighting still works with colors
- [ ] Performance acceptable (no lag on large outputs)

---

## Implementation Order

**Recommendation**: Implement Story 2 FIRST because:
1. Backend change is trivial (add `-e` flag)
2. Frontend ANSI parsing is independent of resize logic
3. Provides immediate visual improvement

**Story 2 (ANSI Colors)**:
1. BE: Add `-e` flag to tmux_service.py (5 min)
2. FE: Add ansi-to-html dependency (2 min)
3. FE: Create ansi-parser.ts utility (15 min)
4. FE: Update TerminalPanel renderOutput (30 min)
5. Tests: Backend + Frontend (1 hour)

**Story 1 (Responsive Width)**:
1. FE: Create useTerminalResize hook (1 hour)
2. FE: Update TerminalPanel CSS (30 min)
3. Tests: Hook + Integration (1 hour)

---

## Files to Modify

### Story 1
- `frontend/hooks/useTerminalResize.ts` (NEW)
- `frontend/hooks/useTerminalResize.test.ts` (NEW)
- `frontend/components/controller/TerminalPanel.tsx`
- `frontend/components/controller/TerminalPanel.test.tsx`

### Story 2
- `backend/app/services/tmux_service.py`
- `backend/tests/test_tmux_service.py`
- `frontend/package.json` (add ansi-to-html)
- `frontend/lib/ansi-parser.ts` (NEW)
- `frontend/lib/ansi-parser.test.ts` (NEW)
- `frontend/components/controller/TerminalPanel.tsx`
- `frontend/components/controller/TerminalPanel.test.tsx`

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| ANSI parser XSS vulnerability | Use `escapeXML: true` in ansi-to-html |
| Performance with large outputs | Lazy render, virtualize if needed |
| Resize observer memory leaks | Proper cleanup in useEffect |
| ansi-to-html bundle size | It's 8KB minified, acceptable |

---

**TL Sign-off**: Specs complete. Ready for FE/BE implementation with TDD.
