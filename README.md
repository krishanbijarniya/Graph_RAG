# GraphRAG — Local Research Assistant

A fully local **GraphRAG (Graph Retrieval-Augmented Generation)** system for answering questions over research papers using **semantic vector retrieval + knowledge-graph retrieval**.

The project runs without OpenAI API credits by using:

- **Qwen 2.5 7B** for local generation and graph/entity extraction
- **Ollama** for local LLM inference
- **Qdrant** for vector search
- **Neo4j** for the knowledge graph
- **BGE-small-en-v1.5** for embeddings
- **FastAPI** for the API
- A lightweight **ChatGPT-style web UI** for querying the system
- **Docker Compose** for reproducible service deployment

---

## Architecture

```text
                              User
                               |
                               v
                     ChatGPT-style Web UI
                               |
                               v
                          FastAPI API
                               |
                               v
                        GraphRAG.ask()
                               |
                     Query Entity Extraction
                               |
                +--------------+--------------+
                |                             |
                v                             v
        Vector Retrieval               Graph Retrieval
            Qdrant                       Neo4j
                |                             |
                +--------------+--------------+
                               |
                               v
                       Hybrid Reranker
                               |
                               v
                      Evidence Processor
                               |
                               v
                       Context Builder
                               |
                               v
                         Qwen 2.5 7B
                           (Ollama)
                               |
                               v
                    Grounded Answer + Citations
```

### Why use both vector and graph retrieval?

**Vector retrieval** is strong at finding textual evidence:

- explanations
- experimental results
- numerical findings
- implementation details
- method descriptions

**Graph retrieval** is strong at finding structured relationships:

```text
SelfExtend
    |
    +-- IMPROVES --> Long-Context Performance

SelfExtend
    |
    +-- USES --> Grouped Attention

SelfExtend
    |
    +-- AVOIDS --> Fine-tuning
```

The system combines both forms of evidence before generating the final answer.

---

# Features

- Local LLM inference with **Qwen 2.5 7B + Ollama**
- Local vector database with **Qdrant**
- Local knowledge graph with **Neo4j**
- Scientific PDF ingestion
- Token-aware chunking
- BGE embeddings
- Query entity extraction
- Vector retrieval
- Graph traversal
- Hybrid score-based reranking
- Evidence deduplication and selection
- Structured context construction
- Grounded answer generation
- Claim-level source citations
- FastAPI REST API
- Local web UI
- Docker Compose deployment
- Persistent Qdrant and Neo4j storage
- End-to-end tests

> **Note:** The current hybrid reranker is a custom score-based fusion approach. It is **not RRF (Reciprocal Rank Fusion)**.

---

# Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| LLM | Qwen 2.5 7B |
| LLM Runtime | Ollama |
| Embeddings | `BAAI/bge-small-en-v1.5` |
| Embedding Dimension | 384 |
| Vector Database | Qdrant |
| Vector Distance | Cosine |
| Graph Database | Neo4j |
| PDF Processing | pypdf |
| Graph Extraction | Qwen 2.5 7B |
| API | FastAPI |
| Web Server | Uvicorn |
| Containerization | Docker / Docker Compose |

---

# Project Structure

