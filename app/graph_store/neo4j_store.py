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

    # =========================================================
    # CONNECTION
    # =========================================================

    def verify_connection(self):

        with self.driver.session() as session:

            result = session.run(
                "RETURN 'Neo4j connected!' AS message"
            )

            return result.single()["message"]

    # =========================================================
    # DOCUMENT
    # =========================================================

    def create_document(
        self,
        document_id
    ):

        query = """
        MERGE (d:Document {
            document_id: $document_id
        })
        """

        with self.driver.session() as session:

            session.run(
                query,
                document_id=document_id
            )

    # =========================================================
    # CHUNK
    # =========================================================

    def create_chunk(
        self,
        chunk
    ):

        query = """
        MERGE (d:Document {
            document_id: $document_id
        })

        MERGE (c:Chunk {
            chunk_id: $chunk_id
        })

        SET c.page = $page,
            c.chunk_number = $chunk_number,
            c.token_count = $token_count,
            c.text = $text

        MERGE (d)-[:CONTAINS]->(c)
        """

        with self.driver.session() as session:

            session.run(
                query,
                document_id=chunk["document_id"],
                chunk_id=chunk["chunk_id"],
                page=chunk["page"],
                chunk_number=chunk["chunk_number"],
                token_count=chunk["token_count"],
                text=chunk["text"]
            )

    # =========================================================
    # ENTITY
    # =========================================================

    def create_entity(
        self,
        name,
        entity_type="Entity"
    ):

        query = """
        MERGE (e:Entity {
            name: $name
        })

        SET e.type = $entity_type
        """

        with self.driver.session() as session:

            session.run(
                query,
                name=name,
                entity_type=entity_type
            )

    # =========================================================
    # CHUNK -> ENTITY
    # =========================================================

    def link_chunk_to_entity(
        self,
        chunk_id,
        entity_name
    ):

        query = """
        MATCH (c:Chunk {
            chunk_id: $chunk_id
        })

        MATCH (e:Entity {
            name: $entity_name
        })

        MERGE (c)-[:MENTIONS]->(e)
        """

        with self.driver.session() as session:

            session.run(
                query,
                chunk_id=chunk_id,
                entity_name=entity_name
            )

    # =========================================================
    # ENTITY -> ENTITY RELATIONSHIP
    # =========================================================

    def create_relationship(
        self,
        source,
        relationship,
        target,
        chunk_id=None,
        document_id=None,
        page=None
    ):

        query = """
        MERGE (s:Entity {
            name: $source
        })

        MERGE (t:Entity {
            name: $target
        })

        MERGE (s)-[r:RELATED_TO {
            type: $relationship
        }]->(t)

        SET r.chunk_id = $chunk_id,
            r.document_id = $document_id,
            r.page = $page
        """

        with self.driver.session() as session:

            session.run(
                query,
                source=source,
                target=target,
                relationship=relationship,
                chunk_id=chunk_id,
                document_id=document_id,
                page=page
            )

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):

        self.driver.close()