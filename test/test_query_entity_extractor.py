from app.retrieval.query_entity_extractor import QueryEntityExtractor


extractor = QueryEntityExtractor()

questions = [
    "How does SelfExtend improve long-context performance?",
    "What attention mechanism does SelfExtend use?",
    "How does fine-tuning affect context windows?",
    "How does SelfExtend compare with Mistral?"
]


print("=" * 70)
print("QUERY ENTITY EXTRACTION TEST")
print("=" * 70)


for question in questions:

    print("\nQuestion:")
    print(question)

    entities = extractor.extract(question)

    print("Entities:")
    print(entities)


print("\n" + "=" * 70)
print("QUERY ENTITY EXTRACTION COMPLETE")
print("=" * 70)