```text
Graph_RAG/
│
├── app/
│   ├── __init__.py
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedder.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   └── chunker.py
│   │
│   ├── vector_store/
│   │   ├── __init__.py
│   │   ├── qdrant_store.py
│   │   └── indexer.py
│   │
│   ├── graph_builder/
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   └── pipeline.py
│   │
│   ├── graph_store/
│   │   ├── __init__.py
│   │   └── neo4j_store.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_retriever.py
│   │   ├── graph_retriever.py
│   │   ├── hybrid_retriever.py
│   │   ├── hybrid_reranker.py
│   │   ├── evidence_processor.py
│   │   ├── query_entity_extractor.py
│   │   └── context_builder.py
│   │
│   ├── generation.py
│   ├── graphrag.py
│   ├── api.py
│   │
│   └── static/
│       └── index.html
│
├── data/
│   └── papers/
│       ├── 2307.06435v10.pdf
│       ├── 2401.01325v3.pdf
│       └── 2401.10491v2.pdf
│
├── test/
│   ├── test_pdf.py
│   ├── test_chunker.py
│   ├── test_embeddings.py
│   ├── test_qdrant.py
│   ├── test_indexer.py
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   ├── test_ollama.py
│   ├── test_extractor.py
│   ├── test_graph_pipeline.py
│   ├── test_graph_ingestion.py
│   ├── test_neo4j.py
│   ├── test_graph_queries.py
│   ├── test_graph_retriever.py
│   ├── test_vector_retriever.py
│   ├── test_hybrid_retriever.py
│   ├── test_query_entity_extractor.py
│   ├── test_hybrid_reranker.py
│   ├── test_context_builder.py
│   └── test_graphrag.py
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── requirements.txt
└── README.md
```

---

# Retrieval Pipeline

## 1. PDF Ingestion

Research papers are placed in:

```text
data/papers/
```

The PDF loader extracts:

- document ID
- page number
- page text

Example:

```text
Document: 2401.01325v3
Page: 7
```

---

## 2. Token-Aware Chunking

Documents are divided into smaller chunks using the tokenizer associated with:

```text
BAAI/bge-small-en-v1.5
```

Current configuration:

```text
Chunk size: 350 tokens
Overlap:      80 tokens
```

Each chunk stores metadata such as:

```text
chunk_id
document_id
page
chunk_number
token_count
text
```

Example:

```text
2401.01325v3_p8_c3
```

---

## 3. Embeddings

Every chunk is converted into a vector using:

```text
BAAI/bge-small-en-v1.5
```

The vectors have:

```text
Dimension: 384
Distance:  Cosine
```

---

## 4. Qdrant Vector Store

The current collection is:

```text
research_papers
```

Configuration:

```text
Vector size: 384
Distance:    Cosine
```

At query time:

```text
User Question
      |
      v
Embedding Model
      |
      v
384-dimensional Query Vector
      |
      v
Qdrant
      |
      v
Top-K Research Chunks
```

Vector retrieval is primarily responsible for textual grounding.

---

# Knowledge Graph

## 5. Graph Construction

Qwen 2.5 7B extracts entities and explicit relationships from each chunk.

Controlled relationship types include:

```text
EXTENDS
USES
IMPROVES
PROPOSES
CAPTURES
CONTAINS
BASED_ON
TRAINS
EVALUATES
COMPARES_WITH
AVOIDS
RELATED_TO
```

The extraction process is intentionally constrained:

- relationships must be explicitly supported by the source text
- no unsupported inference is added
- relationship endpoints must be extracted entities
- common entity aliases are normalized
- invalid relationship types are rejected
- selected negated relationships are filtered

Example:

```text
SelfExtend
    |
    +-- IMPROVES --> Long-Context Performance
```

---

## 6. Neo4j Graph Store

The graph uses a simple schema:

```text
(:Entity)
```

with relationships stored as:

```text
[:RELATED_TO]
```

The semantic relationship type is stored as a property:

```text
r.type
```

Example:

```text
(SelfExtend)-[:RELATED_TO {
    type: "IMPROVES"
}]->(Long-Context Performance)
```

This keeps the graph schema simple while preserving semantic relationship types.

---

# Query Entity Extraction

Before graph retrieval, the user's question is analyzed to identify important technical entities.

Example question:

```text
How does SelfExtend improve long-context performance?
```

Extracted entities:

```text
SelfExtend
Long-Context Performance
```

These entities become starting points for graph traversal.

---

# Vector Retrieval

The vector retriever:

1. Embeds the user's question.
2. Searches Qdrant.
3. Retrieves the highest-scoring chunks.
4. Returns text and source metadata.

