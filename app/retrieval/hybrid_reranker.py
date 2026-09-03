class HybridReranker:

    def __init__(self):

        self.relationship_weights = {
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

    def _query_terms(self, query):

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
            query.lower()
            .replace("?", "")
            .replace(",", "")
            .replace(".", "")
            .split()
        )

        return {
            word
            for word in words
            if word not in stop_words
        }

    def _score_vector(
        self,
        result,
        query,
        query_entities
    ):

        score = 0.0

        # --------------------------------
        # Semantic similarity: 60%
        # --------------------------------

        similarity = max(
            0.0,
            min(1.0, result["score"])
        )

        score += similarity * 0.60

        # --------------------------------
        # Query term overlap: 15%
        # --------------------------------

        query_terms = self._query_terms(query)

        text = result["text"].lower()

        matched_terms = 0

        for term in query_terms:

            if term in text:
                matched_terms += 1

        if query_terms:

            term_ratio = (
                matched_terms /
                len(query_terms)
            )

        else:

            term_ratio = 0.0

        score += term_ratio * 0.15

        # --------------------------------
        # Query entity match: 25%
        # --------------------------------

        matched_entities = 0

        for entity in query_entities:

            if entity.lower() in text:
                matched_entities += 1

        if query_entities:

            entity_ratio = (
                matched_entities /
                len(query_entities)
            )

        else:

            entity_ratio = 0.0

        score += entity_ratio * 0.25

        return max(
            0.0,
            min(1.0, score)
        )

    def _score_graph(
        self,
        result,
        query,
        query_entities
    ):

        entities = result["entities"]
        relationships = result["relationships"]

        score = 0.0

        query_entities_lower = {
            entity.lower()
            for entity in query_entities
        }

        query_terms = self._query_terms(query)

        # --------------------------------
        # Query entity relevance: 30%
        # --------------------------------

        matched_entities = 0

        for entity in entities:

            if entity.lower() in query_entities_lower:
                matched_entities += 1

        if query_entities:

            entity_ratio = (
                matched_entities /
                len(query_entities)
            )

        else:

            entity_ratio = 0.0

        score += entity_ratio * 0.30

        # --------------------------------
        # Direct target match: 25%
        # --------------------------------

        if len(entities) >= 2:

            target = entities[-1].lower()

            if target in query_entities_lower:
                score += 0.25

        # --------------------------------
        # Query word overlap: 15%
        # --------------------------------

        matched_words = 0

        for entity in entities:

            entity_words = {
                word.strip(".,!?;:").lower()
                for word in entity.split()
            }

            overlap = entity_words & query_terms

            matched_words += len(overlap)

        if query_terms:

            word_ratio = min(
                1.0,
                matched_words /
                len(query_terms)
            )

        else:

            word_ratio = 0.0

        score += word_ratio * 0.15

        # --------------------------------
        # Relationship importance: 20%
        # --------------------------------

        relationship_score = 0.0

        for relationship in relationships:

            relationship_score += (
                self.relationship_weights.get(
                    relationship,
                    1
                )
            )

        relationship_score = min(
            1.0,
            relationship_score / 6.0
        )

        score += relationship_score * 0.20

        # --------------------------------
        # Path length penalty
        # --------------------------------

        hop_count = len(relationships)

        if hop_count > 1:

            penalty = min(
                0.10,
                (hop_count - 1) * 0.05
            )

            score -= penalty

        # --------------------------------
        # Generic entity penalty
        # --------------------------------

        generic_count = 0

        for entity in entities[1:]:

            if entity.lower() in self.generic_entities:
                generic_count += 1

        score -= min(
            0.10,
            generic_count * 0.05
        )

        return max(
            0.0,
            min(1.0, score)
        )

    def rerank(
        self,
        query,
        query_entities,
        vector_results,
        graph_results,
        top_k=10,
        max_consecutive_graph=2,
        max_consecutive_vector=3
    ):

        candidates = []

        # --------------------------------
        # Score vector candidates
        # --------------------------------

        for result in vector_results:

            score = self._score_vector(
                result=result,
                query=query,
                query_entities=query_entities
            )

            candidates.append({
                "type": "vector",
                "score": score,
                "data": result
            })

        # --------------------------------
        # Score graph candidates
        # --------------------------------

        for result in graph_results:

            score = self._score_graph(
                result=result,
                query=query,
                query_entities=query_entities
            )

            candidates.append({
                "type": "graph",
                "score": score,
                "data": result
            })

        # --------------------------------
        # Sort by relevance first
        # --------------------------------

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # --------------------------------
        # Diversity-aware selection
        # --------------------------------

        selected = []

        remaining = candidates.copy()

        consecutive_graph = 0
        consecutive_vector = 0

        while remaining and len(selected) < top_k:

            chosen_index = None

            # First try the highest-scoring
            # candidate that does not violate
            # modality diversity.

            for index, candidate in enumerate(
                remaining
            ):

                candidate_type = candidate["type"]

                if (
                    candidate_type == "graph"
                    and consecutive_graph
                    >= max_consecutive_graph
                ):
                    continue

                if (
                    candidate_type == "vector"
                    and consecutive_vector
                    >= max_consecutive_vector
                ):
                    continue

                chosen_index = index
                break

            # If every candidate violates the
            # diversity rule, use the best remaining
            # candidate so retrieval never stops early.

            if chosen_index is None:
                chosen_index = 0

            chosen = remaining.pop(
                chosen_index
            )

            selected.append(chosen)

            # --------------------------------
            # Update modality counters
            # --------------------------------

            if chosen["type"] == "graph":

                consecutive_graph += 1
                consecutive_vector = 0

            else:

                consecutive_vector += 1
                consecutive_graph = 0


        selected.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return selected
        
