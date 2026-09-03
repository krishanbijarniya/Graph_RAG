from app.retrieval.hybrid_reranker import HybridReranker


def main():

    print("=" * 70)
    print("HYBRID RERANKER TEST")
    print("=" * 70)

    query = "How does SelfExtend improve long-context performance?"

    query_entities = [
        "SelfExtend",
        "Long-Context Performance"
    ]

    vector_results = [
        {
            "score": 0.86,
            "chunk_id": "chunk_1",
            "document_id": "paper_1",
            "page": 10,
            "text": (
                "SelfExtend improves long-context performance "
                "without fine-tuning."
            )
        },
        {
            "score": 0.72,
            "chunk_id": "chunk_2",
            "document_id": "paper_1",
            "page": 11,
            "text": (
                "The method uses position interpolation "
                "for extending the context window."
            )
        }
    ]

    graph_results = [
        {
            "entities": [
                "SelfExtend",
                "Long-Context Performance"
            ],
            "relationships": [
                "IMPROVES"
            ]
        },
        {
            "entities": [
                "SelfExtend",
                "Context Window"
            ],
            "relationships": [
                "IMPROVES"
            ]
        },
        {
            "entities": [
                "SelfExtend",
                "Fine-tuning",
                "Zero-shot Performance"
            ],
            "relationships": [
                "AVOIDS",
                "IMPROVES"
            ]
        }
    ]

    reranker = HybridReranker()

    results = reranker.rerank(
        query=query,
        query_entities=query_entities,
        vector_results=vector_results,
        graph_results=graph_results,
        top_k=5
    )

    print()
    print("Query:")
    print(query)

    print()
    print("Final ranked results:")
    print()

    for i, result in enumerate(results, start=1):

        print(
            f"{i}. "
            f"Type: {result['type']} | "
            f"Score: {result['score']:.2f}"
        )

        if result["type"] == "vector":
            data = result["data"]

            print(
                f"   Document: {data['document_id']}"
            )

            print(
                f"   Page: {data['page']}"
            )

            print(
                f"   Text: {data['text']}"
            )

        else:
            data = result["data"]

            entities = data["entities"]
            relationships = data["relationships"]

            path = []

            for j, entity in enumerate(entities):

                path.append(entity)

                if j < len(relationships):
                    path.append(
                        f"-- {relationships[j]} -->"
                    )

            print(
                "   Graph: "
                + " ".join(path)
            )

        print()

    print("=" * 70)
    print("HYBRID RERANKER TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
