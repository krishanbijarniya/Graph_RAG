from app.retrieval.vector_retriever import VectorRetriever


retriever = VectorRetriever()

query = "How does SelfExtend improve long-context performance?"

print("=" * 70)
print("VECTOR RETRIEVER TEST")
print("=" * 70)

print(f"\nQuery: {query}\n")

results = retriever.search(
    query=query,
    top_k=5
)

for i, result in enumerate(results, start=1):

    print(f"\n{i}. Score: {result['score']:.4f}")
    print(f"Chunk: {result['chunk_id']}")
    print(f"Document: {result['document_id']}")
    print(f"Page: {result['page']}")

    text = result["text"]

    print("Text:")
    print(text[:500])
    print("-" * 70)
