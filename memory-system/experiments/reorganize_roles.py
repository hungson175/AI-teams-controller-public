#!/usr/bin/env python3
"""Reorganize memories into proper role collections"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
import voyageai
import os

load_dotenv()

qdrant = QdrantClient(url='http://localhost:16333')
voyage = voyageai.Client(api_key=os.getenv('VOYAGE_API_KEY'))

# Delete universal collection
qdrant.delete_collection('universal')
print('✓ Deleted universal collection')

# Create proper role collections (Scrum Team roles)
collections_to_create = ['other-role', 'tech-leader', 'scrum-master', 'qa']
for coll in collections_to_create:
    qdrant.create_collection(
        collection_name=coll,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )
    print(f'✓ Created collection: {coll}')

# Memories with correct role assignments
memories = [
    {
        'collection': 'other-role',
        'id': 1,
        'title': 'Production-Context Learning Beats Generic Tutorials',
        'preview': 'Learning new technologies by connecting concepts to actual production use cases accelerates understanding compared to abstract tutorials.',
        'content': '''**Title:** Production-Context Learning Beats Generic Tutorials
**Preview:** Learning new technologies by connecting concepts to actual production use cases accelerates understanding compared to abstract tutorials.

**Content:** Generic technology tutorials teach features in isolation without purpose or context, leading to shallow "cookbook" knowledge that doesn't transfer to real problems. Production-driven learning inverts this: start with WHY (what problem does this solve in MY codebase), then learn HOW (implement pattern to solve it). For Celery learning, starting with "PollManager polls OpenAI every 15s for 1 hour" gave concrete motivation - exercises weren't abstract task queues but direct preparation for understanding production code. Pattern: (1) identify production use case, (2) learn concepts through exercises matching that use case, (3) conclude by reading actual production implementation. The progression from "why we need this" → "how it works" → "how we actually use it" creates context that makes abstract concepts stick. This applies universally: learning React by building your actual dashboard beats TodoMVC tutorials, learning SQL by querying your actual database beats abstract schema examples.

**Tags:** #learning #production-driven #context #motivation #teaching'''
    },
    {
        'collection': 'tech-leader',
        'id': 1,
        'title': 'Experiments-First Development Workflow',
        'preview': 'Write new code in experiments/ directory first, validate thoroughly, then migrate to src/ production codebase only after proven.',
        'content': '''**Title:** Experiments-First Development Workflow
**Preview:** Write new code in experiments/ directory first, validate thoroughly, then migrate to src/ production codebase only after proven.

**Content:** Never write unproven code directly in src/ production directories. Create prototypes in experiments/ folder (e.g., experiments/strategies/optimizing_params/) where iteration is fast and breakage is acceptable. Test thoroughly with real data, validate correctness, benchmark performance. Only after everything works well, migrate validated code to src/ with proper structure, tests, and documentation. This keeps production codebase clean and prevents polluting it with half-working experimental code. Failed approach: writing experimental code directly in src/ leads to messy production directories, harder rollbacks, and confusion about what's proven vs experimental.

**Tags:** #development-workflow #experiments #code-organization #production-readiness #process'''
    },
    {
        'collection': 'other-role',
        'id': 2,
        'title': 'Official Documentation as Learning Foundation',
        'preview': 'Use official docs with custom ToC as primary learning material rather than scattered tutorials.',
        'content': '''**Title:** Official Documentation as Learning Foundation
**Preview:** Use official docs with custom ToC as primary learning material rather than scattered tutorials.

**Content:** Instead of relying on random blog posts or videos, fetch official documentation (e.g., Celery first steps guide) and add a tree-like Table of Contents at the top for quick navigation. This provides authoritative, accurate information while improving discoverability. Supplement with a tailored learning plan that maps official doc sections to production use cases. The combination of "what exists" (official docs) and "why you need it" (production context) accelerates learning compared to following generic tutorials that may not match your actual needs.

**Tags:** #documentation #learning #official-docs'''
    },
    {
        'collection': 'scrum-master',
        'id': 1,
        'title': 'Time-Bounded Experiments with Forcing Functions Prevent Drift',
        'preview': 'Engineers get trapped in experiment code because immediate results are addictive, while production code rots - forcing functions with time-boxing and graduation rituals prevent this anti-pattern.',
        'content': '''**Title:** Time-Bounded Experiments with Forcing Functions Prevent Drift
**Preview:** Engineers get trapped in experiment code because immediate results are addictive, while production code rots - forcing functions with time-boxing and graduation rituals prevent this anti-pattern.

**Content:** Experiment drift occurs when engineers iterate endlessly in experiments/ because fast feedback is addictive, losing sight of system-building goals. Pattern: set countdown timer (2-4 hours MAX), write success checklist (3-5 items), define exit conditions, plan graduation target (which production file to update). After timer expires: graduate learnings to production immediately (success/partial/failure), document pattern, DELETE experiment code. Red flags: >4 hours in experiments without updating production, adding features instead of validating hypothesis, refactoring experiment code. Key insight: "Productivity ≠ Progress" - you can write tons of experiment code (productive) without making ANY system progress. Failed approach: letting experiments accumulate leads to working throwaway code but broken production code.

**Tags:** #engineering-process #experiment-management #anti-pattern #time-management #team-management #forcing-function'''
    },
    {
        'collection': 'qa',
        'id': 1,
        'title': 'Establish Baseline Before Refactoring',
        'preview': 'Before refactoring code, capture or find existing outputs to verify behavior preservation through regression testing.',
        'content': '''**Title:** Establish Baseline Before Refactoring
**Preview:** Before refactoring code, capture or find existing outputs to verify behavior preservation through regression testing.

**Content:** Refactoring introduces bugs easily despite being "safe" code reorganization. Before extracting functions, renaming, or restructuring, either find existing output files from prior runs OR execute code once to capture baseline results (save as regression_data/ or baseline_results/ with timestamps). After refactoring, run identical inputs and compare outputs byte-for-byte to detect regressions. For non-deterministic systems (optimizers, ML), fix random seeds for exact reproduction. Failed approach: refactoring without baseline data makes regression detection impossible - discovered this when user asked "do we have base-truth to test BEFORE refactoring?" after 3 commits, fortunately found old output files to create regression test.

**Tags:** #refactoring #testing #regression #baseline #qa'''
    }
]

print('\nInserting memories into proper role collections...')

for mem in memories:
    # Generate embedding
    result = voyage.embed(texts=[mem['content']], model='voyage-4-lite')
    embedding = result.embeddings[0]

    # Store in correct collection
    qdrant.upsert(
        collection_name=mem['collection'],
        points=[PointStruct(
            id=mem['id'],
            vector=embedding,
            payload={
                'title': mem['title'],
                'preview': mem['preview'],
                'content': mem['content']
            }
        )]
    )
    print(f"  ✓ {mem['collection']}/{mem['id']}: {mem['title'][:45]}...")

print('\n=== Final Collections ===')
collections = qdrant.get_collections()
for c in collections.collections:
    info = qdrant.get_collection(c.name)
    print(f'{c.name}: {info.points_count} memories')
