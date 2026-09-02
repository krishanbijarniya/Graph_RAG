from app.graph_store.neo4j_store import Neo4jStore


store = Neo4jStore()


relationships = [
    (
        "SelfExtend",
        "EXTENDS",
        "Context Window"
    ),
    (
        "SelfExtend",
        "USES",
        "Grouped Attention"
    ),
    (
        "SelfExtend",
        "USES",
        "Neighbor Attention"
    )
]


for source, relationship, target in relationships:

    store.create_relationship(
        source,
        relationship,
        target
    )


print("Graph relationships created.")

store.close()