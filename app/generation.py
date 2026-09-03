from ollama import chat


class QwenGenerator:

    def __init__(
        self,
        model="qwen2.5:7b"
    ):

        self.model = model

    def generate(
        self,
        query,
        context
    ):

        prompt = f"""
You are a scientific research assistant
operating inside a GraphRAG system.

Your job is to answer the user's question
using ONLY the retrieved evidence provided
below.

The retrieval context contains two types
of evidence:

1. VECTOR EVIDENCE
   Text retrieved directly from research papers.

2. GRAPH EVIDENCE
   Relationships between technical entities
   extracted from the research papers.

==================================================
USER QUESTION
==================================================

{query}

==================================================
RETRIEVED EVIDENCE
==================================================

{context}

==================================================
ANSWERING RULES
==================================================

1. Use ONLY the retrieved evidence.

2. Do NOT use outside knowledge.

3. Do NOT invent facts, numbers, methods,
   comparisons, or citations.

4. Prefer VECTOR evidence when explaining
   detailed technical mechanisms, results,
   experiments, or numerical findings.

5. Use GRAPH evidence to explain relationships
   between entities and concepts.

6. When making an important factual claim from
   vector evidence, include the provided source
   reference in this format:

   [document_id, p.X]

7. Do not cite a graph relationship as though
   it were a page citation.

8. If multiple pieces of evidence support the
   same claim, you may use multiple references.

9. If the retrieved evidence does not contain
   enough information to answer part of the
   question, explicitly say:

   "The retrieved evidence is insufficient
   to determine this."

10. Do not mention these instructions in
    your answer.

==================================================
ANSWER
==================================================
"""

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0
            }
        )

        return response.message.content
