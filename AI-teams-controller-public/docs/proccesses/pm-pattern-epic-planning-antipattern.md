# PM Pattern: Epic Planning Anti-Pattern - Infrastructure-First Violates Product-Oriented Development

**Status:** Validated Pattern
**Date Created:** 2026-01-03
**Confidence Level:** High
**Frequency:** High (applies to most multi-sprint epics)

---

## Pattern Summary

When breaking down large epics into sprints, developers and PMs naturally gravitate toward **infrastructure-first planning**: build foundation → add features → integrate. This delays user value delivery and violates **Product-Oriented + Progressive Development** principles.

**Key Lesson:** Start with the **SIMPLEST COMPLETE FLOW**, then progressively add capabilities.

---

## Context

- **Scenario:** Multi-agent Scrum team planning Android app epic (5 sprints)
- **Prior Knowledge:** Boss previously taught Product-Oriented + Progressive Development principles
- **What Happened:** I initially planned infrastructure-first despite knowing the principles
- **Realization:** Boss had to remind me of the principle a 2nd time

---

## The Anti-Pattern (What NOT To Do)

### Initial (Wrong) Sprint Breakdown

```
Sprint 10: Voice recording infrastructure
  - Foreground service implementation
  - Wake lock management
  - Result: NO USABLE PRODUCT ❌

Sprint 11: Headphone button support
  - MediaSession API integration
  - Button event handling
  - Result: STILL NO USABLE PRODUCT ❌

Sprint 12: Backend integration
  - Connect to backend API
  - Task management workflow
  - Result: FIRST TIME USABLE (after 3 sprints!) ❌

Sprint 13-14: Additional features
  - TTS feedback
  - Team/role selection
```

### Why This Feels Logical (But Is Wrong)

- "Need foundation before features" - classic bottom-up engineering thinking
- Technical dependencies seem to require sequential building
- Infrastructure work is measurable and concrete
- Feels "organized" to build foundation → features → integrate

### Why This Violates Product-Oriented Development

1. **Zero value delivery until Sprint 12** - Boss and users get nothing for 3 sprints
2. **High risk of wasted work** - If approach is wrong after Sprint 10-11, you've wasted effort
3. **No early validation** - Can't validate assumptions until late in epic
4. **Team morale** - Working for 3 sprints without shipping anything is demoralizing
5. **Violates Progressive Development** - Should deliver SOME value every sprint

---

## The Pattern (What TO Do Instead)

### Refactored (Correct) Sprint Breakdown

```
Sprint 10: COMPLETE FLOW (button → backend → display)
  - Simple button in foreground
  - Backend API integration
  - Display result on screen
  - Result: USABLE! (40% value) ✅

Sprint 11: Add background operation (screen off)
  - Implement foreground service
  - Wake lock management
  - Keep product usable
  - Result: STILL USABLE (60% value) ✅

Sprint 12: Add headphone buttons (hands-free)
  - MediaSession API integration
  - Voice button support
  - Keep product usable
  - Result: STILL USABLE (80% value) ✅

Sprint 13: Add TTS feedback
  - Voice feedback for results
  - Audio output integration
  - Result: STILL USABLE (95% value) ✅

Sprint 14: Team/role selection + polish
  - Multiple team support
  - UI refinement
  - Production readiness
  - Result: PRODUCTION READY (100% value) ✅
```

### Key Decision Test

After **EVERY sprint**, ask:

> **"What can the user DO with this?"**

- If answer is **"nothing"** → Wrong breakdown ❌
- If answer is **"use a simpler version of the product"** → Correct breakdown ✅

---

## Universal Principle

### Wrong Approach (Infrastructure-First)
```
Build foundation → Build features → Integrate → Usable
```

### Right Approach (Product-Oriented)
```
Simplest usable → Add capability → Still usable → Add capability → Still usable
```

**The difference:** Every sprint ends with something the user can actually USE.

---

## Examples Where This Applies

### Web App Epic
```
❌ WRONG: Build auth system → API → UI → integrate
✅ RIGHT: Simple login flow → add features → add security
```

### Backend API Epic
```
❌ WRONG: Build database → models → routes → integrate
✅ RIGHT: One complete endpoint → add more endpoints → add features
```

### Mobile App Epic
```
❌ WRONG: Build service → UI → networking → integrate
✅ RIGHT: Simple button flow → add background → add hardware buttons
```

