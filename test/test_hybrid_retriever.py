from app.retrieval.hybrid_retriever import HybridRetriever


def main():

    print("=" * 70)
    print("HYBRID RETRIEVER TEST")
    print("=" * 70)

    query = "How does SelfExtend improve long-context performance?"

    print()
    print("Query:")
    print(query)

    retriever = HybridRetriever()

    results = retriever.search(
        query=query,
        vector_top_k=5,
        graph_top_k=20,
        final_top_k=10
    )

    print()
    print("Query entities:")
    print(results["query_entities"])

    print()
    print(
        f"Vector candidates: "
        f"{len(results['vector_results'])}"
    )

    print(
        f"Graph candidates: "
        f"{len(results['graph_results'])}"
    )

    print()
    print("FINAL HYBRID RANKING")
    print("-" * 70)

    for i, result in enumerate(
        results["reranked_results"],
        start=1
    ):

        print(
            f"\n{i}. "
            f"Type: {result['type'].upper()} "
            f"| Score: {result['score']:.4f}"
        )

        data = result["data"]

        if result["type"] == "vector":

            print(
                f"Document: {data['document_id']}"
            )

            print(
                f"Page: {data['page']}"
            )

            print(
                f"Chunk: {data['chunk_id']}"
            )

            print(
                f"Text: {data['text'][:300]}..."
            )

        else:

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
                "Graph: "
                + " ".join(path)
            )

    print()
    print("=" * 70)
    print("HYBRID RETRIEVER TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
