"""Mock data service - implements TeamService for testing/development."""

from datetime import datetime
from typing import Optional

from app.services.base import TeamService


class MockDataService(TeamService):
    """Handles mock data for M3 phase. Will be replaced with TmuxService in M4."""

    # Mock teams (tmux sessions)
    MOCK_TEAMS = [
        {"id": "quant-team-v2", "name": "quant-team-v2", "isActive": True},
        {"id": "refactor-dr", "name": "refactor-dr", "isActive": False},
        {"id": "auth-impl-beta", "name": "auth-impl-beta", "isActive": True},
        {"id": "perf-optimization", "name": "perf-optimization", "isActive": False},
    ]

    # Mock roles (tmux panes)
    MOCK_ROLES = [
        {"id": "pm", "name": "PM", "order": 1, "isActive": True},
        {"id": "researcher", "name": "Researcher", "order": 2, "isActive": False},
        {"id": "engineer", "name": "Engineer", "order": 3, "isActive": True},
        {"id": "reviewer", "name": "Code Reviewer", "order": 4, "isActive": False},
    ]

    # Mock terminal outputs for different roles
    MOCK_OUTPUTS = {
        "pm": """$ tmux-team status
Team: Project Management
Status: Active
Last Activity: 2 minutes ago

[PM] Analyzing requirements...
[PM] Current sprint goals:
  - Complete user authentication flow
  - Design database schema
  - Set up CI/CD pipeline

[PM] Blocked items: None
[PM] Next sync: Tomorrow 10:00 AM
[PM] Ready for input...""",
        "researcher": """$ research-agent --mode active
Researcher Agent v1.0
Connected to knowledge base

[Researcher] Current research tasks:
  ✓ Authentication best practices (completed)
  ⟳ Database optimization strategies (in progress)
  ⟳ Scalability patterns for microservices (in progress)

[Researcher] Recent findings:
- JWT tokens with refresh mechanism recommended
- PostgreSQL with proper indexing for our use case
- Consider Redis for caching layer

[Researcher] Awaiting next query...""",
        "engineer": """$ dev-environment status
Development Environment Active
Node: v20.10.0 | TypeScript: 5.3.3

[Engineer] Recent commits:
  ab3d9f2 - Add authentication middleware
  c4e5f89 - Implement user model
  2a1b0c3 - Set up database migrations

[Engineer] Current working on:
  - API endpoint for user registration
  - Input validation with Zod
  - Error handling middleware

[Engineer] Tests: 42 passing, 0 failing
[Engineer] Ready for next task...""",
        "reviewer": """$ code-review --status
Code Review Agent Active
Mode: Automated + Manual

[Reviewer] Recent reviews:
  ✓ Pull Request #23: Authentication system (Approved)
  ⟳ Pull Request #24: Database schema (In Review)

[Reviewer] Code quality metrics:
  - Test Coverage: 87%
  - Linting: No issues
  - Security: No vulnerabilities detected
  - Performance: Good

[Reviewer] Pending reviews: 1
[Reviewer] Feedback:
  - Consider adding rate limiting
  - Add input sanitization for all endpoints

[Reviewer] Standing by for new code...""",
    }

    def __init__(self):
        # In-memory storage for sent messages (same as Next.js version)
        self._sent_messages: dict[str, dict[str, str]] = {}

    def get_teams(self) -> list[dict]:
        """Get all mock teams."""
        return self.MOCK_TEAMS

    def get_roles(self, team_id: str) -> list[dict]:
        """Get all mock roles for a team."""
        return self.MOCK_ROLES

    def send_message(self, team_id: str, role_id: str, message: str) -> dict:
        """Store a sent message and return response."""
        key = f"{team_id}-{role_id}"
        timestamp = datetime.now().strftime("%H:%M")
        self._sent_messages[key] = {"message": message, "timestamp": timestamp}
        return {
            "success": True,
            "message": f"Message sent to {role_id} in {team_id}",
            "sentAt": datetime.now().isoformat(),
        }

    def get_last_message(self, team_id: str, role_id: str) -> Optional[dict]:
        """Get the last sent message for a team/role."""
        key = f"{team_id}-{role_id}"
        return self._sent_messages.get(key)

    def get_pane_state(self, team_id: str, role_id: str) -> dict:
        """Get the pane state with mock output."""
        base_output = self.MOCK_OUTPUTS.get(
            role_id,
            f"""$ tmux pane output
No output available for role: {role_id}
Team: {team_id}
Waiting for commands...""",
        )

        last_message = self.get_last_message(team_id, role_id)
        highlight_text = None

        if last_message:
            responses = self._generate_responses(
                role_id, last_message["message"], last_message["timestamp"]
            )
            base_output += responses
            highlight_text = f"BOSS [{last_message['timestamp']}]: {last_message['message']}"

        # Get isActive status from MOCK_ROLES
        is_active = False
        for role in self.MOCK_ROLES:
            if role["id"] == role_id:
                is_active = role.get("isActive", False)
                break

        return {
            "output": base_output,
            "lastUpdated": datetime.now().strftime("%H:%M:%S"),
            "highlightText": highlight_text,
            "isActive": is_active,
        }

    def set_capture_lines(self, lines: int) -> None:
        """Set capture lines (no-op for mock service).

        Sprint 6 - DIP fix: Mock implementation doesn't use capture_lines.
        """
        pass

    def _generate_responses(self, role_id: str, user_message: str, timestamp: str) -> str:
        """Generate mock agent responses based on role."""
        now = datetime.now()

        def add_minutes(mins: int) -> str:
            from datetime import timedelta

            time = now + timedelta(minutes=mins)
            return time.strftime("%H:%M")

        responses = {
            "pm": [
                f"\n\nBOSS [{timestamp}]: {user_message}",
                f"\n[PM] [{add_minutes(0)}] Acknowledged. Breaking down the requirements...",
                f"[PM] [{add_minutes(0)}] Identified key components:",
                f"[PM] [{add_minutes(0)}]   - Frontend implementation needed",
                f"[PM] [{add_minutes(0)}]   - Backend API endpoints",
                f"[PM] [{add_minutes(0)}]   - Database schema updates",
                f"[PM] [{add_minutes(1)}] Creating task breakdown...",
                f"[PM] [{add_minutes(1)}] Assigning to Engineer for implementation",
                f"[PM] [{add_minutes(1)}] Will coordinate with Researcher for best practices",
                f"[PM] [{add_minutes(2)}] ETA: 2-3 days for full implementation",
            ],
            "researcher": [
                f"\n\nBOSS [{timestamp}]: {user_message}",
                f"\n[Researcher] [{add_minutes(0)}] Received task. Analyzing requirements...",
                f"[Researcher] [{add_minutes(0)}] Searching knowledge base for relevant patterns...",
                f"[Researcher] [{add_minutes(1)}] Found 12 relevant articles and documentation",
                f"[Researcher] [{add_minutes(1)}] Key findings:",
                f"[Researcher] [{add_minutes(1)}]   ✓ React Server Components recommended",
                f"[Researcher] [{add_minutes(1)}]   ✓ Use SWR for client-side data fetching",
                f"[Researcher] [{add_minutes(2)}]   ✓ Implement proper error boundaries",
                f"[Researcher] [{add_minutes(2)}] Cross-referencing with current architecture...",
                f"[Researcher] [{add_minutes(2)}] Preparing detailed recommendations document",
                f"[Researcher] [{add_minutes(3)}] Report ready. Sending to team.",
            ],
            "engineer": [
                f"\n\nBOSS [{timestamp}]: {user_message}",
                f"\n[Engineer] [{add_minutes(0)}] Task received. Setting up development environment...",
                f"[Engineer] [{add_minutes(0)}] $ npm install --save-dev required-packages",
                f"[Engineer] [{add_minutes(1)}] Dependencies installed successfully",
                f"[Engineer] [{add_minutes(1)}] Creating new components...",
                f"[Engineer] [{add_minutes(1)}]   ✓ Created src/components/FeatureX.tsx",
                f"[Engineer] [{add_minutes(2)}]   ✓ Created src/api/feature-endpoint.ts",
                f"[Engineer] [{add_minutes(2)}]   ✓ Added types in src/types/feature.d.ts",
                f"[Engineer] [{add_minutes(2)}] Implementing business logic...",
                f"[Engineer] [{add_minutes(3)}] Running tests...",
                f"[Engineer] [{add_minutes(3)}] $ npm test -- --coverage",
                f"[Engineer] [{add_minutes(4)}] ✓ All tests passing (48/48)",
                f"[Engineer] [{add_minutes(4)}] Ready for code review.",
            ],
            "reviewer": [
                f"\n\nBOSS [{timestamp}]: {user_message}",
                f"\n[Reviewer] [{add_minutes(0)}] Acknowledged. Preparing review checklist...",
                f"[Reviewer] [{add_minutes(0)}] Analyzing proposed implementation approach...",
                f"[Reviewer] [{add_minutes(1)}] Checking against coding standards...",
                f"[Reviewer] [{add_minutes(1)}] Security considerations:",
                f"[Reviewer] [{add_minutes(1)}]   ⚠ Need to validate all user inputs",
                f"[Reviewer] [{add_minutes(1)}]   ⚠ Ensure proper authentication checks",
                f"[Reviewer] [{add_minutes(2)}]   ✓ HTTPS enforcement in place",
                f"[Reviewer] [{add_minutes(2)}] Performance analysis:",
                f"[Reviewer] [{add_minutes(2)}]   ✓ No obvious bottlenecks detected",
                f"[Reviewer] [{add_minutes(3)}]   → Recommend adding pagination for large datasets",
                f"[Reviewer] [{add_minutes(3)}] Will monitor implementation for review.",
            ],
        }

        role_responses = responses.get(role_id)
        if role_responses:
            return "\n".join(role_responses)
        return f"\n\nBOSS [{timestamp}]: {user_message}\n\n[{role_id.upper()}] Processing..."

    # ========== Commander Epic: Team Lifecycle Management ==========

    def kill_team(self, team_id: str) -> dict:
        """Mock kill team - just returns success."""
        return {
            "success": True,
            "message": f"Team '{team_id}' terminated (mock)",
        }

    def restart_team(self, team_id: str) -> dict:
        """Mock restart team - just returns success."""
        return {
            "success": True,
            "message": f"Team '{team_id}' restarted (mock)",
            "setupScriptRun": False,
        }

    def create_terminal(self, name: Optional[str] = None) -> dict:
        """Mock create terminal - just returns success."""
        if not name:
            name = f"terminal-{datetime.now().strftime('%H%M%S')}"
        return {
            "success": True,
            "teamId": name,
            "message": f"Terminal '{name}' created (mock)",
        }

    def list_available_teams(self) -> list[dict]:
        """Mock list available teams - returns mock team directories."""
        return [
            {
                "name": "quant-team-v2",
                "path": "docs/tmux/quant-team-v2",
                "hasSetupScript": True,
                "isActive": True,
            },
            {
                "name": "refactor-dr",
                "path": "docs/tmux/refactor-dr",
                "hasSetupScript": True,
                "isActive": False,
            },
            {
                "name": "ai_controller_full_team",
                "path": "docs/tmux/ai_controller_full_team",
                "hasSetupScript": True,
                "isActive": True,
            },
        ]


# Singleton instance
mock_service = MockDataService()