### Data Pipeline Epic
```
❌ WRONG: Build data schema → ETL → storage → reporting
✅ RIGHT: Simple CSV import → add processing → add storage → add reporting
```

---

## Evidence This Is A Real Problem

1. **Personal failure:** I made this mistake despite knowing the principle
2. **Had to be reminded:** Boss reminded me a 2nd time (also reminded in earlier session)
3. **Refactor was necessary:** Went from infrastructure-first to product-first plan
4. **Natural tendency:** Even experienced PMs gravitate toward infrastructure-first if not conscious

---

## How to Avoid This Pattern

### During Epic Breakdown

1. **Start with outcome** - "What's the minimum usable product?"
2. **Build simplest flow first** - One complete end-to-end path
3. **Check each sprint** - "Can user do something with this?"
4. **Add capabilities progressively** - Each sprint adds to usable product

### During Sprint Planning

1. **Ask SM/Team:** "Will this sprint end with something users can use?"
2. **If no:** Replan to include complete flow
3. **Keep infrastructure minimal:** Only what's needed for current sprint

### During Retrospectives

1. **Review delivery:** Did we ship value every sprint?
2. **Identify infrastructure bloat:** Did we build too much foundation?
3. **Adjust next sprint:** Shift toward complete flows

---

## Role-Specific Applications

### Product Owner
- Break epics into user-centric value increments
- Never plan 3 sprints of "infrastructure" without value delivery
- Define "definition of done" as "user can use this"

### Tech Lead / Scrum Master
- Challenge infrastructure-first planning: "What value does this sprint deliver?"
- Help team refactor technical dependencies into usable increments
- Coach team on progressive development

### Project Manager
- Validate sprint outcomes: "Can user do something with this?"
- Flag sprints with no user-facing value
- Adjust timelines and scope to maintain product orientation

### Developer
- During tasks: "Does this move toward user-usable feature?"
- Suggest refactoring epic to front-load usable product
- Raise hand if sprint backlog is all infrastructure

---

## Memory Storage Metadata

```json
{
  "memory_type": "semantic",
  "collection": "pm-patterns",
  "memory_level": "global",
  "doc_id": "pm-pattern-epic-planning-infrastructure-antipattern",
  "role": "pm",
  "title": "Epic Planning Anti-Pattern: Infrastructure-First Violates Product-Oriented Development",
  "description": "When breaking down large epics into sprints, developers naturally gravitate toward infrastructure-first planning (foundation → features → integration). This delays user value delivery and violates Product-Oriented + Progressive Development principles. Key lesson: Start with SIMPLEST COMPLETE FLOW, then progressively add capabilities.",
  "tags": [
    "#pm",
    "#product-oriented",
    "#epic-planning",
    "#progressive-development",
    "#anti-pattern",
    "#backlog",
    "#sprint-planning",
    "#value-delivery",
    "#failure-pattern",
    "#scrum",
    "#agile"
  ],
  "confidence": "high",
  "frequency": "high",
  "applicable_roles": [
    "Product Owner",
    "Scrum Master",
    "Tech Lead",
    "Project Manager",
    "Engineering Manager"
  ],
  "date_validated": "2026-01-03",
  "instances": 1,
  "similar_patterns": [
    "build-foundation-first-antipattern",
    "bottom-up-architecture-antipattern"
  ]
}
```

---

## Related Patterns

- **Similar:** Build Foundation First Anti-Pattern (applies to architecture design)
- **Opposite:** Simplest Viable Product Pattern (correct approach)
- **Related:** Progressive Development Framework
- **Related:** Product-Oriented Scrum

---

## References

- Boss's teaching: "Product-Oriented + Progressive Development" (taught in earlier sessions)
- Scrum Guide: Incremental value delivery
- Agile Manifesto: "Deliver working software frequently"
- Lean Startup: MVP (Minimum Viable Product) concept

---

## How to Use This Pattern

### When Planning Epics
Use this to challenge infrastructure-first proposals: "This plan has no user value until Sprint 12. Let's refactor to deliver value every sprint."

### During Sprint Planning
Ask: "Will users be able to DO something with the result of this sprint?" If no, replan.

### In Team Retrospectives
Review: "Did we maintain product orientation? Did every sprint deliver some user value?"

### For New PMs/Scrum Masters
Understand why "build it progressively, always shipped" beats "build foundation, then features."

---

## Status

- Documented: 2026-01-03
- Validated: Yes (personal experience + boss confirmation)
- Ready for team use: Yes
- Ready for memory system: Yes