Example:

```text
Document: 2401.01325v3
Page:     8
Chunk:    2401.01325v3_p8_c3
Score:    0.7444
```

---

# Graph Retrieval

The graph retriever starts from query entities and traverses the knowledge graph.

Example:

```text
SelfExtend
    |
    +-- IMPROVES --> Long-Context Performance
```

It can also discover multi-hop paths:

```text
SelfExtend
    |
    +-- EVALUATES --> Perplexity
                         |
                         +-- CAPTURES --> Long-Context Performance
```

Graph ranking considers:

- entity overlap
- target matching
- relationship importance
- path length
- direct relationship preference
- generic entity penalties

---

# Hybrid Reranking

Vector and graph candidates are scored together.

### Vector signals

```text
Semantic similarity
Query-term overlap
Query-entity overlap
```

### Graph signals

```text
Entity overlap
Target matching
Relationship importance
Path length
Generic entity penalties
```

The current implementation uses a **custom score-based fusion**, rather than RRF.

Conceptually:

```text
Qdrant Results
      |
      +------------------+
                         |
                         v
                  Hybrid Reranker
                         ^
                         |
      +------------------+
      |
Neo4j Graph Results
```

---

# Evidence Processing

The Evidence Processor decides which retrieved evidence should actually reach the LLM.

It:

- removes duplicates
- limits graph dominance
- favors useful direct relationships
- removes redundant vector results
- preserves complementary evidence
- creates a compact evidence set

Current limits:

```text
Maximum graph evidence:  3
Maximum vector evidence: 5
Final evidence:           8
```

---

# Context Builder

Selected evidence is converted into structured context for Qwen.

Example vector evidence:

```text
===== EVIDENCE 1 =====

SOURCE TYPE: VECTOR
DOCUMENT: 2401.01325v3
PAGE: 8
CHUNK: 2401.01325v3_p8_c3

TEXT EVIDENCE:
...

CITATION:
[2401.01325v3, p.8]
```

Graph evidence is represented separately:

```text
===== EVIDENCE 2 =====

SOURCE TYPE: GRAPH

GRAPH RELATIONSHIP:
SelfExtend -- IMPROVES --> Long-Context Performance
```

---

# Local Generation

Qwen 2.5 7B generates the final answer through Ollama.

The generation prompt enforces:

```text
Use only retrieved evidence.
Do not use outside knowledge.
Do not invent citations.
Prefer vector evidence for factual claims.
Use graph evidence for relationships.
Cite important claims immediately.
```

This makes the final response grounded in the retrieved research material.

---

# Web UI

The project includes a local ChatGPT-style interface.

The UI provides:

- conversation-style question/answer display
- local service status
- query input
- loading state
- source citations
- extracted query entities
- new-chat control

Open:

```text
http://localhost:8000
```

The browser communicates with:

```text
POST /query
```

---

# REST API

## Health Check

```http
GET /health
```

Example:

```json
{
  "status": "healthy"
}
```

## Query

```http
POST /query
Content-Type: application/json
```

Request:

```json
{
  "query": "How does SelfExtend improve long-context performance?"
}
```

Response structure:

```json
{
  "answer": "Grounded answer...",
  "query_entities": [
    "SelfExtend",
    "Long-Context Performance"
  ],
  "citations": [
    {
      "document": "2401.01325v3",
      "page": 8
    }
  ]
}
```

---

# Docker Deployment

The current deployment uses Docker Compose for:

```text
graphrag-api
graphrag-qdrant
graphrag-neo4j
```

Ollama runs on the host machine and is exposed to the API container through:

```text
host.docker.internal:11434
```

Architecture:

