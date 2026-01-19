# API Specs Review

## Overview
- Goal: confirm mock data lives only in API routes and capture follow-up suggestions.
- Scope: Next.js frontend (`frontend/app`) and API route handlers; backend experiments excluded from UI runtime.

## Findings
- All mock datasets are defined inside API route handlers:
  - `frontend/app/api/teams/route.ts` → `MOCK_TEAMS` (list of team ids/names).
  - `frontend/app/api/teams/[teamId]/roles/route.ts` → `MOCK_ROLES` (role metadata).
  - `frontend/app/api/state/[teamId]/[roleId]/route.ts` → `MOCK_OUTPUTS` and generated scripted responses per role.
- UI surface (`frontend/app/page.tsx`) does not embed mock data; it fetches from the above routes for teams, roles, and pane state.
- Message storage for `/api/send/[teamId]/[roleId]` is an in-memory `Map` scoped to the route module; no mock content defined elsewhere.

## Suggestions / Next Steps
- Add contract coverage (types/tests) for each route to lock response shapes before swapping mocks for real data.
- Introduce simple validation on `teamId`/`roleId` and request bodies to avoid unexpected states when real inputs arrive.
- Persist last messages/responses (or stub an interface) so replacing the in-memory `Map` will not alter endpoint contracts.
- Document expected API evolution (e.g., move to FastAPI, auth requirements) so frontend consumers know upcoming changes.
