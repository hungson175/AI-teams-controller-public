# Memory Test Samples

Extracted from existing MCP memory system on 2026-01-19 for Sprint 1 testing.

---

## Sample 1: Production-Context Learning

**ID:** 4c0afb29-2bb5-47c3-85bf-7149050e5298
**Role:** universal
**Type:** semantic
**Created:** 2025-11-30T16:52:15.190562

**Document:**
```
**Title:** Production-Context Learning Beats Generic Tutorials
**Description:** Learning new technologies by connecting concepts to actual production use cases accelerates understanding compared to abstract tutorials.

**Content:** Generic technology tutorials teach features in isolation without purpose or context, leading to shallow "cookbook" knowledge that doesn't transfer to real problems. Production-driven learning inverts this: start with WHY (what problem does this solve in MY codebase), then learn HOW (implement pattern to solve it). For Celery learning, starting with "PollManager polls OpenAI every 15s for 1 hour" gave concrete motivation - exercises weren't abstract task queues but direct preparation for understanding production code. Pattern: (1) identify production use case, (2) learn concepts through exercises matching that use case, (3) conclude by reading actual production implementation. The progression from "why we need this" → "how it works" → "how we actually use it" creates context that makes abstract concepts stick. This applies universally: learning React by building your actual dashboard beats TodoMVC tutorials, learning SQL by querying your actual database beats abstract schema examples.

**Tags:** #semantic #learning #production-driven #context #motivation #teaching #success
```

---

## Sample 2: Structured Technology Learning

**ID:** c67c4c25-a631-45c7-8004-4c3415c5bfbd
**Role:** universal
**Type:** procedural
**Created:** 2025-11-30T15:54:12.472420

**Document:**
```
# Technology Learning Framework

## Phase-Based Learning with Jupyter Notebooks

**Title:** Structured Technology Learning with Production Context
**Description:** Framework for learning new technologies by connecting concepts to actual production use cases through progressive phases.

**Content:** This pattern emerged from learning Celery by reverse-engineering a production PollManager system. The approach uses 4 progressive phases in Jupyter notebooks: (1) Core concepts with hands-on exercises, (2) Real-world patterns matching production code, (3) Configuration and monitoring for debugging, (4) Deep dive into actual production codebase. Each phase has markdown guide cells where learner fills in code, with reflection questions to solidify understanding. The key insight is starting with WHY (production use case) before HOW (basic tutorial), which provides motivation and context that makes abstract concepts concrete.

**Tags:** #procedural #learning #jupyter #production-driven #success
```

---

## Sample 3: Reverse-Engineering as Learning Phase

**ID:** 69ab7cf0-3e47-4ae2-8ad4-82b2acc2eb04
**Role:** universal
**Type:** procedural
**Created:** 2025-11-30T16:58:08.223122

**Document:**
```
**Title:** Reverse-Engineering as Final Learning Phase
**Description:** Conclude technology learning by reading production code that uses the patterns just learned.

**Content:** After learning basics (Phase 1-3), dedicate final phase to reading actual production code that implements those patterns. This validates understanding, reveals real-world complexities not in tutorials, and shows how pieces integrate. For Celery learning, this meant reading PollManager's tasks.py to see polling pattern in production, tracing task spawning through DeepResearcher, and understanding integration with Supabase. The progression from toy examples to production code creates "aha moments" where abstract concepts snap into focus with real purpose.

**Tags:** #procedural #learning #production-code #reverse-engineering #success
```

---

## Sample 4: Experiments-First Workflow

**ID:** f5abec64-cd50-4d5a-b9a0-d2e36f897a34
**Role:** universal
**Type:** procedural
**Created:** 2025-11-30T17:00:33.688586

