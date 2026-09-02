from app.graph_builder.pipeline import GraphBuilder


chunk = {
    "chunk_id": "test_chunk_001",
    "document_id": "test_document",
    "page": 1,
    "text": """
    SelfExtend extends the context window of pretrained
    large language models without fine-tuning.

    It constructs bi-level attention information consisting
    of grouped attention and neighbor attention.

    Grouped attention captures dependencies among tokens
    that are far apart, while neighbor attention captures
    dependencies among adjacent tokens.
    """
}


builder = GraphBuilder(
    model="qwen2.5:7b"
)


result = builder.process_chunk(
    chunk
)


print("\nExtracted:")
print(result)


builder.close()
