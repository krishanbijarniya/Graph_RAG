from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.context_builder import ContextBuilder
from app.generation import QwenGenerator


class GraphRAG:

    def __init__(self):

        self.retriever = HybridRetriever()
        self.context_builder = ContextBuilder()
        self.generator = QwenGenerator()

    def ask(
        self,
        query,
        vector_top_k=5,
        graph_top_k=20,
        final_top_k=10
    ):

        # --------------------------------
        # 1. Hybrid retrieval
        # --------------------------------

        results = self.retriever.search(
            query=query,
            vector_top_k=vector_top_k,
            graph_top_k=graph_top_k,
            final_top_k=final_top_k
        )

        query_entities = results[
            "query_entities"
        ]

        vector_results = results[
            "vector_results"
        ]

        graph_results = results[
            "graph_results"
        ]

        reranked_results = results[
            "reranked_results"
        ]

        # --------------------------------
        # 2. Build ranked context
        # --------------------------------

        context = self.context_builder.build(
            query=query,
            reranked_results=reranked_results
        )

        # --------------------------------
        # 3. Generate answer
        # --------------------------------

        answer = self.generator.generate(
            query=query,
            context=context
        )

        # --------------------------------
        # 4. Return complete result
        # --------------------------------

        return {
            "answer": answer,
            "query_entities": query_entities,
            "vector_results": vector_results,
            "graph_results": graph_results,
            "reranked_results": reranked_results,
            "context": context
        }
