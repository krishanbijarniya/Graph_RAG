from app.vector_store.indexer import build_chunks
from app.embeddings.embedder import Embedder
from app.vector_store.qdrant_store import QdrantStore


print("Building chunks...")

chunks = build_chunks()

print(f"Total chunks: {len(chunks)}")


print("\nLoading embedding model...")

embedder = Embedder()


print("\nGenerating embeddings...")

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedder.embed(texts)

print(
    f"Embedding shape: {embeddings.shape}"
)


print("\nConnecting to Qdrant...")

store = QdrantStore()

store.create_collection()


print("\nUploading to Qdrant...")

store.upsert_chunks(
    chunks,
    embeddings
)