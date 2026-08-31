from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)


class QdrantStore:

    def __init__(
        self,
        host="localhost",
        port=6333,
        collection_name="research_papers"
    ):
        self.client = QdrantClient(
            host=host,
            port=port
        )

        self.collection_name = collection_name

    def create_collection(self):

        collections = self.client.get_collections()

        existing = [
            collection.name
            for collection in collections.collections
        ]

        if self.collection_name not in existing:

            self.client.create_collection(
                collection_name=self.collection_name,

                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )

            print(
                f"Created collection: "
                f"{self.collection_name}"
            )

        else:

            print(
                f"Collection already exists: "
                f"{self.collection_name}"
            )

    def upsert_chunks(self, chunks, embeddings):

        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):

            point = PointStruct(
                id=index,
                vector=embedding.tolist(),
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "page": chunk["page"],
                    "chunk_number": chunk["chunk_number"],
                    "token_count": chunk["token_count"],
                    "text": chunk["text"]
                }
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        print(
            f"Inserted {len(points)} chunks into Qdrant"
        )

    def search(self, query_vector, top_k=5):

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            limit=top_k,
            with_payload=True
        )

        return results.points