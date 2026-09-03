from app.embeddings.embedder import Embedder
from app.vector_store.qdrant_store import QdrantStore


class VectorRetriever:

    def __init__(self):
        self.embedder = Embedder()
        self.store = QdrantStore()

    def search(self, query, top_k=5):

        query_embedding = self.embedder.embed([query])[0]

        results = self.store.search(
            query_vector=query_embedding,
            top_k=top_k
        )

        retrieved = []

        for result in results:

            payload = result.payload

            retrieved.append({
                "score": result.score,
                "chunk_id": payload["chunk_id"],
                "document_id": payload["document_id"],
                "page": payload["page"],
                "text": payload["text"]
            })

        return retrieved
