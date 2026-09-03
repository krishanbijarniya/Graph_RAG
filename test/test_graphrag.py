from app.graphrag import GraphRAG


def main():

    print("=" * 70)
    print("GRAPH RAG END-TO-END TEST")
    print("=" * 70)

    query = (
        "How does SelfExtend improve "
        "long-context performance?"
    )

    print()
    print("USER QUESTION:")
    print(query)

    print()
    print("Running GraphRAG...")
    print()

    rag = GraphRAG()

    result = rag.ask(
        query=query,
        vector_top_k=5,
        graph_top_k=20,
        final_top_k=10
    )

    # --------------------------------
    # Query entities
    # --------------------------------

    print()
    print("QUERY ENTITIES:")
    print(
        result["query_entities"]
    )

    # --------------------------------
    # Final ranking
    # --------------------------------

    print()
    print("FINAL PROCESSED EVIDENCE:")
    print("-" * 70)

    for i, item in enumerate(
        result["processed_results"],
        start=1
    ):

        print(
            f"{i}. "
            f"{item['type'].upper()} "
            f"| Score: {item['score']:.4f}"
        )

        data = item["data"]

        if item["type"] == "vector":

            print(
                f"   Document: "
                f"{data['document_id']}"
            )

            print(
                f"   Page: {data['page']}"
            )

            print(
                f"   Chunk: {data['chunk_id']}"
            )

        else:

            entities = data["entities"]
            relationships = data["relationships"]

            path = []

            for j, entity in enumerate(
                entities
            ):

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

    # --------------------------------
    # Generated answer
    # --------------------------------

    print()
    print("=" * 70)
    print("GENERATED ANSWER")
    print("=" * 70)

    print()
    print(result["answer"])

    print()
    print("=" * 70)
    print("GRAPH RAG END-TO-END TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()