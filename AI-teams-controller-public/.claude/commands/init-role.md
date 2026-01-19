# Initialize Agent Role

You are initializing as a member of an AI Controller Multi-Agent Team.

## Step 1: Detect Team

Based on the tmux session name, determine which team you belong to:
- **command-center**: Standard Scrum team (PO, SM, TL, FE, BE, QA)
- **ai_controller_full_team**: Full 6-agent team (PM, SA, BE, FE, CR, DK)
- **AI-controller-app-PM**: 3-agent team (PM, CR, TESTER)

Check with:
```bash
tmux display-message -p '#S'
```

## Step 2: Read System Documentation

Read the appropriate team overview:

**For command-center**:
- **File**: `docs/tmux/command-center/workflow.md`

**For ai_controller_full_team**:
- **File**: `docs/tmux/ai_controller_full_team/tmux-team-overview.md`

**For AI-controller-app-PM**:
- **File**: `docs/tmux/AI-controller-app-PM/README.md`

## Step 3: Read Your Role Prompt

Based on the role argument `$ARGUMENTS`, read your specific role prompt:

**For command-center (6-agent)**:
- **SM** (Scrum Master): `docs/tmux/command-center/prompts/SM_PROMPT.md`
- **PO** (Product Owner): `docs/tmux/command-center/prompts/PO_PROMPT.md`
- **TL** (Tech Lead): `docs/tmux/command-center/prompts/TL_PROMPT.md`
- **FE** (Frontend Engineer): `docs/tmux/command-center/prompts/FE_PROMPT.md`
- **BE** (Backend Engineer): `docs/tmux/command-center/prompts/BE_PROMPT.md`
- **QA** (Tester): `docs/tmux/command-center/prompts/QA_PROMPT.md`

**For ai_controller_full_team (6-agent)**:
- **PM** (Project Manager): `docs/tmux/ai_controller_full_team/prompts/PM_PROMPT.md`
- **SA** (Solution Architect): `docs/tmux/ai_controller_full_team/prompts/SA_PROMPT.md`
- **BE** (Backend Engineer): `docs/tmux/ai_controller_full_team/prompts/BE_PROMPT.md`
- **FE** (Frontend Engineer): `docs/tmux/ai_controller_full_team/prompts/FE_PROMPT.md`
- **CR** (Code Reviewer): `docs/tmux/ai_controller_full_team/prompts/CR_PROMPT.md`
- **DK** (Document Keeper): `docs/tmux/ai_controller_full_team/prompts/DK_PROMPT.md`

**For AI-controller-app-PM (3-agent)**:
- **PM** (Project Manager): `docs/tmux/AI-controller-app-PM/prompts/PM_PROMPT.md`
- **CR** (Code Reviewer): `docs/tmux/AI-controller-app-PM/prompts/CR_PROMPT.md`
- **TESTER**: `docs/tmux/AI-controller-app-PM/prompts/TESTER_PROMPT.md`

## Step 4: Understand Your Mission

After reading both files:
1. Confirm your role and responsibilities
2. Verify your communication pane IDs are configured
3. Check the WHITEBOARD for current sprint status
4. Be ready to execute your role in the workflow

## Step 5: Announce Readiness

After initialization, announce:
```
[ROLE] initialized and ready.
Team: [team name]
WHITEBOARD status: [status from WHITEBOARD.md]
Awaiting directives.
```

**Who each role awaits:**

For command-center:
- **PO**: Awaits Boss requirements (PO is first contact with stakeholders!)
- **SM**: Awaits PO to define sprint backlog
- **TL**: Awaits design requests from PO
- **FE/BE**: Await SM to assign sprint work with TL specs
- **QA**: Awaits SM to request testing

For PM-based teams (ai_controller_full_team, AI-controller-app-PM):
- **PM**: Awaits Boss directives (PM is first contact)
- **Others**: Await PM to assign work
