from app.graph_builder.extractor import EntityRelationshipExtractor


extractor = EntityRelationshipExtractor(
    model="qwen2.5:7b"
)


text = """
SelfExtend extends the context window of pretrained
large language models without fine-tuning.

It constructs bi-level attention information consisting
of grouped attention and neighbor attention.

Grouped attention captures dependencies among tokens
that are far apart, while neighbor attention captures
dependencies among adjacent tokens.
"""


result = extractor.extract(text)


print("\nENTITIES")
print("=" * 50)

for entity in result["entities"]:
    print("-", entity)


print("\nRELATIONSHIPS")
print("=" * 50)

for relationship in result["relationships"]:
    print(
        relationship["source"],
        "--",
        relationship["relationship"],
        "-->",
        relationship["target"]
    )