from app.retrieval.context_builder import ContextBuilder


def main():

    print("=" * 70)
    print("CONTEXT BUILDER TEST")
    print("=" * 70)

    query = (
        "How does SelfExtend improve "
        "long-context performance?"
    )

    reranked_results = [

        {
            "type": "graph",
            "score": 0.90,
            "data": {
                "entities": [
                    "SelfExtend",
                    "Long-Context Performance"
                ],
                "relationships": [
                    "IMPROVES"
                ]
            }
        },

        {
            "type": "vector",
            "score": 0.88,
            "data": {
                "document_id": "2401.01325v3",
                "page": 7,
                "chunk_id": "2401.01325v3_p7_c5",
                "text": (
                    "SelfExtend can maintain the "
                    "performance of short-context "
                    "tasks while enhancing performance "
                    "on long-context tasks."
                )
            }
        }
    ]

    builder = ContextBuilder()

    context = builder.build(
        query=query,
        reranked_results=reranked_results
    )

    print()
    print(context)

    print()
    print("=" * 70)
    print("CONTEXT BUILDER TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
