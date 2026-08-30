from pathlib import Path

from app.ingestion.pdf_loader import extract_text
from app.ingestion.chunker import TextChunker
from app.embeddings.embedder import Embedder
from app.vector_store.qdrant_store import QdrantStore


PDF_DIR = Path("data/papers")


def build_chunks():
    chunker = TextChunker()

    all_chunks = []

    for pdf_path in PDF_DIR.glob("*.pdf"):

        print(f"Processing: {pdf_path.name}")

        pages = extract_text(pdf_path)

        document_id = pdf_path.stem

        for page in pages:

            chunks = chunker.chunk_page(
                page_text=page["text"],
                page_number=page["page"],
                document_id=document_id
            )

            all_chunks.extend(chunks)

    return all_chunks