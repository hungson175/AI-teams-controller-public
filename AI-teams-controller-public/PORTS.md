# AI Teams Controller - Port Configuration

**Why unusual ports?** Standard development ports (3000, 8000, etc.) commonly conflict with other programs on developer machines. We use non-standard ports to minimize conflicts.

---

## Service Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| **Frontend (Next.js)** | 3337 | HTTP | Web UI interface |
| **Backend (FastAPI)** | 17063 | HTTP | REST API, WebSocket |
| **Terminal Service** | 17073 | HTTP/WS | Web terminal emulator |

---

## Port Selection Rationale

### Frontend: 3337
- **Not 3000**: Standard Next.js port, conflicts with many dev servers
- **Not 3334**: Boss's existing AI Teams Controller instance
- **Chosen 3337**: Uncommon, memorable (3+3+3+7), low conflict risk

### Backend: 17063
- **Not 8000**: Standard FastAPI/uvicorn port, extremely common conflict
- **Not 17061**: Boss's existing backend instance
- **Chosen 17063**: High port number (>10000), memorable pattern (170+63)

### Terminal Service: 17073
- **Not 17071**: Boss's existing terminal service
- **Chosen 17073**: Matches backend pattern (170XX series), sequential

---

## How to Check Ports

### Check if port is in use
```bash
# Linux/macOS
lsof -i :3337
lsof -i :17063
lsof -i :17073

# Or using netstat
netstat -tlnp | grep :3337
```

### Kill process on port
```bash
# Linux/macOS
lsof -ti:3337 | xargs kill -9
lsof -ti:17063 | xargs kill -9
lsof -ti:17073 | xargs kill -9
```

---

## Configuration Files

### Frontend Port
**File**: `frontend/package.json`
```json
{
  "scripts": {
    "dev": "next dev -p 3337",
    "start": "next start -p 3337"
  }
}
```

**File**: `frontend/next.config.mjs`
```javascript
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:17063'
```

### Backend Port
**File**: `backend/app/main.py` (or via command line)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 17063
```

**Restart script**: `scripts/restart-backend.sh`
```bash
PORT=17063
```

### Terminal Service Port
**File**: `terminal-service/server.js`
```javascript
const PORT = process.env.PORT || 17073;
```

**Restart script**: `scripts/restart-terminal.sh`
```bash
PORT=17073
```

---

## Service URLs

### Local Development
- **Frontend**: http://localhost:3337
- **Backend API**: http://localhost:17063
- **Backend Docs**: http://localhost:17063/docs (Swagger UI)
- **Terminal**: http://localhost:17073

### Production (via SSH tunnels)
- **Frontend**: https://voice-ui.hungson175.com → localhost:3337
- **Backend**: https://voice-backend.hungson175.com → localhost:17063
- **Terminal**: https://voice-terminal.hungson175.com → localhost:17073

---

## Troubleshooting

### Port conflict error
```
Error: Port 3337 is already in use
```

**Solution**:
1. Check what's using the port: `lsof -i :3337`
2. Either stop that service or change our port
3. Update configuration files accordingly

### Service not accessible
```
curl: (7) Failed to connect to localhost port 17063: Connection refused
```

**Checklist**:
1. Is service running? `lsof -i :17063`
2. Check service logs: `tail -f /tmp/ai-teams-backend.log`
3. Try restarting: `./scripts/restart-backend.sh`

---

## Changing Ports (if needed)

If you need to change ports, update ALL these locations:

**Frontend Port Change**:
1. `frontend/package.json` - scripts.dev and scripts.start
2. `scripts/restart-frontend.sh` - PORT variable
3. `scripts/restart-all.sh` - show_status function
4. `scripts/test-restart-scripts.sh` - FRONTEND_PORT variable
5. This file (PORTS.md)
6. `CLAUDE.md` - Ports table
7. `README.md` - Installation instructions

**Backend Port Change**:
1. `frontend/next.config.mjs` - backendUrl default
2. `backend/README.md` - uvicorn command examples
3. `scripts/restart-backend.sh` - PORT variable
4. `scripts/restart-all.sh` - show_status function
5. `scripts/test-restart-scripts.sh` - BACKEND_PORT variable
6. This file (PORTS.md)
7. `CLAUDE.md` - Ports table
8. `install-web-ui.sh` - Next steps section

**Terminal Port Change**:
1. `terminal-service/server.js` - PORT default
2. `scripts/restart-terminal.sh` - PORT variable
3. `scripts/restart-all.sh` - show_status function
4. This file (PORTS.md)
5. `CLAUDE.md` - Ports table

---

**Last Updated**: 2026-01-20
**Port Schema**: Frontend 3337, Backend 17063, Terminal 17073
