class ContextBuilder:

    def build(
        self,
        query,
        reranked_results
    ):

        context_parts = []

        # --------------------------------
        # Header
        # --------------------------------

        context_parts.append(
            "===== GRAPH RAG RETRIEVAL CONTEXT ====="
        )

        context_parts.append(
            "\nUSER QUERY:"
        )

        context_parts.append(
            query
        )

        context_parts.append(
            "\nThe evidence below was retrieved "
            "from the indexed research papers."
        )

        context_parts.append(
            "Each vector result contains textual "
            "evidence with document and page metadata."
        )

        context_parts.append(
            "Graph results contain relationships "
            "between entities extracted from the papers."
        )

        # --------------------------------
        # Evidence
        # --------------------------------

        for i, result in enumerate(
            reranked_results,
            start=1
        ):

            result_type = result["type"]
            score = result["score"]
            data = result["data"]

            context_parts.append(
                f"\n===== EVIDENCE {i} ====="
            )

            context_parts.append(
                f"SOURCE TYPE: {result_type.upper()}"
            )

            context_parts.append(
                f"RELEVANCE SCORE: {score:.4f}"
            )

            # =================================
            # VECTOR EVIDENCE
            # =================================

            if result_type == "vector":

                document_id = data[
                    "document_id"
                ]

                page = data[
                    "page"
                ]

                chunk_id = data[
                    "chunk_id"
                ]

                context_parts.append(
                    f"DOCUMENT: {document_id}"
                )

                context_parts.append(
                    f"PAGE: {page}"
                )

                context_parts.append(
                    f"CHUNK: {chunk_id}"
                )

                context_parts.append(
                    "\nTEXT EVIDENCE:"
                )

                context_parts.append(
                    data["text"]
                )

                context_parts.append(
                    f"\nSOURCE REFERENCE: "
                    f"[{document_id}, p.{page}]"
                )

            # =================================
            # GRAPH EVIDENCE
            # =================================

            elif result_type == "graph":

                entities = data[
                    "entities"
                ]

                relationships = data[
                    "relationships"
                ]

                path_parts = []

                for j, entity in enumerate(
                    entities
                ):

                    path_parts.append(
                        entity
                    )

                    if j < len(
                        relationships
                    ):

                        path_parts.append(
                            f"-- "
                            f"{relationships[j]}"
                            f" -->"
                        )

                path = " ".join(
                    path_parts
                )

                context_parts.append(
                    "\nGRAPH RELATIONSHIP:"
                )

                context_parts.append(
                    path
                )

                context_parts.append(
                    "\nGRAPH NOTE: "
                    "This relationship represents "
                    "a connection extracted from the "
                    "indexed research papers."
                )

        # --------------------------------
        # Grounding instructions
        # --------------------------------

        context_parts.append(
            "\n===== GROUNDING RULES ====="
        )

        context_parts.append(
            "1. Use only the evidence provided above."
        )

        context_parts.append(
            "2. Do not invent facts or sources."
        )

        context_parts.append(
            "3. Use vector evidence for detailed "
            "factual explanations."
        )

        context_parts.append(
            "4. Use graph evidence to explain "
            "relationships between concepts."
        )

        context_parts.append(
            "5. When making a factual claim from "
            "vector evidence, include its source "
            "reference when appropriate."
        )

        context_parts.append(
            "6. If the evidence is insufficient, "
            "say so explicitly."
        )

        return "\n".join(
            context_parts
        )
