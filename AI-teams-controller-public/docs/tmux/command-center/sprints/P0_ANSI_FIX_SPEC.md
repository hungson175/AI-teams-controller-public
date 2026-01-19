# P0 Technical Spec: ANSI Code Stripping for Path Detection

**Author:** TL
**Date:** 2026-01-09
**Priority:** P0
**Size:** XS (~15 lines)

## Problem

`detectFilePaths()` fails on terminal output containing ANSI color codes.
- Input: `"Error in \x1b[34msrc/file.ts\x1b[0m"` → 0 paths detected
- Expected: 1 path detected (`src/file.ts`)

## Solution

Strip ANSI codes from line BEFORE calling `detectFilePaths()`.

## Implementation

### File: `frontend/lib/ansi-parser.ts`

Add new function:

```typescript
/**
 * Strip ANSI escape codes from text
 * Used before regex-based path detection
 */
export function stripAnsi(text: string): string {
  // eslint-disable-next-line no-control-regex
  return text.replace(/\x1b\[[0-9;]*m/g, '')
}
```

### File: `frontend/components/controller/TerminalPanel.tsx`

Line 9: Add import:
```typescript
import { parseAnsiToHtml, stripAnsi } from "@/lib/ansi-parser"
```

Line 403: Change from:
```typescript
const filePaths = detectFilePaths(line)
```

To:
```typescript
const strippedLine = stripAnsi(line)
const filePaths = detectFilePaths(strippedLine)
```

## Test Case

Add to `frontend/lib/ansi-parser.test.ts`:

```typescript
describe("stripAnsi", () => {
  it("should strip ANSI color codes from text", () => {
    const input = "Error in \x1b[34msrc/file.ts\x1b[0m at line 10"
    const result = stripAnsi(input)
    expect(result).toBe("Error in src/file.ts at line 10")
  })
})
```

## Acceptance Criteria

1. Paths with ANSI colors render as clickable TerminalFileLink buttons
2. Existing plain-text path detection still works
3. Unit test for stripAnsi passes

## Verification

After fix, QA re-runs Playwright test - `totalPathButtons > 0`
