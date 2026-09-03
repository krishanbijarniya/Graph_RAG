from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.graphrag import GraphRAG


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="GraphRAG API",
    description="Local GraphRAG research assistant",
    version="1.0.0"
)


rag = GraphRAG()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    query_entities: list
    citations: list


@app.get("/")
def root():
    return FileResponse(
        BASE_DIR / "static" / "index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):

    result = rag.ask(
        query=request.query,
        vector_top_k=5,
        graph_top_k=20,
        final_top_k=10
    )

    citations = []

    for item in result["processed_results"]:

        if item["type"] != "vector":
            continue

        data = item["data"]

        citation = {
            "document": data["document_id"],
            "page": data["page"],
            "chunk": data["chunk_id"]
        }

        if citation not in citations:
            citations.append(citation)

    return {
        "answer": result["answer"],
        "query_entities": result["query_entities"],
        "citations": citations
    }
