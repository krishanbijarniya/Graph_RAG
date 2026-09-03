# GraphRAG — Local Research Assistant

A local **GraphRAG (Graph Retrieval-Augmented Generation)** system for answering questions over research papers using both **semantic vector retrieval** and **knowledge-graph retrieval**.

The project is designed to run locally with **Ollama/Qwen**, **Qdrant**, and **Neo4j**, so the core question-answering pipeline does not depend on OpenAI API credits.

---

## Overview

Traditional RAG retrieves relevant text chunks from a vector database.

This project combines two complementary retrieval strategies:

```text
                         User Question
                              |
                              v
                    Query Entity Extraction
                              |
                 +------------+------------+
                 |                         |
                 v                         v
          Vector Retrieval           Graph Retrieval
             (Qdrant)                 (Neo4j)
                 |                         |
                 +------------+------------+
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
                              |
                              v
                    Grounded Answer
                    + Citations
```

### Why combine vectors and graphs?

**Vector retrieval** is useful for finding detailed textual evidence such as:

- explanations
- experimental results
- numerical findings
- implementation details
- descriptions of methods

**Graph retrieval** is useful for discovering relationships such as:

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

Combining both allows the system to retrieve **textual evidence + structured relationships**.

---

# Features

- Local LLM inference using **Qwen 2.5 7B through Ollama**
- Local vector search using **Qdrant**
- Local knowledge graph using **Neo4j**
- Scientific PDF ingestion
- Token-aware document chunking
- BGE embeddings
- Query entity extraction
- Vector retrieval
- Graph traversal
- Hybrid reranking
- Evidence deduplication and selection
- Context construction
- Grounded answer generation
- Claim-level source citations
- Modular Python architecture
- End-to-end test suite

---

# Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| LLM | Qwen 2.5 7B |
| LLM Runtime | Ollama |
| Embeddings | `BAAI/bge-small-en-v1.5` |
| Vector Database | Qdrant |
| Graph Database | Neo4j |
| PDF Processing | PyMuPDF |
| Graph Extraction | Qwen 2.5 7B |
| Vector Dimension | 384 |
| Vector Distance | Cosine |
| Containerization | Docker |

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
│   └── graphrag.py
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
└── README.md
```

---

# System Architecture

## 1. PDF Ingestion

Research papers are placed inside:

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

## 2. Chunking

Documents are divided into smaller token-aware chunks.

Current configuration:

```text
Chunk size: 350 tokens
Overlap:     80 tokens
```

The tokenizer is associated with:

```text
BAAI/bge-small-en-v1.5
```

Chunk metadata includes:

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

# 3. Embeddings

Each chunk is converted into a vector using:

```text
BAAI/bge-small-en-v1.5
```

The embedding dimension is:

```text
384
```

These vectors are stored in Qdrant.

---

# 4. Qdrant Vector Store

Qdrant stores the embedded chunks.

Current configuration:

```text
Collection:
research_papers

Vector size:
384

Distance:
Cosine
```

Conceptually:

```text
Research Chunk
      |
      v
Embedding Model
      |
      v
384-dimensional Vector
      |
      v
Qdrant
```

At query time, the question is embedded using the same embedding model and the nearest chunks are retrieved.

---

# 5. Knowledge Graph Construction

The system also extracts entities and relationships from the research papers.

Qwen 2.5 7B is used for structured extraction.

Example:

```text
SelfExtend
    |
    +-- IMPROVES --> Long-Context Performance
```

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

The extraction prompt is designed to reduce hallucinated relationships by requiring relationships to be explicitly supported by the source text.

---

# 6. Neo4j Graph Store

The extracted knowledge graph is stored in Neo4j.

The graph currently uses:

```text
(:Entity)
```

nodes and:

```text
[:RELATED_TO]
```

relationships.

The semantic relationship is stored as a relationship property:

```text
r.type
```

For example:

```text
(SelfExtend)-[:RELATED_TO {
    type: "IMPROVES"
}]->(Long-Context Performance)
```

This design keeps the graph schema simple while preserving semantic relationship types.

---

# 7. Query Entity Extraction

Before graph retrieval, the user's question is analyzed to identify important technical entities.

Example:

```text
Question:

