#!/usr/bin/env python3
"""
TDD tests for memory search engine module
Written BEFORE implementation (Sprint 3)
"""

import pytest
from unittest.mock import Mock
from src.memory.search_engine import search, fetch, batch_fetch


# ===== AC1: search() - Preview-Only Search =====

def test_search_returns_preview_objects_only():
    """AC1.1: Search returns list of preview objects (no content field)"""
    mock_qdrant = Mock()
    mock_point1 = Mock(id=1, score=0.95, payload={
        'title': 'Test Memory',
        'preview': 'This is a preview',
        'content': 'Full content should not be returned'
    })
    mock_qdrant.query_points.return_value = Mock(points=[mock_point1])

    mock_voyage = Mock()
    mock_voyage.embed.return_value = Mock(embeddings=[[0.1] * 1024])

    results = search("test query", "backend", limit=20,
                    qdrant_client=mock_qdrant, voyage_client=mock_voyage)

    assert len(results) == 1
    assert results[0]['id'] == 1
    assert results[0]['title'] == 'Test Memory'
    assert results[0]['preview'] == 'This is a preview'
    assert results[0]['score'] == 0.95
    assert 'content' not in results[0]


def test_search_results_sorted_by_similarity():
    """AC1.2: Results sorted by similarity score"""
    mock_qdrant = Mock()
    mock_point1 = Mock(id=1, score=0.75, payload={'title': 'Low', 'preview': 'Low score'})
    mock_point2 = Mock(id=2, score=0.95, payload={'title': 'High', 'preview': 'High score'})
    mock_point3 = Mock(id=3, score=0.85, payload={'title': 'Mid', 'preview': 'Mid score'})
    mock_qdrant.query_points.return_value = Mock(points=[mock_point1, mock_point2, mock_point3])

    mock_voyage = Mock()
    mock_voyage.embed.return_value = Mock(embeddings=[[0.1] * 1024])

    results = search("test", "backend", qdrant_client=mock_qdrant, voyage_client=mock_voyage)

    assert results[0]['score'] == 0.95
    assert results[1]['score'] == 0.85
    assert results[2]['score'] == 0.75


def test_search_respects_limit_parameter():
    """AC1.3: Respects limit parameter"""
    mock_qdrant = Mock()
    mock_qdrant.query_points.return_value = Mock(points=[])
    mock_voyage = Mock()
    mock_voyage.embed.return_value = Mock(embeddings=[[0.1] * 1024])

    search("test", "backend", limit=5, qdrant_client=mock_qdrant, voyage_client=mock_voyage)

    mock_qdrant.query_points.assert_called_once()
    call_kwargs = mock_qdrant.query_points.call_args[1]
    assert call_kwargs['limit'] == 5


def test_search_returns_empty_for_nonexistent_collection():
    """AC1.4: Returns empty list for non-existent collection"""
    mock_qdrant = Mock()
    mock_qdrant.query_points.side_effect = Exception("Collection not found")
    mock_voyage = Mock()
    mock_voyage.embed.return_value = Mock(embeddings=[[0.1] * 1024])

    results = search("test", "nonexistent", qdrant_client=mock_qdrant, voyage_client=mock_voyage)

    assert results == []


# ===== AC2: fetch() - Single Document Retrieval =====

def test_fetch_returns_full_document_with_content():
    """AC2.1: Fetch returns full document with content field"""
    mock_qdrant = Mock()
    mock_point = Mock(id=1, payload={
        'title': 'Test Memory',
        'preview': 'Preview text',
        'content': 'Full content with tags #tag1 #tag2'
    })
    mock_qdrant.retrieve.return_value = [mock_point]

    result = fetch(1, "backend", qdrant_client=mock_qdrant)

    assert result['id'] == 1
    assert result['title'] == 'Test Memory'
    assert result['preview'] == 'Preview text'
    assert result['content'] == 'Full content with tags #tag1 #tag2'


def test_fetch_raises_error_for_nonexistent_doc_id():
    """AC2.2: Raises ValueError for non-existent doc_id"""
    mock_qdrant = Mock()
    mock_qdrant.retrieve.return_value = []

    with pytest.raises(ValueError, match="Document.*not found"):
        fetch(999, "backend", qdrant_client=mock_qdrant)


