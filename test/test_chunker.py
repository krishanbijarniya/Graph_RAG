from pathlib import Path

from app.ingestion.pdf_loader import extract_text
from app.ingestion.chunker import TextChunker


pdf_path = Path("data/papers/2307.06435v10.pdf")

document_id = pdf_path.stem

pages = extract_text(pdf_path)

chunker = TextChunker()

all_chunks = []

for page in pages:
    chunks = chunker.chunk_page(
        page_text=page["text"],
        page_number=page["page"],
        document_id=document_id
    )

    all_chunks.extend(chunks)


print(f"Total pages: {len(pages)}")
print(f"Total chunks: {len(all_chunks)}")


for chunk in all_chunks[:5]:

    print("\n" + "=" * 80)

    print(
        f"Chunk ID: {chunk['chunk_id']}"
    )

    print(
        f"Page: {chunk['page']}"
    )

    print(
        f"Tokens: {chunk['token_count']}"
    )

    print("=" * 80)

    print(chunk["text"][:1000])