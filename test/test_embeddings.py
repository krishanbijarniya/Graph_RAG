from app.embeddings.embedder import Embedder
import numpy as np


embedder = Embedder()

texts = [
    "GraphRAG combines knowledge graphs with retrieval augmented generation.",
    "Knowledge graphs can improve retrieval for complex questions.",
    "I like eating pizza in Rome."
]

vectors = embedder.embed(texts)


for i in range(len(texts)):
    for j in range(i + 1, len(texts)):

        similarity = np.dot(
            vectors[i],
            vectors[j]
        )

        print(
            f"\nSimilarity between {i} and {j}: "
            f"{similarity:.4f}"
        )