import json
from ollama import chat


class QueryEntityExtractor:

    def __init__(self, model="qwen2.5:7b"):
        self.model = model

    def extract(self, query):

        prompt = f"""
You are a query analyzer for a scientific GraphRAG system.

Extract the important technical entities from the user question.

Only extract entities that are useful for searching a
scientific knowledge graph.

Examples:

Question:
How does SelfExtend improve long-context performance?

Entities:
["SelfExtend", "Long-Context Performance"]

Question:
What attention mechanism does SelfExtend use?

Entities:
["SelfExtend", "Attention"]

Question:
How does fine-tuning affect context windows?

Entities:
["Fine-tuning", "Context Window"]

Rules:

- Return only important technical entities.
- Do not extract generic words such as "how", "does", "what".
- Do not create entities that are not supported by the question.
- Keep entity names short.
- Preserve technical names such as SelfExtend, GPT-4, Mistral, etc.
- Return valid JSON only.

Output format:

{{
    "entities": [
        "Entity 1",
        "Entity 2"
    ]
}}

Question:

{query}
"""

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0
            }
        )

        result = json.loads(
            response.message.content
        )

        return result["entities"]