**Document:**
```
**Title:** Experiments-First Development Workflow
**Description:** Write new code in experiments/ directory first, validate thoroughly, then migrate to src/ production codebase only after proven.

**Content:** Never write unproven code directly in src/ production directories. Create prototypes in experiments/ folder (e.g., experiments/strategies/optimizing_params/) where iteration is fast and breakage is acceptable. Test thoroughly with real data, validate correctness, benchmark performance. Only after everything works well, migrate validated code to src/ with proper structure, tests, and documentation. This keeps production codebase clean and prevents polluting it with half-working experimental code. Failed approach: writing experimental code directly in src/ leads to messy production directories, harder rollbacks, and confusion about what's proven vs experimental.

**Tags:** #procedural #development-workflow #experiments #code-organization #production-readiness #success
```

---

## Sample 5: Official Documentation as Foundation

**ID:** 8f02445d-99fa-4e2b-b45f-14b839944c5a
**Role:** universal
**Type:** procedural
**Created:** 2025-11-30T16:53:54.975743

**Document:**
```
**Title:** Official Documentation as Learning Foundation
**Description:** Use official docs with custom ToC as primary learning material rather than scattered tutorials.

**Content:** Instead of relying on random blog posts or videos, fetch official documentation (e.g., Celery first steps guide) and add a tree-like Table of Contents at the top for quick navigation. This provides authoritative, accurate information while improving discoverability. Supplement with a tailored learning plan that maps official doc sections to production use cases. The combination of "what exists" (official docs) and "why you need it" (production context) accelerates learning compared to following generic tutorials that may not match your actual needs.

**Tags:** #procedural #documentation #learning #success
```

---

## Sample 6: Time-Bounded Experiments

**ID:** cefa345b-2977-4e38-ba76-dfcf97b0adda
**Role:** universal
**Type:** semantic
**Created:** 2025-11-30T17:01:22.941932

**Document:**
```
**Title:** Time-Bounded Experiments with Forcing Functions Prevent Drift
**Description:** Engineers get trapped in experiment code because immediate results are addictive, while production code rots - forcing functions with time-boxing and graduation rituals prevent this anti-pattern.

**Content:** Experiment drift occurs when engineers iterate endlessly in experiments/ because fast feedback is addictive, losing sight of system-building goals. Pattern: set countdown timer (2-4 hours MAX), write success checklist (3-5 items), define exit conditions, plan graduation target (which production file to update). After timer expires: graduate learnings to production immediately (success/partial/failure), document pattern, DELETE experiment code. Red flags: >4 hours in experiments without updating production, adding features instead of validating hypothesis, refactoring experiment code. Key insight: "Productivity ≠ Progress" - you can write tons of experiment code (productive) without making ANY system progress. Failed approach: letting experiments accumulate leads to working throwaway code but broken production code.

**Tags:** #semantic #engineering-process #experiment-management #anti-pattern #time-management #productivity #technical-debt #system-design #forcing-function
```

---

## Sample 7: Establish Baseline Before Refactoring

**ID:** 2dc55f99-0d96-44e3-970e-3ccf1423d9e3
**Role:** universal
**Type:** procedural
**Created:** 2025-11-08T14:00:37.246784Z

**Document:**
```
**Title:** Establish Baseline Before Refactoring
**Description:** Before refactoring code, capture or find existing outputs to verify behavior preservation through regression testing.

**Content:** Refactoring introduces bugs easily despite being "safe" code reorganization. Before extracting functions, renaming, or restructuring, either find existing output files from prior runs OR execute code once to capture baseline results (save as regression_data/ or baseline_results/ with timestamps). After refactoring, run identical inputs and compare outputs byte-for-byte to detect regressions. For non-deterministic systems (optimizers, ML), fix random seeds for exact reproduction. Failed approach: refactoring without baseline data makes regression detection impossible - discovered this when user asked "do we have base-truth to test BEFORE refactoring?" after 3 commits, fortunately found old output files to create regression test.

**Tags:** #procedural #refactoring #testing #regression #baseline #failure #success
```

---

## Summary

- **Total Samples:** 7
- **Roles:** All universal
- **Types:** 4 procedural, 3 semantic
- **Themes:** Learning, development workflows, testing, experimentation
- **Source:** Existing MCP memory system via mcp__memory__search_memory and mcp__memory__batch_get_memories
