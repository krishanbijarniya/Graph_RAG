from app.graph_store.neo4j_store import Neo4jStore


store = Neo4jStore()

message = store.verify_connection()

print(message)

store.close()