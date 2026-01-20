# Qdrant Scoring Research: Similarity vs Distance

**Date**: 2026-01-20
**Investigator**: DEV
**Boss Question**: Does Qdrant return SIMILARITY or DISTANCE scores?

---

## Part 1: Web Research Findings

### Official Qdrant Documentation

**Source**: [Qdrant Search Documentation](https://qdrant.tech/documentation/concepts/search/)

**Key Findings**:
- Qdrant returns **SIMILARITY scores** for COSINE distance metric
- Score range: -1.0 to 1.0
- 1.0 = perfect match (perfectly aligned vectors)
- 0.0 = no similarity
- -1.0 = diametrically opposed (completely dissimilar)
- **Higher scores = better matches**

**Source**: [Qdrant Distance Metrics Course](https://qdrant.tech/course/essentials/day-1/distance-metrics/)

**Implementation Details**:
- COSINE similarity is implemented as dot-product over normalized vectors
- Vectors are automatically normalized during upload
- After normalization, COSINE, Dot Product, and Euclidean give same ranking
- The `score` field in search results represents similarity value

**Important Distinction**:
- **COSINE metric**: Returns similarity (1.0 = best, higher is better)
- **EUCLIDEAN metric**: Returns distance (0.0 = best, lower is better)
- Metric behavior varies by distance type

### Research Sources:
1. [Qdrant Search Documentation](https://qdrant.tech/documentation/concepts/search/)
2. [Distance Metrics - Qdrant Course](https://qdrant.tech/course/essentials/day-1/distance-metrics/)
3. [What is Vector Similarity? - Qdrant Blog](https://qdrant.tech/blog/what-is-vector-similarity/)
4. [Qdrant Vectors Documentation](https://qdrant.tech/documentation/concepts/vectors/)

---

## Part 2: Practical Experiment Results

### Experiment Design

**Method**: Exact Content Match Test
1. Fetched actual document from Qdrant (backend collection)
2. Used document's exact content as search query
3. Measured score returned for perfect match
4. Determined scoring type based on result

### Experiment Data

**Document Tested**:
- ID: 1
- Title: "FastMCP: Minimal Python MCP Server"
- Content Length: 884 characters
- Collection: backend

**Search Query**: Exact same content (884 chars)

**Results**:

| Rank | Document ID | Title | Score |
|------|-------------|-------|-------|
| 1 | 1 (EXACT MATCH) | FastMCP: Minimal Python MCP Server | **0.9999999** |
| 2 | 1768842547541796 | Minimal | 0.50694346 |
| 3 | 1768844229709652 | Minimal | 0.50694346 |
| 4 | 1768844033674151 | Minimal | 0.50694346 |
| 5 | 1768842233637443 | Minimal | 0.50694346 |

### Analysis

**Exact Match Score**: 0.9999999 (essentially 1.0, accounting for floating point precision)

**Interpretation**:
- ✓ Score ≈ 1.0 indicates **SIMILARITY scoring**
- If it were distance scoring, exact match would score ≈ 0.0
- Higher score (0.9999999) for exact match confirms similarity
- Lower scores (0.506...) for non-matching documents

---

## Conclusion

**ANSWER**: Qdrant returns **SIMILARITY scores** for COSINE distance metric

### Summary:
- **1.0** = perfect match (highest similarity)
- **0.0** = no similarity (lowest)
- **-1.0** = completely dissimilar
- **Higher scores = better matches**

### Practical Implications:
- When interpreting search results, look for scores close to 1.0
- Results are already sorted by score (highest first)
- No need to invert scores or apply transformations
- Score of 0.9999999 for exact match confirms this is similarity

---

## Evidence Files

All evidence committed to repository:

1. **Experiment Script**: `experiments/qdrant_scoring_test/test_similarity_vs_distance.py`
2. **Experiment Log**: `experiments/qdrant_scoring_test/experiment_log.txt`
3. **Findings Report**: `experiments/qdrant_scoring_test/FINDINGS.md` (this file)

**Experiment Timestamp**: 2026-01-20T07:04:16

---

## Boss: Critical Takeaway

Qdrant with COSINE distance returns **SIMILARITY scores**, where:
- 1.0 = perfect match
- Higher = better
- Our search results are already correctly ordered (highest score first)
