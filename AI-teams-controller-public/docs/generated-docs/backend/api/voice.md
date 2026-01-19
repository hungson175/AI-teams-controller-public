# Voice Commands API

Endpoints for speech-to-text and voice command processing.

## Endpoints

### Get Soniox Token

```http
POST /api/voice/token/soniox
```

Returns Soniox API key for frontend STT.

**Response:**
```json
{
  "api_key": "soniox_xxx..."
}
```

### Process Voice Command

```http
POST /api/voice/command/{team_id}/{role_id}
```

Corrects voice transcript using LLM and sends to pane.

**Request:**
```json
{
  "raw_command": "write a function that adds two numbers thank you",
  "transcript": "write a function that adds two numbers",
  "speed": 0.8
}
```

**Response (streaming):**
```json
{"type": "llm_token", "token": "write"}
{"type": "llm_token", "token": " a"}
{"type": "command_sent", "corrected_command": "write a function that adds two numbers"}
```

### Task Done (Stop Hook)

```http
POST /api/voice/task-done/{team_id}/{role_id}
```

Called by Claude Stop hook when task completes. Triggers LLM summary + TTS.

**Request:**
```json
{
  "session_id": "abc123",
  "transcript_path": "/tmp/transcript.md",
  "role_name": "FE"
}
```

### WebSocket: Voice Feedback

```
ws://backend:17061/api/voice/ws/feedback/global
```

Receives voice feedback notifications:

```json
{
  "type": "voice_feedback",
  "summary": "Task completed successfully",
  "audio": "<base64 MP3>"
}
```

## Voice Command Flow

1. Frontend captures audio → Soniox WebSocket STT
2. Stop word detected → `POST /api/voice/command`
3. Backend corrects with grok-4-fast → sends to tmux
4. Claude completes → Stop hook fires → `POST /api/voice/task-done`
5. Celery generates summary + TTS → Redis pub/sub → WebSocket
