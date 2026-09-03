from app.graph_store.neo4j_store import Neo4jStore


class GraphRetriever:

    def __init__(self):
        self.graph = Neo4jStore()

    def search(
        self,
        entity_names,
        query=None,
        max_hops=2,
        top_k=10
    ):
        """
        Retrieve and rank graph paths for a query.

        Ranking strategy:

        1. Direct connection to query entity
        2. Query entity overlap
        3. Query-term overlap
        4. Relationship importance
        5. Path length penalty
        6. Generic hub penalty
        """

        if not entity_names:
            return []

        # ==================================================
        # 1. GRAPH QUERY
        # ==================================================

        query_cypher = """
        MATCH path =
            (start:Entity)-[:RELATED_TO*1..2]->(target:Entity)

        WHERE start.name IN $entity_names
        AND ALL(
            node IN nodes(path)[1..]
            WHERE node <> start
        )

        WITH
            path,
            nodes(path) AS path_nodes,
            relationships(path) AS path_relationships

        RETURN
            [node IN path_nodes | node.name] AS entities,
            [rel IN path_relationships | rel.type] AS relationships
        """

        with self.graph.driver.session() as session:

            result = session.run(
                query_cypher,
                entity_names=entity_names
            )

            candidates = []

            for record in result:

                candidates.append({
                    "entities": record["entities"],
                    "relationships": record["relationships"]
                })

        # ==================================================
        # 2. QUERY TERMS
        # ==================================================

        query_terms = set()

        if query:

            stop_words = {
                "how",
                "does",
                "do",
                "did",
                "what",
                "why",
                "when",
                "where",
                "which",
                "is",
                "are",
                "the",
                "a",
                "an",
                "of",
                "to",
                "in",
                "on",
                "for",
                "and",
                "or",
                "with",
                "from",
                "by",
                "can",
                "could",
                "would",
                "should",
                "improve",
                "improves",
                "use",
                "uses"
            }

            words = (
                query
                .lower()
                .replace("?", "")
                .replace(",", "")
                .split()
            )

            query_terms = {
                word
                for word in words
                if word not in stop_words
            }

        # ==================================================
        # 3. GENERIC ENTITIES
        # ==================================================

        generic_entities = {
            "llm",
            "llms",
            "large language model",
            "large language models",
            "model",
            "models",
            "performance",
            "task",
            "tasks",
            "method",
            "methods",
            "approach",
            "approaches",
            "technique",
            "techniques"
        }

        # ==================================================
        # 4. RELATIONSHIP WEIGHTS
        # ==================================================

        relationship_weights = {

            "IMPROVES": 6,

            "EXTENDS": 6,

            "CAPTURES": 6,

            "USES": 5,

            "AVOIDS": 5,

            "PROPOSES": 5,

            "CONTAINS": 4,

            "BASED_ON": 4,

            "EVALUATES": 3,

            "COMPARES_WITH": 3,

            "TRAINS": 3,

            "RELATED_TO": 1
        }

        # ==================================================
        # 5. SCORE EACH PATH
        # ==================================================

        scored_paths = []

        query_entities_lower = {
            entity.lower()
            for entity in entity_names
        }

        for path in candidates:

            path_entities = path["entities"]

            path_relationships = path["relationships"]

            path_entities_lower = [
                entity.lower()
                for entity in path_entities
            ]

            # ----------------------------------------------
            # Entity overlap
            # ----------------------------------------------

            entity_overlap = len(
                query_entities_lower
                &
                set(path_entities_lower)
            )

            entity_score = entity_overlap * 8

            # ----------------------------------------------
            # Direct target match
            # ----------------------------------------------

            direct_target_score = 0

            if len(path_entities) >= 2:

                target = (
                    path_entities[-1]
                    .lower()
                )

                if target in query_entities_lower:

                    direct_target_score = 20

            # ----------------------------------------------
            # Query word overlap
            # ----------------------------------------------

            word_score = 0

            for entity in path_entities:

                entity_words = {
                    word.strip(".,!?;:").lower()
                    for word in entity.split()
                }

                overlap = (
                    entity_words
                    &
                    query_terms
                )

                word_score += (
                    len(overlap) * 4
                )

            # ----------------------------------------------
            # Relationship score
            # ----------------------------------------------

            relationship_score = 0

            for relationship in path_relationships:

                relationship_score += (
                    relationship_weights.get(
                        relationship,
                        1
                    )
                )

            # ----------------------------------------------
            # Path length
            # ----------------------------------------------

            hop_count = len(
                path_relationships
            )

            path_penalty = (
                (hop_count - 1) * 4
            )

            # ----------------------------------------------
            # Generic hub penalty
            # ----------------------------------------------

            generic_penalty = 0

            for entity in path_entities[1:]:

                if (
                    entity.lower()
                    in generic_entities
                ):

                    generic_penalty += 8

            # ----------------------------------------------
            # Final score
            # ----------------------------------------------

            score = (
                entity_score
                + direct_target_score
                + word_score
                + relationship_score
                - path_penalty
                - generic_penalty
            )

            path["score"] = score

            scored_paths.append(path)

        # ==================================================
        # 6. SORT
        # ==================================================

        scored_paths.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # ==================================================
        # 7. REMOVE DUPLICATES
        # ==================================================

        unique_paths = []

        seen = set()

        for path in scored_paths:

            path_key = (
                tuple(path["entities"]),
                tuple(path["relationships"])
            )

            if path_key in seen:
                continue

            seen.add(path_key)

            unique_paths.append(path)

            if len(unique_paths) >= top_k:
                break

        return unique_paths

    def close(self):
        self.graph.close()