```text
                         Host Machine
┌──────────────────────────────────────────────────────┐
│                                                      │
│  Ollama                                              │
│  Qwen 2.5 7B                                         │
│      ^                                               │
│      | host.docker.internal:11434                    │
│      |                                               │
│  ┌───┴───────────────────────────────────────────┐   │
│  │ Docker Compose                               │   │
│  │                                               │   │
│  │  graphrag-api                                │   │
│  │      |              |                        │   │
│  │      v              v                        │   │
│  │   Qdrant         Neo4j                       │   │
│  │   :6333          :7687                       │   │
│  │                                               │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

# Environment Configuration

The current `.env` configuration is:

```env
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=research_papers

NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b
```

For a real deployment, change the Neo4j password and do not commit secrets.

Add `.env` to `.gitignore`:

```text
.env
```

---

# Running the Project

## Prerequisites

Install:

- Python 3
- Docker
- Docker Compose
- Ollama
- NVIDIA GPU + drivers if GPU inference is desired

The current development environment uses:

```text
Python:       3.14.4
Ollama:       0.33.2
Qwen:         qwen2.5:7b
CUDA:         13.2
GPU:          NVIDIA RTX 4060 8 GB
```

---

## 1. Start Ollama

Verify:

```bash
ollama --version
```

Check models:

```bash
ollama list
```

Pull Qwen if required:

```bash
ollama pull qwen2.5:7b
```

Test:

```bash
ollama run qwen2.5:7b
```

For Docker-to-host connectivity, Ollama must listen on an address reachable from the Docker bridge. The current setup uses:

```text
OLLAMA_HOST=0.0.0.0:11434
```

---

## 2. Start the Docker Stack

From the project root:

```bash
cd ~/Graph_RAG
```

Build and start:

```bash
docker compose up -d --build
```

Check services:

```bash
docker compose ps
```

Expected services:

```text
graphrag-api
graphrag-qdrant
graphrag-neo4j
```

---

## 3. Check the API

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"healthy"}
```

---

## 4. Open the Web UI

Open in a browser:

```text
http://localhost:8000
```

Then ask a question such as:

```text
How does SelfExtend improve long-context performance?
```

---

# Data Ingestion

The current prototype contains three research papers:

```text
2307.06435v10.pdf
2401.01325v3.pdf
2401.10491v2.pdf
```

Current ingestion:

```text
Total PDF chunks:        481
Qdrant vector chunks:    481

Neo4j documents:           3
Neo4j chunks:            475
Neo4j entities:         3899
Neo4j relationships:    1571
```

The six-chunk difference between Qdrant and Neo4j is due to graph-extraction failures for six chunks; vector ingestion succeeded for all 481 chunks.

---

# Ingestion Flow

When a new PDF is added:

```text
New PDF
   |
   v
PDF Loader
   |
   v
Token-Aware Chunker
   |
   +----------------------+
   |                      |
   v                      v
Embeddings          Graph Extraction
   |                      |
   v                      v
Qdrant                  Neo4j
   |                      |
   +----------+-----------+
              |
              v
       Searchable Knowledge Base
```

---

# Example End-to-End Query

Question:

```text
How does SelfExtend improve long-context performance?
```

Query entities:

```text
SelfExtend
Long-Context Performance
```

Graph evidence:

```text
SelfExtend
    |
    +-- IMPROVES --> Long-Context Performance
```

Vector evidence comes from the relevant research-paper chunks.

The final generator produces a grounded answer with source citations such as:

```text
[2401.01325v3, p.8]
[2401.01325v3, p.7]
[2401.01325v3, p.6]
```

---

# Testing

Activate the Python environment:

```bash
source .venv/bin/activate
```

Examples:

```bash
python -m test.test_pdf
python -m test.test_chunker
python -m test.test_embeddings
python -m test.test_qdrant
python -m test.test_neo4j
python -m test.test_vector_retriever
python -m test.test_graph_retriever
python -m test.test_hybrid_retriever
python -m test.test_query_entity_extractor
python -m test.test_hybrid_reranker
python -m test.test_context_builder
python -m test.test_graphrag
```

