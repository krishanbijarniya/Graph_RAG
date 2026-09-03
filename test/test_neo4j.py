from app.graph_store.neo4j_store import Neo4jStore


store = Neo4jStore()

print("=" * 70)
print("NEO4J GRAPH TEST")
print("=" * 70)


# ---------------------------------------------------------
# TEST CONNECTION
# ---------------------------------------------------------

print("\nConnection:")

print(
    store.verify_connection()
)


# ---------------------------------------------------------
# COUNT ENTITIES
# ---------------------------------------------------------

with store.driver.session() as session:

    result = session.run(
        """
        MATCH (e:Entity)
        RETURN count(e) AS count
        """
    )

    count = result.single()["count"]


print("\nTotal entities:", count)


# ---------------------------------------------------------
# COUNT RELATIONSHIPS
# ---------------------------------------------------------

with store.driver.session() as session:

    result = session.run(
        """
        MATCH ()-[r]->()
        RETURN count(r) AS count
        """
    )

    count = result.single()["count"]


print("Total relationships:", count)


# ---------------------------------------------------------
# SHOW SAMPLE ENTITIES
# ---------------------------------------------------------

print("\nSample entities:")

with store.driver.session() as session:

    result = session.run(
        """
        MATCH (e:Entity)
        RETURN e.name AS name
        LIMIT 20
        """
    )

    for record in result:

        print(
            "-",
            record["name"]
        )


# ---------------------------------------------------------
# SHOW SAMPLE RELATIONSHIPS
# ---------------------------------------------------------

print("\nSample relationships:")

with store.driver.session() as session:

    result = session.run(
        """
        MATCH (s:Entity)-[r:RELATED_TO]->(t:Entity)

        RETURN
            s.name AS source,
            r.type AS relationship,
            t.name AS target

        LIMIT 20
        """
    )

    for record in result:

        print(
            f"{record['source']} "
            f"-- {record['relationship']} --> "
            f"{record['target']}"
        )


store.close()