How does SelfExtend improve long-context performance?
```

The extractor returns:

```json
{
  "entities": [
    "SelfExtend",
    "Long-Context Performance"
  ]
}
```

This gives the graph retriever meaningful starting points.

---

# 8. Vector Retrieval

The vector retriever:

1. Embeds the user question.
2. Searches Qdrant.
3. Retrieves the highest-scoring chunks.
4. Returns text and source metadata.

Example:

```text
Document: 2401.01325v3
Page: 8
Chunk: 2401.01325v3_p8_c3
Score: 0.7444
```

Vector retrieval is primarily responsible for **factual textual grounding**.

---

# 9. Graph Retrieval

The graph retriever starts from extracted query entities and traverses the graph.

Example:

```text
SelfExtend
    |
    +-- IMPROVES --> Long-Context Performance
```

It can also find multi-hop relationships:

```text
SelfExtend
    |
    +-- EVALUATES --> Perplexity
                         |
                         +-- CAPTURES --> Long-Context Performance
```

Graph retrieval uses:

- relationship weights
- query/entity overlap
- path length
- generic entity penalties
- direct relationship preference

to rank graph paths.

---

# 10. Hybrid Reranking

Vector and graph candidates are scored together.

The reranker considers different signals.

### Vector evidence

```text
Semantic similarity
Query-term overlap
Query-entity overlap
```

### Graph evidence

```text
Entity overlap
Target matching
Relationship importance
Path length
Generic entity penalties
```

This creates a common relevance score between vector and graph candidates.

---

# 11. Evidence Processing

The reranker answers:

> "How relevant is this result?"

The Evidence Processor answers:

> "Which evidence should actually reach the LLM?"

This separation is intentional.

The Evidence Processor:

- removes duplicates
- limits graph dominance
- favors direct graph relationships
- removes redundant vector results
- preserves complementary evidence
- creates a compact evidence set

Current limits:

```text
Maximum graph evidence: 3
Maximum vector evidence: 5
Final evidence: 8
```

---

# 12. Context Builder

The selected evidence is converted into a structured context for Qwen.

Example:

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

This makes the source type explicit to the generator.

---

# 13. Local Generation

Qwen 2.5 7B generates the final answer using Ollama.

The generation prompt enforces:

```text
Use only retrieved evidence.
Do not use outside knowledge.
Do not invent citations.
Prefer vector evidence for factual claims.
Use graph evidence for relationships.
Cite important claims immediately.
```

Example:

```text
SelfExtend can extend the context window of
Phi-2 from 2k to 4k, 6k, and 8k, with
substantial improvements on long-context tasks
[2401.01325v3, p.7].
```

---

# Example End-to-End Query

Question:

```text
How does SelfExtend improve long-context performance?
```

The system extracts:

```text
SelfExtend
Long-Context Performance
```

Graph retrieval finds:

```text
SelfExtend
    |
    +-- IMPROVES --> Long-Context Performance
```

Vector retrieval finds relevant research-paper chunks.

The final answer can contain claims such as:

```text
SelfExtend improves long-context performance
without requiring additional fine-tuning or
training [2401.01325v3, p.8].

It can extend the context window of Phi-2 from
2k to 4k, 6k, and 8k, producing substantial
improvements on long-context tasks [2401.01325v3, p.7].

It operates during inference and can preserve
short-context performance [2401.01325v3, p.6].
```

The graph can additionally support the conceptual relationship:

```text
SelfExtend
    |
    +-- IMPROVES --> Long-Context Performance
```

---

# Current Dataset

The current prototype has been tested with three research papers:

```text
2307.06435v10.pdf
2401.01325v3.pdf
2401.10491v2.pdf
```

Current ingestion results:

```text
Total chunks: 481
```

The Qdrant collection contains:

```text
481 vectorized chunks
```

The graph ingestion produced thousands of entities and relationships.

---


---

# Deployment

The project can be used in two ways:

1. **Local deployment** — ideal for development, research, and personal use.
2. **Server deployment** — suitable when multiple users need to access GraphRAG through an API.

## Local Deployment

For a single user, the simplest architecture is:

```text
                 Local Machine
