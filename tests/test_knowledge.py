import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_chroma(tmp_path):
    """Use a temporary directory for ChromaDB in tests."""
    chroma_dir = tmp_path / "chroma_test"
    chroma_dir.mkdir()

    from luxia_companion.config import settings

    orig_chroma = settings.chroma_persist_dir
    orig_kb = settings.knowledge_base_dir
    orig_api = settings.openai_api_key

    settings.chroma_persist_dir = str(chroma_dir)
    settings.knowledge_base_dir = str(tmp_path / "kb")
    settings.openai_api_key = "test-key"

    # Reset singletons
    import luxia_companion.knowledge.store as store_mod

    store_mod._client = None
    store_mod._collection = None

    yield tmp_path

    # Restore
    settings.chroma_persist_dir = orig_chroma
    settings.knowledge_base_dir = orig_kb
    settings.openai_api_key = orig_api
    store_mod._client = None
    store_mod._collection = None


def test_ingest_markdown(temp_chroma):
    """Test ingesting a markdown file and searching it."""
    kb_dir = temp_chroma / "kb"
    kb_dir.mkdir(exist_ok=True)

    # Create a test markdown document
    doc = kb_dir / "teste.md"
    doc.write_text(
        "# Energia Solar\n\n"
        "A compensação de energia funciona através do sistema de créditos da ANEEL. "
        "O consumidor que gera energia solar recebe créditos que são abatidos na "
        "conta de luz. Os créditos têm validade de 60 meses.\n\n"
        "## Cotas de Usinas\n\n"
        "As cotas de usinas solares permitem que consumidores participem de uma "
        "usina compartilhada sem precisar instalar painéis no próprio imóvel.",
        encoding="utf-8",
    )

    # Mock the OpenAI embedding to use a simple default
    with patch("luxia_companion.knowledge.store._get_embedding_fn") as mock_emb:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        mock_emb.return_value = DefaultEmbeddingFunction()

        from luxia_companion.knowledge.ingestion import ingest_all
        from luxia_companion.knowledge.store import count, search

        # Reset store singletons to pick up mock
        import luxia_companion.knowledge.store as store_mod

        store_mod._collection = None

        result = ingest_all(clear_existing=True)
        assert result["files"] == 1
        assert result["chunks"] >= 1
        assert count() >= 1

        results = search("compensação de energia créditos")
        assert len(results) > 0
        assert "compensação" in results[0]["text"].lower() or "créditos" in results[0]["text"].lower()