The end-to-end test verifies the retrieval and generation pipeline.

---

# Persistent Storage

Docker Compose uses persistent volumes for databases:

```text
Qdrant
└── qdrant_data

Neo4j
├── neo4j_data
├── neo4j_logs
├── neo4j_import
└── neo4j_plugins
```

This prevents database contents from disappearing when containers are recreated.

Ollama model files remain on the host in the normal Ollama model directory.

---

# Service Ports

| Service | Port | Purpose |
|---|---:|---|
| GraphRAG API | 8000 | Web UI + REST API |
| Qdrant | 6333 | Vector database |
| Neo4j Browser | 7474 | Graph UI |
| Neo4j Bolt | 7687 | Graph database connection |
| Ollama | 11434 | Local LLM API |

For a production deployment, Qdrant, Neo4j, and Ollama should not be exposed directly to the public Internet.

---

# Graph Quality

The graph extraction pipeline is intentionally conservative, but a 7B local model can still produce noisy or overly generic entities/relationships.

Known areas for future improvement include:

- stronger entity deduplication
- better ontology constraints
- confidence scoring
- improved relation validation
- section-aware extraction
- document-level entity resolution
- better handling of generic entities
- graph quality evaluation
- improved multi-hop ranking

The current system prioritizes getting a complete local GraphRAG pipeline working end-to-end before deeper graph-quality optimization.

---

# Current Project Status

## Implemented

```text
[x] PDF loading
[x] Token-aware chunking
[x] BGE embeddings
[x] Qdrant vector indexing
[x] Neo4j graph indexing
[x] Qwen local inference
[x] Query entity extraction
[x] Vector retrieval
[x] Graph retrieval
[x] Hybrid score-based reranking
[x] Evidence processing
[x] Context building
[x] Grounded generation
[x] Source citations
[x] FastAPI API
[x] Local web UI
[x] Dockerfile
[x] Docker Compose deployment
[x] Persistent Qdrant storage
[x] Persistent Neo4j storage
[x] End-to-end testing
```

## Next Engineering Steps

```text
[ ] RRF-based retrieval fusion
[ ] Improve graph entity resolution
[ ] Improve graph relationship precision
[ ] Retrieval evaluation dataset
[ ] Automated retrieval metrics
[ ] Answer quality evaluation
[ ] Authentication
[ ] Rate limiting
[ ] HTTPS / reverse proxy
[ ] Production monitoring
[ ] Multi-user concurrency testing
[ ] Better UI source exploration
```

---

# Design Principles

The project follows several important principles:

### 1. Local-first

The core pipeline does not require OpenAI API credits.

### 2. Retrieval before generation

The LLM should answer from retrieved evidence rather than relying on unrestricted model knowledge.

### 3. Vector + graph complementarity

Vectors provide detailed textual evidence while the graph provides structured relationships.

### 4. Evidence selection before generation

Not every retrieved result should be sent to the LLM. Evidence is deduplicated and filtered first.

### 5. Explicit graph relationships

The graph extractor is instructed to extract relationships supported by source text rather than inventing new relationships.

### 6. Modular architecture

Each major component can be replaced independently:

```text
PDF Loader
    ↓
Chunker
    ↓
Embedder
    ↓
Qdrant

Graph Extractor
    ↓
Neo4j

Retrievers
    ↓
Reranker
    ↓
Evidence Processor
    ↓
Context Builder
    ↓
Generator
```

---

# Security Notes

Before exposing the system beyond a trusted local network:

- change default Neo4j credentials
- keep `.env` out of Git
- add authentication to the API
- add rate limiting
- put FastAPI behind HTTPS
- use a reverse proxy
- keep Qdrant private
- keep Neo4j private
- keep Ollama private
- restrict access to port `11434`

Only the intended application/API entry point should be publicly accessible.

---

# License

This project is currently a personal research/development prototype. Add an explicit license before distributing it publicly.
