# Technical Spec: Interactive Terminal Tab

**Sprint:** Terminal Integration (P0)
**Date:** 2026-01-07
**Author:** TL
**Status:** Ready for Review
**Updated:** Tech stack corrected to match POC (Node.js + node-pty)

---

## Overview

Add a 3rd "Terminal" tab next to existing Monitor and Browse tabs. This tab provides an interactive shell (xterm.js) that spawns `/bin/bash` in the project directory.

**Key Constraint:** NO separate login. User is already authenticated via JWT. WebSocket validates JWT and spawns shell directly.

**Tech Stack:** Reuse exact tech from POC (`./sample_codes/web-ssh-terminal/`)
- Frontend: xterm.js (same)
- Backend: Node.js + node-pty (NOT Python pty)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Browser                                                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Role Tab (e.g., TL)                                          │ │
│ │ ┌─────────┬─────────┬─────────┐                              │ │
│ │ │ Monitor │ Browse  │Terminal │  ← NEW TAB                   │ │
│ │ └─────────┴─────────┴─────────┘                              │ │
│ │                                                              │ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ xterm.js                                                  ││ │
│ │ │ $ ls -la                                                  ││ │
│ │ │ total 48                                                  ││ │
│ │ │ drwxr-xr-x  12 user  staff   384 Jan  7 23:30 .           ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
        │
        │ WebSocket (JWT in query param)
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ Terminal Service (Node.js - Separate from FastAPI)              │
│ Port: 17071                                                       │
│                                                                  │
│  /terminal?token=<JWT>                                           │
│        │                                                         │
│        ▼                                                         │
│  ┌──────────────────────────────────────────┐                   │
│  │ JWT Validation (call FastAPI /api/auth/me)│                   │
│  │ - Verify token via main backend           │                   │
│  │ - No additional login required            │                   │
│  └──────────────────────────────────────────┘                   │
│        │ (valid)                                                 │
│        ▼                                                         │
│  ┌──────────────────────────────────────────┐                   │
│  │ node-pty Session                          │                   │
│  │ - pty.spawn('/bin/bash')                  │                   │
│  │ - cwd: PROJECT_ROOT                       │                   │
│  │ - Bidirectional I/O                       │                   │
│  └──────────────────────────────────────────┘                   │
│        │                                                         │
│        ▼                                                         │
│  /bin/bash (project directory)                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Backend Implementation (Node.js Microservice)

### 1. Project Structure

**Location:** `sample_codes/web-terminal/` (new, based on POC)

```
sample_codes/web-terminal/
├── server.js           # Main server (modified from SSH POC)
├── package.json        # Dependencies
└── README.md           # Documentation
```

### 2. Dependencies

**File:** `sample_codes/web-terminal/package.json`

```json
{
  "name": "web-terminal",
  "version": "1.0.0",
  "description": "Local PTY terminal for AI Teams Controller",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^5.2.1",
    "express-ws": "^5.0.2",
    "node-pty": "^1.0.0",
    "ws": "^8.19.0",
    "helmet": "^8.1.0",
    "express-rate-limit": "^8.2.1"
  }
}
```

### 3. Server Implementation

**File:** `sample_codes/web-terminal/server.js`

```javascript
const express = require('express');
const expressWs = require('express-ws');
const pty = require('node-pty');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
expressWs(app);

// Configuration
const PORT = process.env.PORT || 17071;
const PROJECT_ROOT = process.env.PROJECT_ROOT || '/home/hungson175/dev/coding-agents/AI-teams-controller';
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:17061';

// Security headers
app.use(helmet({
  contentSecurityPolicy: false
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
});
app.use(limiter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'web-terminal' });
});

/**
 * Validate JWT token by calling FastAPI backend
 */
async function validateJwt(token) {
  try {
    const response = await fetch(`${FASTAPI_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.ok;
  } catch (error) {
    console.error('JWT validation error:', error);
    return false;
  }
}

/**
 * WebSocket endpoint for terminal
 * No separate login - validates JWT from web app session
 */
