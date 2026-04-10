"""Ingestão de documentos na base de conhecimento.

Uso:
    python scripts/ingest.py [--clear]
"""

import argparse
import logging
import sys
from pathlib import Path

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from luxia_companion.knowledge.ingestion import ingest_all  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="Ingestão de documentos na base de conhecimento")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Limpa a base existente antes de re-ingerir",
    )
    args = parser.parse_args()

    result = ingest_all(clear_existing=args.clear)
    print(f"\nIngestão concluída: {result['files']} arquivos, {result['chunks']} chunks indexados.")


if __name__ == "__main__":
    main()
