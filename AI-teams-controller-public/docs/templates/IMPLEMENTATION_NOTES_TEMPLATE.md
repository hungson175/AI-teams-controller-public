# Implementation Notes

**Story**: [Story #X]
**Feature/Fix**: [Brief title]
**Author(s)**: [Engineer names - BE, FE, etc.]
**Completed**: [YYYY-MM-DD]
**PR/Commit**: [Link to PR or commit hash]

---

## Overview

**What was implemented**:
- [High-level summary of changes]
- [Features added/fixed]

**Why**:
- [Business/technical rationale]
- [Problem solved]

**Scope**:
- Backend: [Changed files/modules]
- Frontend: [Changed files/modules]
- Database: [Schema changes, if any]
- Infrastructure: [Config/env changes]

---

## Technical Approach

**Architecture Decision**:
- How did we solve the problem?
- Key design choices made
- Patterns applied (if notable)

**Key Components**:
1. **[Component Name]** (`backend/app/services/...`)
   - Purpose: [What does it do?]
   - Integration: [How does it integrate with other components?]
   - Key methods: [Important public APIs]

2. **[Component Name]** (`frontend/components/...`)
   - Purpose: [What does it do?]
   - State management: [How is state handled?]
   - Integration: [API calls, context usage, etc.]

---

## Implementation Details

### Database Changes
```sql
-- Migration name: [timestamp]
-- Changes made:
ALTER TABLE ...
```

**Migration Status**: [Applied / Pending / Rolled back]
**Backward Compatibility**: [Yes / No] - [Details if breaking]

### API Endpoints (Backend)

| Method | Endpoint | Purpose | Auth | Returns |
|--------|----------|---------|------|---------|
| GET | `/api/...` | [Purpose] | [Token/None] | `[Schema]` |
| POST | `/api/...` | [Purpose] | [Token/None] | `[Schema]` |

### Frontend Integration

**New Components**:
- `frontend/components/.../[Component].tsx` - [Purpose]

**Modified Components**:
- `frontend/components/.../[Component].tsx` - [Changes made]

**New Hooks**:
- `frontend/hooks/[useHook].ts` - [Purpose]

**API Integration**:
```typescript
// Example usage
import { apiCall } from '@/lib/api/...';
const result = await apiCall(...);
```

---

## Testing Strategy

### Unit Tests
- **File**: `backend/tests/test_...py` or `frontend/__tests__/...`
- **Coverage**: [X% - X lines]
- **Key scenarios tested**:
  - [Scenario 1]
  - [Scenario 2]
  - [Scenario 3]

### Integration Tests
- **Tested API endpoints**: [List endpoints tested]
- **Frontend-backend contract verified**: [Yes/No]
- **Cross-component interactions**: [What was tested]

### Manual Testing Performed
- [Test case and result]
- [Test case and result]

---

## Performance Impact

**Changes to critical paths**:
- [API endpoint]: [Before] ms → [After] ms ([+/- X%])
- [Component render time]: [Before] ms → [After] ms

**Database query optimization**:
- [Query]: [Before] → [After] (indexes added: [list])

**Bundle size impact**:
- Frontend bundle: [+/- X KB]
- New dependencies: [List if added]

---

## Known Issues & Limitations

| Issue | Severity | Workaround | Future Improvement |
|-------|----------|-----------|-------------------|
| [Issue] | [High/Med/Low] | [Workaround] | [Plan to fix] |

---

## Deployment Considerations

**Environment Variables** (if new):
- `NEW_VAR`: [Description, default value, required]

**Service Restarts Required**:
- [ ] Backend service
- [ ] Frontend service
- [ ] Celery workers
- [ ] Database migrations

**Feature Flags** (if applicable):
- `feature_flag_name`: [Enabled/Disabled], [Rollout plan]

**Rollback Plan**:
- [How to revert if issues occur]
- [Data cleanup if needed]

---

## Code Review Checkpoints

**Reviewed By**: [CR name]
**Review Date**: [YYYY-MM-DD]
**Changes Requested**: [List, now resolved]
**Approved**: [Yes/No]

---

## Post-Merge Notes

**Merge Date**: [YYYY-MM-DD]
**Merge Commit**: [commit hash]
**Issues Discovered Post-Merge**: [List, if any]

**Production Status**: [In production / Staged / Rolling out]

---

## Lessons Learned

**What Went Well**:
- [Pattern/process that worked well]
- [Reusable solution for future use]

**What Could Be Better**:
- [Challenge faced and how we'd approach it differently]
- [Process improvement opportunity]

**Reusable Patterns**:
- [Code pattern that could be extracted as a utility]
- [Process/workflow improvement]

---

## References & Related Work

- Related stories: [#X, #Y]
- ADRs applied: [ADR-X, ADR-Y]
- External docs: [Links]
- Dependencies updated: [npm packages, Python libs, etc.]
