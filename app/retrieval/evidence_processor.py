class EvidenceProcessor:

    def __init__(self):

        self.generic_entities = {
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

    def _graph_signature(self, data):
        """
        Create a normalized signature for a graph path.

        This allows us to detect duplicate or nearly
        duplicate graph evidence.
        """

        entities = [
            entity.lower().strip()
            for entity in data["entities"]
        ]

        relationships = [
            relationship.upper().strip()
            for relationship in data["relationships"]
        ]

        return (
            tuple(entities),
            tuple(relationships)
        )

    def _vector_signature(self, data):
        """
        Identify vector evidence by document/page/chunk.
        """

        return (
            data["document_id"],
            data["page"],
            data["chunk_id"]
        )

    def _is_redundant_graph(self, current, selected):

        current_entities = [
            entity.lower()
            for entity in current["data"]["entities"]
        ]

        current_relationships = current["data"]["relationships"]

        for item in selected:

            if item["type"] != "graph":
                continue

            selected_entities = [
                entity.lower()
                for entity in item["data"]["entities"]
            ]

            selected_relationships = item["data"]["relationships"]

            # Exact duplicate
            if (
                current_entities == selected_entities
                and current_relationships == selected_relationships
            ):
                return True

            # Same source and target relationship
            if (
                len(current_entities) == 2
                and len(selected_entities) == 2
                and current_entities == selected_entities
                and current_relationships == selected_relationships
            ):
                return True

        return False

    def _is_redundant_vector(self, current, selected):

        current_data = current["data"]

        for item in selected:

            if item["type"] != "vector":
                continue

            selected_data = item["data"]

            if (
                self._vector_signature(current_data)
                == self._vector_signature(selected_data)
            ):
                return True

        return False

    def _graph_quality(self, item):

        data = item["data"]

        entities = data["entities"]
        relationships = data["relationships"]

        score = item["score"]

        # Prefer direct relationships
        if len(relationships) == 1:
            score += 0.15

        # Penalize long graph paths
        if len(relationships) > 1:
            score -= 0.05 * (len(relationships) - 1)

        # Penalize generic intermediate nodes
        for entity in entities[1:-1]:

            if entity.lower() in self.generic_entities:
                score -= 0.10

        return max(0.0, min(1.0, score))

    def _vector_quality(self, item):

        data = item["data"]

        score = item["score"]

        text = data["text"].strip()

        # Slight preference for useful textual evidence
        if len(text) > 200:
            score += 0.03

        if len(text) < 80:
            score -= 0.05

        return max(0.0, min(1.0, score))

    def process(
        self,
        reranked_results,
        top_k=8,
        max_graph_results=3,
        max_vector_results=5
    ):
        """
        Process reranked candidates into a compact,
        complementary evidence set.

        Responsibilities:

        1. Remove duplicate evidence.
        2. Prefer high-quality graph paths.
        3. Prefer direct graph relationships.
        4. Keep enough vector evidence for factual grounding.
        5. Limit graph dominance.
        """

        if not reranked_results:
            return []

        candidates = []

        for item in reranked_results:

            processed_item = item.copy()

            if item["type"] == "graph":
                processed_item["processed_score"] = (
                    self._graph_quality(item)
                )

            else:
                processed_item["processed_score"] = (
                    self._vector_quality(item)
                )

            candidates.append(processed_item)

        # Highest quality first
        candidates.sort(
            key=lambda x: x["processed_score"],
            reverse=True
        )

        selected = []

        graph_count = 0
        vector_count = 0

        seen_graph = set()
        seen_vector = set()

        for item in candidates:

            if len(selected) >= top_k:
                break

            item_type = item["type"]

            # -----------------------------
            # GRAPH
            # -----------------------------

            if item_type == "graph":

                if graph_count >= max_graph_results:
                    continue

                signature = self._graph_signature(
                    item["data"]
                )

                if signature in seen_graph:
                    continue

                if self._is_redundant_graph(
                    item,
                    selected
                ):
                    continue

                seen_graph.add(signature)

                selected.append(item)

                graph_count += 1

            # -----------------------------
            # VECTOR
            # -----------------------------

            elif item_type == "vector":

                if vector_count >= max_vector_results:
                    continue

                signature = self._vector_signature(
                    item["data"]
                )

                if signature in seen_vector:
                    continue

                if self._is_redundant_vector(
                    item,
                    selected
                ):
                    continue

                seen_vector.add(signature)

                selected.append(item)

                vector_count += 1

        # Final ordering by processed relevance
        selected.sort(
            key=lambda x: x["processed_score"],
            reverse=True
        )

        return selected