┌───────────────────────────────────────────────┐
│                                               │
│   GraphRAG Python Application                 │
│              │                                │
│       ┌──────┼──────────┐                     │
│       ▼      ▼          ▼                     │
│    Qdrant  Neo4j      Ollama                  │
│                        │                      │
│                        ▼                      │
│                   Qwen 2.5 7B                 │
│                                               │
└───────────────────────────────────────────────┘
```

### Requirements

A machine running the complete local stack should have:

- Python 3
- Docker
- Ollama
- sufficient disk space for models and databases
- sufficient RAM
- a GPU with enough VRAM if GPU-accelerated Qwen inference is desired

The current development setup uses Qwen 2.5 7B through Ollama and has been tested with GPU inference.

### Start the infrastructure

Start Qdrant:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Start Neo4j:

```bash
docker run \
  --name neo4j-graphrag \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Start/check Ollama:

```bash
ollama list
```

Pull the model if required:

```bash
ollama pull qwen2.5:7b
```

Activate the Python environment:

```bash
source .venv/bin/activate
```

Then run the end-to-end test:

```bash
python -m test.test_graphrag
```

---

# Server Deployment

For a multi-user deployment, the recommended architecture is:

```text
                         Internet
                            |
                            v
                  ┌──────────────────┐
                  │ Reverse Proxy    │
                  │ Nginx / HTTPS    │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ FastAPI GraphRAG │
                  │       API        │
                  └────────┬─────────┘
                           |
             ┌─────────────┼─────────────┐
             |             |             |
             v             v             v
        ┌────────┐    ┌────────┐    ┌────────┐
        │ Qdrant │    │ Neo4j  │    │ Ollama │
        └────────┘    └────────┘    └───┬────┘
                                       |
                                       v
                                  Qwen 2.5 7B
```

The important security principle is:

> **Only the API/reverse proxy should be publicly accessible.**

Qdrant, Neo4j, and Ollama should remain on a private network and should not be exposed directly to the Internet.

---

## Recommended Server Components

| Component | Purpose |
|---|---|
| FastAPI | Public GraphRAG API |
| Nginx | Reverse proxy and HTTPS |
| Qdrant | Vector database |
| Neo4j | Knowledge graph |
| Ollama | Local LLM inference |
| Qwen 2.5 7B | Generation and extraction |
| Docker Compose | Service orchestration |
| Persistent volumes | Database/model persistence |

---

# Docker Compose Deployment

A production-oriented deployment can use Docker Compose to run the infrastructure together.

Example structure:

```text
Graph_RAG/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── app/
├── data/
└── README.md
```

A typical Compose architecture is:

```text
Docker Network
│
├── graphrag-api
│
├── qdrant
│
├── neo4j
│
└── ollama
```

### Example `docker-compose.yml`

```yaml
services:

  qdrant:
    image: qdrant/qdrant
    restart: unless-stopped
    volumes:
      - qdrant_data:/qdrant/storage

  neo4j:
    image: neo4j:latest
    restart: unless-stopped
    environment:
      NEO4J_AUTH: neo4j/change-this-password
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

  ollama:
    image: ollama/ollama
    restart: unless-stopped
    volumes:
      - ollama_data:/root/.ollama

  graphrag-api:
    build: .
    restart: unless-stopped
    depends_on:
      - qdrant
      - neo4j
      - ollama
    environment:
      QDRANT_HOST: qdrant
      QDRANT_PORT: 6333
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USERNAME: neo4j
      NEO4J_PASSWORD: change-this-password
      OLLAMA_HOST: http://ollama:11434
    ports:
      - "8000:8000"

volumes:
  qdrant_data:
  neo4j_data:
  neo4j_logs:
  ollama_data:
```

> This Compose example describes the target deployment architecture. The current repository still needs a production `Dockerfile` and FastAPI application before this exact deployment can be used as-is.

---

# Environment Variables

Production deployments should not hard-code credentials.

Create:

```text
.env
```

from:

```text
.env.example
```

Example:

