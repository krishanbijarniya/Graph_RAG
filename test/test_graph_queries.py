from app.graph_store.neo4j_store import Neo4jStore


store = Neo4jStore()

print("=" * 70)
print("GRAPH QUERY TEST")
print("=" * 70)


# --------------------------------------------------
# 1. Find SelfExtend
# --------------------------------------------------

print("\n1. SelfExtend connections")
print("-" * 70)

with store.driver.session() as session:

    result = session.run(
        """
        MATCH (e:Entity {name: "SelfExtend"})
        OPTIONAL MATCH (e)-[r:RELATED_TO]->(target:Entity)

        RETURN
            e.name AS source,
            r.type AS relationship,
            target.name AS target

        LIMIT 20
        """
    )

    found = False

    for record in result:
        found = True

        print(
            f"{record['source']} "
            f"-- {record['relationship']} --> "
            f"{record['target']}"
        )

    if not found:
        print("SelfExtend not found.")


# --------------------------------------------------
# 2. Two-hop traversal
# --------------------------------------------------

print("\n2. Two-hop traversal from SelfExtend")
print("-" * 70)

with store.driver.session() as session:

    result = session.run(
        """
        MATCH path =
            (start:Entity {name: "SelfExtend"})
            -[:RELATED_TO*1..2]->
            (target:Entity)

        RETURN
            [node IN nodes(path) | node.name] AS nodes,
            [rel IN relationships(path) | rel.type] AS relationships

        LIMIT 30
        """
    )

    for record in result:

        print(
            " -> ".join(record["nodes"])
        )

        print(
            "Relationships:",
            " -> ".join(record["relationships"])
        )

        print()


# --------------------------------------------------
# 3. Most connected entities
# --------------------------------------------------

print("\n3. Most connected entities")
print("-" * 70)

with store.driver.session() as session:

    result = session.run(
        """
        MATCH (e:Entity)
        OPTIONAL MATCH (e)-[r]-()

        RETURN
            e.name AS entity,
            count(r) AS connections

        ORDER BY connections DESC

        LIMIT 20
        """
    )

    for record in result:

        print(
            f"{record['entity']:<45} "
            f"{record['connections']}"
        )


# --------------------------------------------------
# 4. Relationship distribution
# --------------------------------------------------

print("\n4. Relationship distribution")
print("-" * 70)

with store.driver.session() as session:

    result = session.run(
        """
        MATCH ()-[r:RELATED_TO]->()

        RETURN
            r.type AS relationship,
            count(*) AS count

        ORDER BY count DESC
        """
    )

    for record in result:

        print(
            f"{record['relationship']:<20} "
            f"{record['count']}"
        )


store.close()

print("\n" + "=" * 70)
print("GRAPH QUERY TEST COMPLETE")
print("=" * 70)