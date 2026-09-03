from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.query_entity_extractor import QueryEntityExtractor
from app.retrieval.hybrid_reranker import HybridReranker
from app.retrieval.evidence_processor import EvidenceProcessor


class HybridRetriever:

    def __init__(self):

        self.vector_retriever = VectorRetriever()
        self.graph_retriever = GraphRetriever()
        self.entity_extractor = QueryEntityExtractor()
        self.reranker = HybridReranker()
        self.evidence_processor = EvidenceProcessor()

    def search(
        self,
        query,
        vector_top_k=5,
        graph_top_k=20,
        final_top_k=10
    ):

        # --------------------------------
        # 1. Extract query entities
        # --------------------------------

        entity_names = self.entity_extractor.extract(
            query
        )

        # --------------------------------
        # 2. Vector retrieval
        # --------------------------------

        vector_results = self.vector_retriever.search(
            query=query,
            top_k=vector_top_k
        )

        # --------------------------------
        # 3. Graph retrieval
        # --------------------------------

        graph_results = self.graph_retriever.search(
            entity_names=entity_names,
            query=query,
            max_hops=2,
            top_k=graph_top_k
        )

        # --------------------------------
        # 4. Hybrid reranking
        # --------------------------------

        reranked_results = self.reranker.rerank(
            query=query,
            query_entities=entity_names,
            vector_results=vector_results,
            graph_results=graph_results,
            top_k=final_top_k
        )

        processed_results = self.evidence_processor.process(
            reranked_results=reranked_results,
            top_k=8,
            max_graph_results=3,
            max_vector_results=5
        )
        return {
            "vector_results": vector_results,
            "graph_results": graph_results,
            "reranked_results": reranked_results,
            "processed_results": processed_results,
            "query_entities": entity_names
        }