```env
QDRANT_HOST=qdrant
QDRANT_PORT=6333

NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=change-this-password

OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=qwen2.5:7b
```

Never commit real passwords or API keys to Git.

Add `.env` to `.gitignore`:

```text
.env
```

---

# API Deployment

For external users, GraphRAG should be exposed through a REST API rather than allowing users to execute the Python application directly.

A future API can expose an endpoint such as:

```http
POST /query
```

Request:

```json
{
  "query": "How does SelfExtend improve long-context performance?"
}
```

Response:

```json
{
  "answer": "SelfExtend improves long-context performance...",
  "citations": [
    {
      "document": "2401.01325v3",
      "page": 7
    },
    {
      "document": "2401.01325v3",
      "page": 8
    }
  ]
}
```

The API should internally execute:

```text
HTTP Request
     |
     v
FastAPI
     |
     v
GraphRAG.ask()
     |
     +--> Query Entity Extraction
     |
     +--> Vector Retrieval
     |
     +--> Graph Retrieval
     |
     +--> Hybrid Reranking
     |
     +--> Evidence Processing
     |
     +--> Context Building
     |
     +--> Qwen Generation
     |
     v
Grounded JSON Response
```

---

# Example API Usage

Once the API is running:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does SelfExtend improve long-context performance?"
  }'
```

A client application can then consume the response and display:

```text
Answer
------
SelfExtend improves long-context performance...

Sources
-------
2401.01325v3 — page 7
2401.01325v3 — page 8
```

---

# Production Security

Before exposing the API publicly, add:

### 1. Authentication

Require users to authenticate before accessing `/query`.

Possible approaches include:

- API keys
- JWT
- OAuth/OIDC

### 2. HTTPS

Put the API behind a reverse proxy and use TLS.

```text
HTTPS
  |
  v
Nginx
  |
  v
FastAPI
```

### 3. Rate Limiting

Protect the LLM endpoint from excessive requests.

For example:

```text
User
  |
  v
Rate Limiter
  |
  v
GraphRAG API
```

### 4. Input Validation

Validate:

- query length
- malformed requests
- unexpected fields
- maximum concurrent requests

### 5. Network Isolation

Do not publicly expose:

```text
Qdrant :6333
Neo4j  :7474 / 7687
Ollama :11434
```

These services should be accessible only inside the private application network.

---

# GPU Deployment

Qwen 2.5 7B inference can benefit substantially from GPU acceleration.

A server deployment should therefore consider:

```text
                 GPU Server
                     |
              ┌──────┴──────┐
              │   Ollama    │
              │             │
              │ Qwen 2.5 7B │
              └─────────────┘
```

The required GPU resources depend on:

- model size
- quantization
- context length
- number of concurrent users
- requested generation length

For multiple simultaneous users, model serving and concurrency should be benchmarked before selecting the final hardware.

---

# Scaling the System

For a small deployment:

```text
1 API
1 Qdrant
1 Neo4j
1 Ollama
```

For a larger deployment:

```text
                 Load Balancer
                       |
             ┌─────────┼─────────┐
             ▼         ▼         ▼
           API-1     API-2     API-3
             |         |         |
             └─────────┼─────────┘
                       |
              ┌────────┴────────┐
              ▼                 ▼
           Qdrant             Neo4j
              |
              |
          LLM Serving
              |
        ┌─────┴─────┐
        ▼           ▼
      GPU-1       GPU-2
      Ollama      Ollama
```

The API layer can be scaled horizontally, while database and model-serving strategies should be chosen based on workload.

---

# Deployment Workflow

A complete deployment workflow should eventually look like:

```text
1. Clone repository
        |
        v
2. Configure .env
        |
        v
3. Start Docker Compose
        |
        v
4. Start Qdrant
        |
        v
5. Start Neo4j
        |
        v
6. Start Ollama
        |
        v
7. Pull Qwen model
        |
        v
8. Ingest research papers
        |
        v
9. Build vectors + graph
        |
        v
10. Start FastAPI
        |
        v
11. Put Nginx/HTTPS in front
        |
        v
