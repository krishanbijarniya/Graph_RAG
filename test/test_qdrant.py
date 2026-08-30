from app.vector_store.qdrant_store import QdrantStore


store = QdrantStore()

store.create_collection()