app.ws('/terminal', async (ws, req) => {
  const token = req.query.token;

  // Validate JWT before spawning shell
  if (!token) {
    console.log('No token provided');
    ws.close(1008, 'Missing authentication token');
    return;
  }

  const isValid = await validateJwt(token);
  if (!isValid) {
    console.log('Invalid token');
    ws.close(1008, 'Invalid authentication token');
    return;
  }

  console.log('Terminal session started');

  // Spawn PTY with bash in project directory
  const shell = process.platform === 'win32' ? 'powershell.exe' : '/bin/bash';
  const ptyProcess = pty.spawn(shell, [], {
    name: 'xterm-256color',
    cols: 80,
    rows: 24,
    cwd: PROJECT_ROOT,
    env: {
      ...process.env,
      TERM: 'xterm-256color'
    }
  });

  // CRITICAL PATTERN: Receive → Process → Forward
  // Forward PTY output to WebSocket
  ptyProcess.onData((data) => {
    if (ws.readyState === ws.OPEN) {
      ws.send(data);
    }
  });

  ptyProcess.onExit(({ exitCode }) => {
    console.log(`PTY exited with code ${exitCode}`);
    if (ws.readyState === ws.OPEN) {
      ws.close();
    }
  });

  // Handle WebSocket messages
  ws.on('message', (msg) => {
    try {
      // Try to parse as JSON for resize events
      const data = JSON.parse(msg);
      if (data.type === 'resize') {
        ptyProcess.resize(data.cols, data.rows);
        console.log(`Terminal resized to ${data.cols}x${data.rows}`);
      }
    } catch (e) {
      // Not JSON - forward as terminal input
      ptyProcess.write(msg.toString());
    }
  });

  ws.on('close', () => {
    console.log('WebSocket closed, killing PTY');
    ptyProcess.kill();
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
    ptyProcess.kill();
  });
});

app.listen(PORT, () => {
  console.log(`Web terminal server running on http://localhost:${PORT}`);
  console.log(`Project root: ${PROJECT_ROOT}`);
  console.log(`FastAPI backend: ${FASTAPI_URL}`);
});
```

### 4. Running the Service

```bash
# Start terminal service
cd sample_codes/web-terminal
npm install
npm start

# Or with environment variables
PORT=3381 PROJECT_ROOT=/path/to/project npm start
```

---

## Frontend Implementation

### 1. Install xterm.js (Already in POC)

Frontend already uses xterm.js from POC. If not installed:

```bash
cd frontend && pnpm add xterm @xterm/addon-fit @xterm/addon-web-links
```

### 2. New Terminal Component

**File:** `frontend/components/terminal/InteractiveTerminal.tsx` (NEW)

```tsx
"use client"

import { useEffect, useRef, useCallback } from "react"
import { Terminal } from "xterm"
import { FitAddon } from "@xterm/addon-fit"
import { WebLinksAddon } from "@xterm/addon-web-links"
import "xterm/css/xterm.css"

interface InteractiveTerminalProps {
  /** JWT token for authentication */
  token: string
  /** Whether the terminal tab is visible */
  isVisible: boolean
}

// Terminal service port (Node.js microservice)
const TERMINAL_PORT = 17071

export function InteractiveTerminal({ token, isVisible }: InteractiveTerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null)
  const xtermRef = useRef<Terminal | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const fitAddonRef = useRef<FitAddon | null>(null)

  const connect = useCallback(() => {
    if (!terminalRef.current || !token) return

    // Create terminal
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: "#1e1e1e",
        foreground: "#d4d4d4",
        cursor: "#ffffff",
      },
    })

    // Add addons
    const fitAddon = new FitAddon()
    terminal.loadAddon(fitAddon)
    terminal.loadAddon(new WebLinksAddon())

    // Mount terminal
    terminal.open(terminalRef.current)
    fitAddon.fit()

    xtermRef.current = terminal
    fitAddonRef.current = fitAddon

    // Connect to Node.js terminal service (NOT FastAPI)
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    const wsUrl = `${wsProtocol}//${window.location.hostname}:${TERMINAL_PORT}/terminal?token=${encodeURIComponent(token)}`

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      // Send initial size
      const { cols, rows } = terminal
      ws.send(JSON.stringify({ type: "resize", cols, rows }))
    }

    ws.onmessage = (event) => {
      terminal.write(event.data)
    }

    ws.onclose = () => {
      terminal.write("\r\n\x1b[31mConnection closed\x1b[0m\r\n")
    }

    // Forward terminal input to WebSocket
    terminal.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data)
      }
    })

    // Handle resize
    terminal.onResize(({ cols, rows }) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "resize", cols, rows }))
      }
    })

    // Handle window resize
    const handleResize = () => {
      if (fitAddonRef.current) {
        fitAddonRef.current.fit()
      }
    }
    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      ws.close()
      terminal.dispose()
    }
  }, [token])

  useEffect(() => {
    if (isVisible) {
      const cleanup = connect()
      return cleanup
    }
  }, [isVisible, connect])

  // Fit terminal when tab becomes visible
  useEffect(() => {
    if (isVisible && fitAddonRef.current) {
      setTimeout(() => fitAddonRef.current?.fit(), 100)
    }
  }, [isVisible])

  return (
    <div
      ref={terminalRef}
      className="h-full w-full bg-[#1e1e1e]"
      style={{ minHeight: "400px" }}
    />
  )
}
```

### 3. Add Terminal Tab to TmuxController

**File:** `frontend/components/controller/TmuxController.tsx`

```tsx
// 1. Import
import { Terminal as TerminalIcon } from "lucide-react"
import { InteractiveTerminal } from "@/components/terminal/InteractiveTerminal"

