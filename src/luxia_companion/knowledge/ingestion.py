import hashlib
import logging
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from luxia_companion.config import settings
from luxia_companion.knowledge import store

logger = logging.getLogger(__name__)

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300,
    separators=[
        "\n\n## ",
        "\n\n### ",
        "\n\nArtigo ",
        "\n\nCláusula ",
        "\n\nSeção ",
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ],
)


def _parse_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _parse_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _parse_pdf(path)
    if suffix in (".md", ".txt"):
        return _parse_markdown(path)
    raise ValueError(f"Formato não suportado: {suffix}")


def _chunk_id(source: str, index: int) -> str:
    raw = f"{source}::{index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def ingest_file(path: Path) -> int:
    logger.info(f"Processando: {path.name}")
    text = _parse_file(path)
    if not text.strip():
        logger.warning(f"Arquivo vazio: {path.name}")
        return 0

    chunks = _splitter.split_text(text)
    source = path.name

    ids = [_chunk_id(source, i) for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]

    store.add_documents(ids=ids, documents=chunks, metadatas=metadatas)
    logger.info(f"  → {len(chunks)} chunks indexados de {source}")
    return len(chunks)


def ingest_all(clear_existing: bool = False) -> dict:
    kb_dir = Path(settings.knowledge_base_dir)
    if not kb_dir.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {kb_dir}")

    if clear_existing:
        store.clear()
        logger.info("Base de conhecimento limpa.")

    files = sorted(
        p for p in kb_dir.iterdir()
        if p.is_file() and p.suffix.lower() in (".pdf", ".md", ".txt")
    )

    if not files:
        logger.warning(f"Nenhum documento encontrado em {kb_dir}")
        return {"files": 0, "chunks": 0}

    total_chunks = 0
    for f in files:
        total_chunks += ingest_file(f)

    logger.info(f"Total: {len(files)} arquivos, {total_chunks} chunks")
    return {"files": len(files), "chunks": total_chunks}