def test_fetch_raises_error_for_nonexistent_collection():
    """AC2.3: Raises ValueError for non-existent collection"""
    mock_qdrant = Mock()
    mock_qdrant.retrieve.side_effect = Exception("Collection not found")

    with pytest.raises(ValueError, match="Collection.*not found"):
        fetch(1, "nonexistent", qdrant_client=mock_qdrant)


# ===== AC3: batch_fetch() - Multiple Document Retrieval Across Collections =====

def test_batch_fetch_returns_documents_from_multiple_collections():
    """AC3.1: Batch fetch returns documents from multiple collections"""
    mock_qdrant = Mock()

    mock_point_backend = Mock(id=1, payload={'title': 'Backend Doc', 'preview': 'P1', 'content': 'C1'})
    mock_point_qa = Mock(id=2, payload={'title': 'QA Doc', 'preview': 'P2', 'content': 'C2'})

    def retrieve_side_effect(collection_name, ids, **kwargs):
        if collection_name == "backend" and 1 in ids:
            return [mock_point_backend]
        elif collection_name == "qa" and 2 in ids:
            return [mock_point_qa]
        return []

    mock_qdrant.retrieve.side_effect = retrieve_side_effect

    results = batch_fetch([(1, "backend"), (2, "qa")], qdrant_client=mock_qdrant)

    assert len(results) == 2
    assert results[0]['id'] == 1
    assert results[0]['collection'] == 'backend'
    assert results[1]['id'] == 2
    assert results[1]['collection'] == 'qa'
    assert all('content' in doc for doc in results)


def test_batch_fetch_skips_nonexistent_refs_without_error():
    """AC3.2: Skips non-existent doc_refs without error"""
    mock_qdrant = Mock()
    mock_point1 = Mock(id=1, payload={'title': 'Doc1', 'preview': 'P1', 'content': 'C1'})

    def retrieve_side_effect(collection_name, ids, **kwargs):
        if collection_name == "backend" and 1 in ids:
            return [mock_point1]
        return []

    mock_qdrant.retrieve.side_effect = retrieve_side_effect

    results = batch_fetch([(1, "backend"), (999, "backend")], qdrant_client=mock_qdrant)

    assert len(results) == 1
    assert results[0]['id'] == 1


def test_batch_fetch_preserves_input_order():
    """AC3.3: Preserves input order"""
    mock_qdrant = Mock()
    mock_point1 = Mock(id=1, payload={'title': 'Doc1', 'preview': 'P1', 'content': 'C1'})
    mock_point2 = Mock(id=2, payload={'title': 'Doc2', 'preview': 'P2', 'content': 'C2'})
    mock_point3 = Mock(id=3, payload={'title': 'Doc3', 'preview': 'P3', 'content': 'C3'})

    def retrieve_side_effect(collection_name, ids, **kwargs):
        if collection_name == "backend":
            return [p for p in [mock_point2, mock_point1, mock_point3] if p.id in ids]
        return []

    mock_qdrant.retrieve.side_effect = retrieve_side_effect

    results = batch_fetch([(1, "backend"), (3, "backend"), (2, "backend")],
                         qdrant_client=mock_qdrant)

    assert results[0]['id'] == 1
    assert results[1]['id'] == 3
    assert results[2]['id'] == 2


def test_batch_fetch_groups_by_collection_for_efficiency():
    """AC3.4: Groups requests by collection (performance optimization)"""
    mock_qdrant = Mock()
    mock_point1 = Mock(id=1, payload={'title': 'Doc1', 'preview': 'P1', 'content': 'C1'})
    mock_point2 = Mock(id=3, payload={'title': 'Doc3', 'preview': 'P3', 'content': 'C3'})

    def retrieve_side_effect(collection_name, ids, **kwargs):
        if collection_name == "backend":
            return [p for p in [mock_point1, mock_point2] if p.id in ids]
        return []

    mock_qdrant.retrieve.side_effect = retrieve_side_effect

    batch_fetch([(1, "backend"), (3, "backend")], qdrant_client=mock_qdrant)

    assert mock_qdrant.retrieve.call_count == 1
    call_kwargs = mock_qdrant.retrieve.call_args[1]
    assert call_kwargs['collection_name'] == 'backend'
    assert set(call_kwargs['ids']) == {1, 3}


def test_batch_fetch_handles_empty_doc_refs_list():
    """AC3.5: Handles empty doc_refs list"""
    mock_qdrant = Mock()

    results = batch_fetch([], qdrant_client=mock_qdrant)

    assert results == []
    mock_qdrant.retrieve.assert_not_called()
