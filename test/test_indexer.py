from app.vector_store.indexer import build_chunks


chunks = build_chunks()

print("\n" + "=" * 80)
print(f"TOTAL CHUNKS: {len(chunks)}")
print("=" * 80)

for chunk in chunks[:3]:

    print("\n")
    print("Chunk ID:", chunk["chunk_id"])
    print("Document:", chunk["document_id"])
    print("Page:", chunk["page"])
    print("Tokens:", chunk["token_count"])
    print("Text:", chunk["text"][:500])