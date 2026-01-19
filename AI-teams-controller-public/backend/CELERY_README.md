# Celery Voice Feedback Service

Background task processing for voice feedback generation.

## Architecture

```
[Stop Hook] → [POST /api/voice/task-done] → [Celery Task Queue]
                                                    ↓
                                           [Background Worker]
                                                    ↓
                                           [LLM Summary + TTS]
                                                    ↓
                                           [Redis Pub/Sub] → [All WebSocket Clients]
```

## Prerequisites

1. **Redis** - Message broker and pub/sub
   ```bash
   # macOS
   brew install redis
   brew services start redis

   # Or run directly
   redis-server
   ```

2. **Environment Variables** (in `backend/.env`)
   ```
   REDIS_URL=redis://localhost:6379/0
   OPENAI_API_KEY=sk-...
   XAI_API_KEY=xai-...
   ```

## Running the Services

### 1. Start Redis (if not running)
```bash
redis-server
```

### 2. Start FastAPI Backend
```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 17061 --reload
```

### 3. Start Celery Worker
```bash
cd backend
uv run celery -A celery_config worker --loglevel=info
```

## How It Works

1. **Stop Hook Fires**: When Claude Code completes a task, the Stop hook calls `/api/voice/task-done`

2. **Task Queued**: The endpoint immediately queues a Celery task and returns

3. **Background Processing**: Celery worker picks up the task and:
   - Generates LLM summary (grok-4-fast)
   - Generates TTS audio (OpenAI tts-1)
   - Publishes to Redis pub/sub channel

4. **Broadcast**: FastAPI's pub/sub listener receives the message and broadcasts to ALL connected WebSocket clients

5. **Playback**: Frontend receives the message and plays the audio

## Key Endpoints

- `POST /api/voice/task-done/{team_id}/{role_id}` - Queue voice feedback task
- `WS /api/voice/ws/feedback/global` - Global WebSocket for receiving feedback from all teams
- `WS /api/voice/ws/feedback/{team_id}/{role_id}` - Legacy per-team WebSocket (deprecated)

## Troubleshooting

### Redis Connection Failed
Check Redis is running:
```bash
redis-cli ping
# Should return PONG
```

### Celery Worker Not Processing
Check worker logs:
```bash
uv run celery -A celery_config worker --loglevel=debug
```

### No Voice Feedback
1. Check Stop hook is firing (logs in `/tmp/voice_hook.log`)
2. Check Celery worker received task
3. Check Redis pub/sub is working
4. Check WebSocket is connected (browser console)

## Development Mode (No Redis)

If Redis is not available, the system gracefully degrades:
- Tasks are processed inline in FastAPI (blocking)
- Pub/sub listener fails silently on startup
- Voice feedback still works, just not as scalable
