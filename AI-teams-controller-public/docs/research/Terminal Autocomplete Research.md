# Terminal Autocomplete Research

**Date:** 2025-12-29
**Purpose:** Research for Sprint 2 - Terminal-like input with autocomplete
**Note:** This research was done prematurely by PO. TL should review and make final technology decision.

---

## Top 3 Solutions

### Option 1: xterm.js + local-echo (Recommended for Full Terminal)

**What:** Industry-standard terminal emulator (used by VS Code, Hyper)

**Pros:**
- Full terminal emulation with ANSI colors
- Tab completion via local-echo addon
- Command history support
- Battle-tested, actively maintained

**Cons:**
- Heavier bundle (~200KB)
- More complex setup
- No built-in autocomplete (requires addon)

**Links:**
- https://xtermjs.org/
- https://github.com/wavesoft/local-echo

---

### Option 2: Custom Implementation with Fuzzy Search

**What:** Build from scratch using fuzzy matching library

**Pros:**
- Lightweight
- Full control over UX
- Easy React integration

**Cons:**
- More development effort
- Need to implement all features manually

**Recommended Libraries:**
- `@nozbe/microfuzz` (2KB, fastest)
- `fuse.js` (most popular, feature-rich)

---

### Option 3: react-terminal-component

**What:** React component with built-in autocomplete

**Pros:**
- Tab completion out of the box
- Command history included
- Easy to integrate

**Cons:**
- Less actively maintained
- Less flexible than xterm.js

**Link:** https://github.com/rohanchandra/react-terminal-component

---

## Key Features Needed

1. **Tab completion** - Complete commands/paths on Tab key
2. **Command history** - Up/Down arrow to navigate history
3. **Path autocomplete** - Backend API for file system paths
4. **Fuzzy matching** - Smart matching for commands
5. **Dropdown UI** - Show suggestions visually

---

## TL Decision Required

TL should evaluate:
1. Which solution fits our architecture best
2. Integration complexity with existing TerminalPanel
3. Backend changes needed for path autocomplete API
4. Bundle size impact

---

## Sources

- xterm.js: https://xtermjs.org/
- local-echo: https://github.com/wavesoft/local-echo
- microfuzz: https://github.com/Nozbe/microfuzz
- fuse.js: https://www.fusejs.io/
- react-terminal-component: https://github.com/rohanchandra/react-terminal-component
