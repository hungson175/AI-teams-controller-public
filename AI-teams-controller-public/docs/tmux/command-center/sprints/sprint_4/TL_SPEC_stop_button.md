# Technical Spec: Send Special Keys (Stop Button)

**Sprint**: 4
**Created**: 2025-12-29
**Author**: TL

---

## Overview

Add a "Stop" button near the input field that sends the Escape key to the active tmux pane, allowing users to stop Claude Code agents. The implementation uses a dedicated backend endpoint for special keys to avoid conflicts with the Two-Enter rule used for regular messages.

---

## Architecture

### Backend Changes

**New Endpoint**: `POST /api/send-key/{team_id}/{role_id}`

Create a dedicated endpoint for sending special keys (Escape, Enter) without the Two-Enter rule.

**Location**: `backend/app/api/routes.py`

**New Service Method**: `send_special_key(team_id, role_id, key)` in `tmux_service.py`

**Why a new endpoint?**
- Existing `/api/send/{team}/{role}` uses Two-Enter rule (sends message + Enter + Enter)
- Special keys like Escape should be sent ONCE, not followed by Enter
- Cleaner separation of concerns

### Frontend Changes

**Location**: `frontend/components/controller/TerminalPanel.tsx`

**Changes**:
1. Add new `onSendSpecialKey` prop
2. Add Stop button (Square icon) before Send button
3. Button sends Escape key on click

---

## API Contract

### Endpoint: `POST /api/send-key/{team_id}/{role_id}`

**Request**:
```json
{
  "key": "Escape"
}
```

**Supported Keys**: `"Escape"`, `"Enter"`, `"Tab"`, `"C-c"` (Ctrl+C)

**Response (Success)**:
```json
{
  "success": true,
  "message": "Key 'Escape' sent to pane-0 in command-center",
  "sentAt": "2025-12-29T22:00:00.000Z"
}
```

**Response (Error)**:
```json
{
  "success": false,
  "message": "Pane not found: pane-99 in command-center",
  "sentAt": "2025-12-29T22:00:00.000Z"
}
```

---

## Backend Implementation Details

### New Schema: `SendKeyRequest`

**Location**: `backend/app/models/schemas.py`

```python
class SendKeyRequest(BaseModel):
    """Request to send a special key to a pane."""
    key: str = Field(..., description="Special key to send (Escape, Enter, Tab, C-c)")
```

### New Service Method: `send_special_key`

**Location**: `backend/app/services/tmux_service.py`

```python
ALLOWED_SPECIAL_KEYS = {"Escape", "Enter", "Tab", "C-c", "C-d"}

def send_special_key(self, team_id: str, role_id: str, key: str) -> dict:
    """Send a special key to a pane (no Two-Enter rule).

    Args:
        team_id: tmux session name
        role_id: API role ID like "pane-0"
        key: Special key name (Escape, Enter, Tab, C-c)

    Returns:
        dict with success, message, sentAt
    """
    # Validate key
    if key not in ALLOWED_SPECIAL_KEYS:
        return {
            "success": False,
            "message": f"Invalid key: {key}. Allowed: {ALLOWED_SPECIAL_KEYS}",
            "sentAt": datetime.now().isoformat(),
        }

    pane_index = self._get_pane_index(team_id, role_id)
    if pane_index is None:
        return {
            "success": False,
            "message": f"Pane not found: {role_id} in {team_id}",
            "sentAt": datetime.now().isoformat(),
        }

    target = f"{team_id}:0.{pane_index}"

    # Send the special key ONCE (no Two-Enter rule)
    success, output = self._run_tmux(["send-keys", "-t", target, key])

    if not success:
        return {
            "success": False,
            "message": f"Failed to send key: {output}",
            "sentAt": datetime.now().isoformat(),
        }

    return {
        "success": True,
        "message": f"Key '{key}' sent to {role_id} in {team_id}",
        "sentAt": datetime.now().isoformat(),
    }
```

### New Route

**Location**: `backend/app/api/routes.py`

```python
@router.post("/send-key/{team_id}/{role_id}", response_model=SendMessageResponse)
async def send_special_key(
    team_id: str,
    role_id: str,
    request: SendKeyRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """Send a special key to a pane. Requires JWT auth.

    Supported keys: Escape, Enter, Tab, C-c (Ctrl+C)
    Does NOT apply Two-Enter rule - sends key once.
    """
    result = service.send_special_key(team_id, role_id, request.key)
    return result
```