12. Users query GraphRAG
```

---

# Ingesting New Documents

A deployed instance can be populated with additional research papers.

The intended workflow is:

```text
New PDF
   |
   v
PDF Loader
   |
   v
Chunker
   |
   +------------------+
   |                  |
   v                  v
Embedding          Graph Extraction
   |                  |
   v                  v
Qdrant              Neo4j
   |                  |
   +--------+---------+
            |
            v
       Searchable
       Knowledge Base
```

This means users do not need to manually create embeddings or graph relationships.

---

# Persistent Storage

Production deployments must use persistent storage.

Recommended volumes:

```text
Qdrant
  └── qdrant_data

Neo4j
  ├── neo4j_data
  └── neo4j_logs

Ollama
  └── ollama_data
```

Without persistent volumes, containers can lose their stored data when recreated.

---

# Deployment Status

### Currently implemented

```text
[x] Local Qdrant
[x] Local Neo4j
[x] Local Ollama
[x] Local Qwen inference
[x] PDF ingestion
[x] Vector indexing
[x] Graph indexing
[x] Hybrid retrieval
[x] Grounded generation
```

### Deployment components still to implement

```text
[ ] FastAPI production API
[ ] Production Dockerfile
[ ] Complete Docker Compose deployment
[ ] Persistent production configuration
[ ] Authentication
[ ] Rate limiting
[ ] Nginx configuration
[ ] HTTPS
[ ] Production monitoring
[ ] Multi-user concurrency testing
```

Therefore, the current project is **fully functional as a local GraphRAG application**, while the public/server deployment layer is the next engineering stage.

# Running the Project

## Prerequisites

Install:

- Python 3
- Docker
- Ollama

The Python environment is:

```text
.venv/
```

Activate it:

```bash
source .venv/bin/activate
```

---

# Start Qdrant

Example Docker command:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Qdrant will be available at:

```text
http://localhost:6333
```

---

# Start Neo4j

Example:

```bash
docker run \
  --name neo4j-graphrag \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Neo4j Browser:

```text
http://localhost:7474
```

Bolt connection:

```text
bolt://localhost:7687
```

Credentials used by the prototype:

```text
Username: neo4j
Password: password
```

For production, use a secure password and persistent volumes.

---

# Start Ollama

Verify Ollama:

```bash
ollama --version
```

Verify the model:

```bash
ollama list
```

The project currently uses:

```text
qwen2.5:7b
```

If it is not installed:

```bash
ollama pull qwen2.5:7b
```

Test it:

```bash
ollama run qwen2.5:7b
```

---

# Run Tests

The project contains unit and integration tests.

For example:

```bash
python -m test.test_pdf
```

```bash
python -m test.test_chunker
```

```bash
python -m test.test_embeddings
```

```bash
python -m test.test_qdrant
```

```bash
python -m test.test_neo4j
```

```bash
python -m test.test_graph_retriever
```

```bash
python -m test.test_hybrid_reranker
```

---

# End-to-End Test

Run:

```bash
python -m test.test_graphrag
```

The test executes:

```text
Query
  ↓
Entity Extraction
  ↓
Vector Retrieval
  ↓
Graph Retrieval
  ↓
Hybrid Reranking
  ↓
Evidence Processing
  ↓
Context Construction
  ↓
Qwen Generation
  ↓
Grounded Answer
```

---

# Current Results

For:

```text
How does SelfExtend improve long-context performance?
```

the system currently retrieves both structured and textual evidence.

Example processed evidence:

```text
GRAPH
SelfExtend -- IMPROVES --> Long-Context Performance

GRAPH
SelfExtend -- EVALUATES --> Perplexity
    -- CAPTURES --> Long-Context Performance

VECTOR
2401.01325v3, page 8

VECTOR
2401.01325v3, page 6

VECTOR
2401.01325v3, page 7
```

The generated answer successfully uses page-level citations such as:

```text
[2401.01325v3, p.7]
[2401.01325v3, p.8]
[2401.01325v3, p.6]
```

---

# Design Principles

## Grounding First

The LLM should not be responsible for finding facts.

Instead:

```text
Retrieval → Evidence → Generation
```

The generator should synthesize retrieved evidence.

