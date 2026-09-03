from app.retrieval.graph_retriever import GraphRetriever


retriever = GraphRetriever()

print("=" * 70)
print("GRAPH RETRIEVER TEST")
print("=" * 70)


query = "How does SelfExtend improve long-context performance?"

entity_names = [
    "SelfExtend",
    "Long-Context Performance"
]


print("\nQuery:")
print(query)

print("\nQuery entities:")
print(entity_names)


results = retriever.search(
    entity_names=entity_names,
    query=query,
    max_hops=2,
    top_k=20
)


print(f"\nFound {len(results)} paths\n")


for index, result in enumerate(
    results,
    start=1
):

    entities = result["entities"]

    relationships = result["relationships"]

    score = result.get(
        "score",
        0
    )

    print(
        f"{index}. Score: {score}"
    )

    for i, entity in enumerate(
        entities
    ):

        print(
            entity,
            end=""
        )

        if i < len(relationships):

            print(
                f" -- {relationships[i]} --> ",
                end=""
            )

    print("\n")


retriever.close()


print("=" * 70)
print("GRAPH RETRIEVER TEST COMPLETE")
print("=" * 70)