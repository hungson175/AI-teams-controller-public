# Code Quality Review

Findings (ordered by severity):
- **Auth bypass/mismatch**: `backend/app/main.py:36-89` and `backend/app/api/auth_routes.py:218-243` keep a hardcoded `SESSION_TOKEN` and mark most `/api/*` prefixes (teams, send, state, voice) as unprotected. This leaves most endpoints effectively unauthenticated despite JWT support elsewhere, and the token isn’t configurable. Clarify the intended auth model or gate these routes with JWT before shipping broadly.
- **Stop-hook contract bug**: `backend/app/models/voice_schemas.py:107-122` requires `team_id` and `role_id` in the JSON body even though they’re already path params. If the Stop hook sends only `session_id` and `transcript_path`, the endpoint 422s (observed). Either drop the body fields or make them optional/validated against the path to avoid brittle integrations.
- **CORS configuration risk**: `backend/app/main.py:147-160` sets `allow_origins=["*"]` with `allow_credentials=True`. Starlette disallows wildcard with credentials and will fail to send `Access-Control-Allow-Credentials`, causing subtle browser issues and an overly permissive origin policy. Define explicit allowed origins for deployed hosts.
- **Env validation is advisory only**: `backend/app/main.py:23-66` logs missing API keys but continues startup. In prod this yields silent degradation (no summaries/audio) and runtime warnings instead of a fast fail. Consider a `--strict-env` flag or hard fail when required services are enabled.
- **Legacy auth path lingering**: `backend/app/api/auth_routes.py:230-243` exposes `/api/auth/login/simple` with shared secrets and same static token, bypassing JWT flow. If left enabled in prod, it weakens auth; gate it with an env flag or remove once clients migrate.

Questions / follow-ups:
- Should the voice Stop hook accept path params only? If not, we need to update Claude hook payload to include `team_id`/`role_id`.
- Which origins are expected in production? Add them to CORS to avoid wildcard-with-credentials pitfalls.
- Do we intend any endpoints to remain legacy-token only? If not, we can unify on JWT and remove the static token paths.
