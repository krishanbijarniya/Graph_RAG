from app.graph_builder.extractor import EntityRelationshipExtractor
from app.graph_store.neo4j_store import Neo4jStore


class GraphBuilder:

    def __init__(self, model="qwen2.5:7b"):

        self.extractor = EntityRelationshipExtractor(
            model=model
        )

        self.graph = Neo4jStore()

    # =========================================================
    # ENTITY NORMALIZATION
    # =========================================================

    def normalize_entity(self, entity):

        entity = entity.strip()

        canonical = {
            "selfextend": "SelfExtend",

            "context window": "Context Window",

            "pretrained large language models":
                "Pretrained Language Models",

            "pre-trained large language models":
                "Pretrained Language Models",

            "fine-tuning": "Fine-tuning",

            "fine tuning": "Fine-tuning",

            "grouped attention": "Grouped Attention",

            "neighbor attention": "Neighbor Attention",

            "bi-level attention":
                "Bi-Level Attention",

            "bi-level attention information":
                "Bi-Level Attention",

            "long-range dependencies":
                "Long-Range Dependencies",
        }

        key = entity.lower()

        return canonical.get(
            key,
            entity
        )

    # =========================================================
    # RELATIONSHIP VALIDATION
    # =========================================================

    def validate_relationship(
        self,
        source,
        relationship,
        target,
        text
    ):
        """
        Validate an LLM-generated relationship
        against the original chunk text.
        """

        text_lower = text.lower()

        source_lower = source.lower()
        target_lower = target.lower()

        relationship = relationship.upper()

        # -----------------------------------------------------
        # Handle explicit negation
        # -----------------------------------------------------

        if target_lower == "fine-tuning":

            negative_patterns = [
                "without fine-tuning",
                "without fine tuning",
                "does not require fine-tuning",
                "doesn't require fine-tuning",
                "do not require fine-tuning",
                "does not use fine-tuning",
                "doesn't use fine-tuning",
                "without requiring fine-tuning",
            ]

            for pattern in negative_patterns:

                if pattern in text_lower:

                    if relationship in {
                        "USES",
                        "BASED_ON",
                        "REQUIRES",
                        "DEPENDS_ON",
                        "TRAINS",
                    }:

                        return False

        return True

    # =========================================================
    # PROCESS ONE CHUNK
    # =========================================================

    def process_chunk(self, chunk):

        print(
            f"Processing {chunk['chunk_id']}"
        )

        # -----------------------------------------------------
        # Extract graph information using Ollama
        # -----------------------------------------------------

        result = self.extractor.extract(
            chunk["text"]
        )

        # -----------------------------------------------------
        # Entities that should not become graph nodes
        # -----------------------------------------------------

        ignored_entities = {
            "adjacent tokens",
            "dependencies among tokens",
            "dependencies among tokens that are far apart",
            "dependencies among adjacent tokens",
        }

        # -----------------------------------------------------
        # Normalize entities
        # -----------------------------------------------------

        normalized_entities = []

        for entity in result["entities"]:

            normalized = self.normalize_entity(
                entity
            )

            # Remove noisy entities
            if normalized.lower() in ignored_entities:
                continue

            # Avoid duplicates
            if normalized not in normalized_entities:

                normalized_entities.append(
                    normalized
                )

        # -----------------------------------------------------
        # Create document
        # -----------------------------------------------------

        self.graph.create_document(
            chunk["document_id"]
        )


        # -----------------------------------------------------
        # Create chunk
        # -----------------------------------------------------

        self.graph.create_chunk(
            chunk
        )


        # -----------------------------------------------------
        # Create entities
        # -----------------------------------------------------

        for entity in normalized_entities:

            self.graph.create_entity(
                entity
            )


        # -----------------------------------------------------
        # Link chunk -> entities
        # -----------------------------------------------------

        for entity in normalized_entities:

            self.graph.link_chunk_to_entity(
                chunk_id=chunk["chunk_id"],
                entity_name=entity
            )
        # -----------------------------------------------------
        # Validate and create relationships
        # -----------------------------------------------------

        valid_relationships = []

        allowed_relationships = {
            "EXTENDS",
            "USES",
            "IMPROVES",
            "PROPOSES",
            "CAPTURES",
            "CONTAINS",
            "BASED_ON",
            "TRAINS",
            "EVALUATES",
            "COMPARES_WITH",
            "AVOIDS",
            "RELATED_TO",
        }

        for rel in result["relationships"]:

            # ---------------------------------------------
            # Normalize source
            # ---------------------------------------------

            source = self.normalize_entity(
                rel["source"]
            )

            # ---------------------------------------------
            # Normalize target
            # ---------------------------------------------

            target = self.normalize_entity(
                rel["target"]
            )

            # ---------------------------------------------
            # Normalize relationship type
            # ---------------------------------------------

            relationship = rel[
                "relationship"
            ].strip().upper()

            # ---------------------------------------------
            # Check relationship type
            # ---------------------------------------------

            if relationship not in allowed_relationships:

                print(
                    f"Rejected relationship type: "
                    f"{relationship}"
                )

                continue

            # ---------------------------------------------
            # Source must exist in entity list
            # ---------------------------------------------

            if source not in normalized_entities:

                print(
                    f"Rejected relationship: "
                    f"source '{source}' "
                    f"is not an entity"
                )

                continue

            # ---------------------------------------------
            # Target must exist in entity list
            # ---------------------------------------------

            if target not in normalized_entities:

                print(
                    f"Rejected relationship: "
                    f"target '{target}' "
                    f"is not an entity"
                )

                continue

            # ---------------------------------------------
            # Validate relationship against source text
            # ---------------------------------------------

            if not self.validate_relationship(
                source,
                relationship,
                target,
                chunk["text"]
            ):

                print(
                    f"Rejected relationship: "
                    f"{source} -- "
                    f"{relationship} --> "
                    f"{target}"
                )

                continue

            # ---------------------------------------------
            # Store valid relationship
            # ---------------------------------------------

            self.graph.create_relationship(
                source=source,
                relationship=relationship,
                target=target,
                chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                page=chunk["page"]
            )

            valid_relationships.append({
                "source": source,
                "relationship": relationship,
                "target": target
            })

        # -----------------------------------------------------
        # Return only validated graph information
        # -----------------------------------------------------

        return {
            "entities": normalized_entities,
            "relationships": valid_relationships
        }

    # =========================================================
    # CLOSE NEO4J CONNECTION
    # =========================================================

    def close(self):

        self.graph.close()