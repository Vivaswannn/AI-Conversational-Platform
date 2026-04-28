import os
import pytest
from unittest.mock import patch, MagicMock

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars!!")


def test_rag_engine_can_be_instantiated():
    """RAGEngine class exists and can be referenced."""
    from app.ai.rag import RAGEngine
    assert RAGEngine is not None


@patch("app.ai.rag.chromadb.PersistentClient")
@patch("app.ai.rag.OpenAIEmbedding")
def test_query_returns_list_of_strings(mock_embed, mock_chroma):
    """query() returns a list of strings."""
    from app.ai.rag import RAGEngine

    engine = RAGEngine.__new__(RAGEngine)

    mock_node = MagicMock()
    mock_node.node.text = "chunk one"
    mock_node2 = MagicMock()
    mock_node2.node.text = "chunk two"

    mock_qe = MagicMock()
    mock_qe.query.return_value = MagicMock(source_nodes=[mock_node, mock_node2])
    engine._query_engine = mock_qe

    results = engine.query("help with anxiety")
    assert isinstance(results, list)
    assert all(isinstance(r, str) for r in results)
    assert results == ["chunk one", "chunk two"]


def test_query_returns_empty_list_on_exception():
    """query() returns empty list when query engine raises."""
    from app.ai.rag import RAGEngine

    engine = RAGEngine.__new__(RAGEngine)
    mock_qe = MagicMock()
    mock_qe.query.side_effect = Exception("Network error")
    engine._query_engine = mock_qe

    results = engine.query("any question")
    assert results == []
