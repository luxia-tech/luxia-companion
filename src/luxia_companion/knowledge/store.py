import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from luxia_companion.config import settings

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client


def _get_embedding_fn() -> OpenAIEmbeddingFunction:
    return OpenAIEmbeddingFunction(
        api_key=settings.openai_api_key,
        model_name="text-embedding-3-small",
    )


def get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=_get_embedding_fn(),
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_documents(
    ids: list[str],
    documents: list[str],
    metadatas: list[dict] | None = None,
) -> None:
    collection = get_collection()
    collection.add(ids=ids, documents=documents, metadatas=metadatas)


def search(query: str, n_results: int = 5) -> list[dict]:
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=n_results)

    docs = []
    for i in range(len(results["ids"][0])):
        docs.append(
            {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
            }
        )
    return docs


def clear() -> None:
    client = _get_client()
    try:
        client.delete_collection("knowledge_base")
    except Exception:
        pass
    global _collection
    _collection = None


def count() -> int:
    return get_collection().count()
