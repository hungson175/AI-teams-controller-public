#!/usr/bin/env python3
"""
Qdrant Scoring Test: Similarity vs Distance

Boss Question: Does Qdrant return SIMILARITY or DISTANCE scores?

Test Method:
1. Fetch an actual document from Qdrant (backend collection)
2. Search using the EXACT same content as query
3. Check the score returned
4. If score ≈ 1.0 → similarity (1.0 = perfect match)
5. If score ≈ 0.0 → distance (0.0 = perfect match)

Expected: With COSINE distance, Qdrant should return similarity scores (1.0 = best)
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.memory.search_engine import _get_qdrant_client, _get_voyage_client, search


def main():
    """Run the experiment and log results."""

    log_file = "experiments/qdrant_scoring_test/experiment_log.txt"

    with open(log_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("Qdrant Scoring Experiment: Similarity vs Distance\n")
        f.write("="*80 + "\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

        # Step 1: Connect to Qdrant and fetch a document
        f.write("Step 1: Fetching a document from Qdrant (backend collection)\n")
        f.write("-" * 80 + "\n")

        qdrant = _get_qdrant_client()

        # Get a document from backend collection
        points = qdrant.scroll(
            collection_name="backend",
            limit=1,
            with_payload=True,
            with_vectors=False
        )

        if not points[0]:
            f.write("ERROR: No documents found in backend collection\n")
            print("ERROR: No documents found in backend collection")
            return

        doc = points[0][0]
        doc_id = doc.id
        doc_payload = doc.payload

        f.write(f"Document ID: {doc_id}\n")
        f.write(f"Document Title: {doc_payload.get('title', 'N/A')}\n")
        f.write(f"Document Preview: {doc_payload.get('preview', 'N/A')[:100]}...\n")

        # Get the full content
        content = doc_payload.get('content', '')

        f.write(f"\nDocument Content Length: {len(content)} characters\n")
        f.write(f"Document Content (first 200 chars):\n{content[:200]}\n\n")

        # Step 2: Search using EXACT same content as query
        f.write("Step 2: Searching with EXACT same content as query\n")
        f.write("-" * 80 + "\n")
        f.write("Query = Document Content (exact match)\n\n")

        # Use the search function which handles embedding generation
        results = search(
            query=content,  # Use EXACT document content as query
            collection="backend",
            limit=5
        )

        f.write(f"Search returned {len(results)} results\n\n")

        # Step 3: Analyze the scores
        f.write("Step 3: Analyzing Scores\n")
        f.write("-" * 80 + "\n")

        if not results:
            f.write("ERROR: No search results returned\n")
            print("ERROR: No search results returned")
            return

        # Find our document in results
        exact_match = None
        for i, result in enumerate(results):
            f.write(f"\nResult {i+1}:\n")
            f.write(f"  ID: {result['id']}\n")
            f.write(f"  Title: {result['title']}\n")
            f.write(f"  Score: {result['score']}\n")

            if result['id'] == doc_id:
                exact_match = result
                f.write(f"  *** THIS IS THE EXACT MATCH (same document) ***\n")

        if not exact_match:
            f.write("\nWARNING: Exact match document not found in top 5 results\n")
            f.write("Using highest scoring result instead\n")
            exact_match = results[0]

        # Step 4: Conclusion
        f.write("\n" + "="*80 + "\n")
        f.write("CONCLUSION\n")
        f.write("="*80 + "\n")

        exact_score = exact_match['score']

        f.write(f"\nExact Match Score: {exact_score}\n\n")

        if exact_score >= 0.99:  # Account for floating point precision
            f.write("✓ Score ≈ 1.0 → Qdrant returns SIMILARITY scores\n")
            f.write("  - 1.0 = perfect match (highest similarity)\n")
            f.write("  - 0.0 = no similarity (lowest)\n")
            f.write("  - Higher scores = better matches\n\n")
            f.write("ANSWER: Qdrant returns SIMILARITY scores for COSINE distance\n")
            conclusion = "SIMILARITY"
        elif exact_score <= 0.01:  # Account for floating point precision
            f.write("✓ Score ≈ 0.0 → Qdrant returns DISTANCE scores\n")
            f.write("  - 0.0 = perfect match (closest distance)\n")
            f.write("  - Higher values = worse matches\n")
            f.write("  - Lower scores = better matches\n\n")
            f.write("ANSWER: Qdrant returns DISTANCE scores for COSINE distance\n")
            conclusion = "DISTANCE"
        else:
            f.write(f"⚠ Unexpected score: {exact_score}\n")
            f.write("Expected either ≈1.0 (similarity) or ≈0.0 (distance)\n")
            conclusion = "UNCLEAR"

        f.write("\n" + "="*80 + "\n")
        f.write("Experiment Complete\n")
        f.write("="*80 + "\n")

        # Print to console
        print(f"\n{'='*80}")
        print("EXPERIMENT COMPLETE")
        print(f"{'='*80}")
        print(f"Exact Match Score: {exact_score}")
        print(f"Conclusion: Qdrant returns {conclusion} scores")
        print(f"\nLog file: {log_file}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