// 2. Update ViewMode type
type ViewMode = "monitor" | "browse" | "terminal"

// 3. Add tab trigger (after Browse TabsTrigger, around line 848-851)
<TabsTrigger value="terminal" className="gap-1.5 text-xs data-[state=active]:bg-background">
  <TerminalIcon className="h-3.5 w-3.5" />
  Terminal
</TabsTrigger>

// 4. Add tab content (after Browse TabsContent)
<TabsContent value="terminal" className="flex-1 mt-0 flex flex-col min-h-0">
  <InteractiveTerminal
    token={authToken}  // Get from auth context
    isVisible={viewMode === "terminal"}
  />
</TabsContent>
```

---

## Acceptance Criteria

| # | Criteria | Test |
|---|----------|------|
| 1 | 3rd tab "Terminal" appears | Visual check |
| 2 | Clicking Terminal shows xterm.js | Visual check |
| 3 | Shell opens in project directory | Run `pwd`, expect PROJECT_ROOT |
| 4 | Can run commands | Run `ls`, `git status`, etc. |
| 5 | Colors work | Run `ls --color` |
| 6 | Cursor/history works | Arrow keys navigate history |
| 7 | Each role has own terminal | Switch roles, terminals are independent |
| 8 | No separate login | Terminal works immediately after web login |
| 9 | Scrolling works | Scroll through long output |

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Auth bypass | JWT validated via FastAPI /api/auth/me |
| Path traversal | Shell starts in PROJECT_ROOT (user can cd, expected) |
| Resource exhaustion | Rate limiting in terminal service |
| Session cleanup | PTY killed on WebSocket disconnect |

**Note:** Per Boss requirement, no directory restriction enforced. User already has machine access.

---

## Deployment

### Running the Terminal Service

```bash
# Option 1: Direct (development)
cd sample_codes/web-terminal && npm start

# Option 2: Background process
cd sample_codes/web-terminal && nohup npm start > /tmp/web-terminal.log 2>&1 &

# Option 3: systemd/launchd (production)
# Create service file similar to other services
```

### Service Ports

| Service | Port |
|---------|------|
| Frontend (Next.js) | 3334 |
| Backend (FastAPI) | 17061 |
| **Terminal (Node.js)** | **17071** (NEW) |

---

## Code Coverage Requirements

| Component | Target |
|-----------|--------|
| Backend (server.js) | 80% |
| Frontend (InteractiveTerminal.tsx) | 70% |

---

## Effort Estimate

| Task | Hours |
|------|-------|
| BE: Modify POC to local PTY | 2-3h |
| BE: JWT validation integration | 1h |
| FE: xterm.js component | 2-3h |
| FE: Tab integration | 1h |
| Testing | 2h |
| **Total** | **8-10h** |

---

## Files to Create/Modify

### New Files
- `sample_codes/web-terminal/server.js`
- `sample_codes/web-terminal/package.json`
- `frontend/components/terminal/InteractiveTerminal.tsx`

### Modified Files
- `frontend/components/controller/TmuxController.tsx` (add tab)
- `frontend/package.json` (add xterm deps if not present)

---

## Implementation Order

1. **BE:** Create `sample_codes/web-terminal/` based on SSH POC
2. **BE:** Replace SSH with node-pty local shell
3. **BE:** Add JWT validation via FastAPI call
4. **BE:** Test service standalone
5. **FE:** Create `InteractiveTerminal.tsx` component
6. **FE:** Add Terminal tab to `TmuxController.tsx`
7. **Test:** Manual testing of full flow
8. **Test:** Write unit tests

---

## Key Differences from SSH POC

| Aspect | SSH POC | Terminal Service |
|--------|---------|------------------|
| Connection | SSH to remote server | Local PTY |
| Auth | SSH username/password | JWT from web app |
| Library | ssh2 | node-pty |
| Port | 3380 | 17071 |
| Use case | Remote server access | Local shell in project dir |

---

**End of Technical Spec**
