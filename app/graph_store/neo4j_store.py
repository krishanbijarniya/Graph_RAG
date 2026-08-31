from neo4j import GraphDatabase


class Neo4jStore:

    def __init__(
        self,
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password"
    ):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(username, password)
        )

    def verify_connection(self):

        with self.driver.session() as session:

            result = session.run(
                "RETURN 'Neo4j connected!' AS message"
            )

            return result.single()["message"]

    def close(self):
        self.driver.close()