### Base Service Update

**Location**: `backend/app/services/base.py`

Add abstract method to `TeamService`:
```python
@abstractmethod
def send_special_key(self, team_id: str, role_id: str, key: str) -> dict:
    """Send a special key to a pane."""
    pass
```

---

## Frontend Implementation Details

### Props Addition

**Location**: `frontend/components/controller/TerminalPanel.tsx`

Add to `TerminalPanelProps`:
```typescript
/** Callback when special key is sent */
onSendSpecialKey: (key: string) => void
```

### UI Changes

Add Stop button between Mode Toggle and Input:

```tsx
{/* Stop Button - sends Escape to stop agent */}
<Button
  variant="ghost"
  size="icon"
  className="h-10 w-10 shrink-0 text-red-500 hover:text-red-400 hover:bg-red-500/10"
  onClick={() => onSendSpecialKey("Escape")}
  disabled={isPending}
  title="Stop agent (Escape)"
  aria-label="Stop agent"
>
  <Square className="h-4 w-4" />
</Button>
```

**Icon**: Use `Square` from lucide-react (standard stop icon)

**Layout**: `[Mode Toggle] [Stop] [Input] [Send]`

### Handler in TmuxController.tsx

**Location**: `frontend/components/controller/TmuxController.tsx`

```typescript
const handleSendSpecialKey = async (key: string) => {
  if (!selectedTeam || !selectedRole) return

  try {
    const response = await fetch(
      `/api/send-key/${selectedTeam}/${selectedRole}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key }),
      }
    )

    if (!response.ok) {
      console.error("[TmuxController] sendSpecialKey error:", response.status)
    }
  } catch (error) {
    console.error("[TmuxController] Error sending special key:", error)
  }
}
```

### Next.js API Proxy

**Location**: `frontend/app/api/send-key/[team]/[role]/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:17061'

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ team: string; role: string }> }
) {
  const { team, role } = await params
  const body = await request.json()

  const response = await fetch(
    `${BACKEND_URL}/api/send-key/${team}/${role}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify(body),
    }
  )

  const data = await response.json()
  return NextResponse.json(data, { status: response.status })
}
```

---

## Test Cases (for TDD)

### Backend Tests

**Location**: `backend/tests/test_routes.py`

1. **Test send Escape key success**
   - POST `/api/send-key/test-team/pane-0` with `{"key": "Escape"}`
   - Expected: `success: true`, message contains "Escape sent"

2. **Test send Enter key success**
   - POST `/api/send-key/test-team/pane-0` with `{"key": "Enter"}`
   - Expected: `success: true`

3. **Test invalid key rejected**
   - POST `/api/send-key/test-team/pane-0` with `{"key": "InvalidKey"}`
   - Expected: `success: false`, message contains "Invalid key"

4. **Test pane not found**
   - POST `/api/send-key/test-team/pane-99` with `{"key": "Escape"}`
   - Expected: `success: false`, message contains "not found"

5. **Test requires authentication**
   - POST without JWT token
   - Expected: 401 Unauthorized

### Frontend Tests

**Location**: `frontend/components/controller/TerminalPanel.test.tsx`

1. **Test Stop button renders**
   - Check button with aria-label "Stop agent" exists

2. **Test Stop button calls onSendSpecialKey**
   - Click Stop button
   - Verify `onSendSpecialKey("Escape")` called

3. **Test Stop button disabled when isPending**
   - Set `isPending: true`
   - Verify button is disabled

4. **Test Stop button has correct styling**
   - Verify red color classes applied

---

## Acceptance Criteria (from PO)

- [x] "Stop" button visible near the input field (before Send button)
- [x] Clicking "Stop" sends Escape key to active pane
- [x] Visual feedback when key is sent (button state change)
- [x] Works on mobile (touch-friendly size: h-10 w-10)

---

## Implementation Order (for FE/BE)

### BE First:
1. Add `SendKeyRequest` schema
2. Add `send_special_key` method to base service
3. Implement in `TmuxService`
4. Add route `/api/send-key/{team}/{role}`
5. Write tests

### FE Second:
1. Add Next.js API proxy route
2. Add `onSendSpecialKey` prop to TerminalPanel
3. Add Stop button UI
4. Implement handler in TmuxController
5. Write tests

---

## Optional Future Enhancement (P2)

Dropdown/long-press to choose other keys (Enter, Ctrl+C). Not in scope for Sprint 4.
