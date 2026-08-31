from app.embeddings.embedder import Embedder
from app.vector_store.qdrant_store import QdrantStore


query = "How do large language models improve their context window?"


print("Loading embedding model...")

embedder = Embedder()


print("Embedding query...")

query_vector = embedder.embed([query])[0]


print("Searching Qdrant...")

store = QdrantStore()

results = store.search(
    query_vector,
    top_k=5
)


print("\n" + "=" * 80)
print("QUERY")
print("=" * 80)
print(query)


for i, result in enumerate(results):

    print("\n" + "=" * 80)
    print(f"RESULT {i + 1}")
    print("=" * 80)

    print("Score:", result.score)
    print("Chunk ID:", result.payload["chunk_id"])
    print("Document:", result.payload["document_id"])
    print("Page:", result.payload["page"])

    print("\nText:")
    print(result.payload["text"][:1000])