---

## Vector + Graph Complementarity

Vector retrieval answers:

> "What text is relevant?"

Graph retrieval answers:

> "How are the concepts connected?"

Together:

```text
Semantic Search + Structured Relationships
```

---

## Separation of Responsibilities

Each component has one primary responsibility:

```text
PDF Loader
    ↓
Chunker
    ↓
Embedder
    ↓
Qdrant

PDF
    ↓
Graph Extractor
    ↓
Neo4j

Query
    ↓
Entity Extractor
    ↓
Vector + Graph Retrieval
    ↓
Reranker
    ↓
Evidence Processor
    ↓
Context Builder
    ↓
Generator
```

This makes the system easier to test and evolve.

---

# Known Limitations

The prototype is functional, but several areas still need improvement.

## 1. Entity Duplication

The current graph contains semantically equivalent entities such as:

```text
LLM
LLMs
Large Language Model
Large Language Models
```

and:

```text
Long Context Performance
Long-Context Performance
```

These should eventually be resolved into canonical entities.

---

## 2. Graph Noise

Some automatically extracted relationships are weak or overly generic.

For example, generic concepts such as:

```text
LLMs
Models
Performance
Tasks
```

can become highly connected graph hubs.

The graph retrieval layer currently applies penalties to reduce their influence.

---

## 3. Graph Extraction Errors

The local 7B model occasionally produces malformed JSON during large-scale extraction.

The ingestion pipeline currently handles extraction failures without stopping the complete ingestion process.

---

## 4. Citation Granularity

The system now supports claim-level citations, but citation quality can still be improved with:

- sentence-to-evidence mapping
- citation verification
- citation confidence
- answer evaluation

---

## 5. Persistence

The current Qdrant prototype was initially launched without a persistent Docker volume.

For production use, persistent storage should be configured.

---

# Roadmap

Planned improvements:

```text
[x] PDF ingestion
[x] Token-aware chunking
[x] BGE embeddings
[x] Qdrant vector search
[x] Neo4j graph construction
[x] Graph retrieval
[x] Query entity extraction
[x] Hybrid retrieval
[x] Hybrid reranking
[x] Evidence processing
[x] Grounded generation
[x] Claim-level citations
[ ] Entity resolution
[ ] Canonical entity mapping
[ ] Graph deduplication
[ ] Better graph extraction validation
[ ] Citation verification
[ ] Retrieval evaluation
[ ] RAG evaluation metrics
[ ] Query decomposition
[ ] Multi-hop reasoning
[ ] Persistent Docker volumes
[ ] Production API
[ ] Web UI
```

---

# Future Production Architecture

A future production version could evolve toward:

```text
                         ┌─────────────────┐
                         │    Web / API    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Query Analyzer  │
                         └────────┬────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
          ┌───────────────┐               ┌───────────────┐
          │    Qdrant     │               │     Neo4j     │
          │ Vector Search │               │ Graph Search  │
          └───────┬───────┘               └───────┬───────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  ▼
                         ┌─────────────────┐
                         │ Hybrid Reranker │
                         └────────┬────────┘
                                  ▼
                         ┌─────────────────┐
                         │    Evidence     │
                         │    Processor    │
                         └────────┬────────┘
                                  ▼
                         ┌─────────────────┐
                         │ Context Builder │
                         └────────┬────────┘
                                  ▼
                         ┌─────────────────┐
                         │   Local / API   │
                         │       LLM       │
                         └────────┬────────┘
                                  ▼
                         ┌─────────────────┐
                         │ Grounded Answer │
                         │ + Citations     │
                         └─────────────────┘
```

---

# Project Goal

The goal of this project is to build a **fully understandable, modular GraphRAG system from first principles**, rather than relying on a black-box RAG framework.

The project demonstrates how:

```text
Documents
   ↓
Chunks
   ↓
Embeddings + Knowledge Graph
   ↓
Hybrid Retrieval
   ↓
Evidence Selection
   ↓
Grounded Generation
```

can be assembled into a practical research assistant using locally hosted infrastructure.

---

## License

Add the project's intended license here before publishing it publicly.
