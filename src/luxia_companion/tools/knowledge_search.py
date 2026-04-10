from crewai.tools import tool

from luxia_companion.knowledge import store


@tool("search_knowledge_base")
def search_knowledge_base(query: str) -> str:
    """Pesquisa a base de conhecimento sobre energia solar, cotas de usinas,
    contratos, regulamentação e informações do produto.
    Use esta ferramenta sempre que precisar consultar documentos de referência
    para responder perguntas dos parceiros comerciais."""

    results = store.search(query, n_results=5)

    if not results:
        return "Nenhum documento relevante encontrado na base de conhecimento."

    parts = []
    for doc in results:
        source = doc["metadata"].get("source", "desconhecido")
        parts.append(f"[Fonte: {source}]\n{doc['text']}")

    return "\n\n---\n\n".join(parts)
