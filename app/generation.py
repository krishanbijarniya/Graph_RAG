import os

from ollama import Client


class QwenGenerator:

    def __init__(
        self,
        model=None
    ):

        self.host = os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434"
        )

        self.model = model or os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5:7b"
        )

        self.client = Client(
            host=self.host
        )

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

4. Synthesize the evidence into a coherent
   technical answer. Do not simply list or
   repeat the retrieved evidence.

5. Prefer VECTOR evidence for factual claims,
   including:

   - technical mechanisms
   - experimental findings
   - performance improvements
   - numerical results
   - model behavior
   - implementation details
   - datasets
   - comparisons

6. Use GRAPH evidence only when it adds useful
   information about relationships between
   technical concepts.

7. Do NOT mention every graph relationship.

   Only include a graph relationship if it
   materially helps answer the question.

8. Do NOT repeat the same fact using multiple
   evidence sources unless the sources provide
   complementary information.

9. CITATIONS MUST BE CLAIM-LEVEL.

   Put the citation immediately after the
   factual statement it supports.

   Example:

   SelfExtend operates during inference without
   additional training [2401.01325v3, p.6].

10. Use the exact document ID and page number
    provided by the VECTOR evidence.

11. Never invent citations.

12. GRAPH CITATIONS must use this format:

   [GRAPH RELATIONSHIP:
   SelfExtend -- IMPROVES --> Long-Context Performance]

13. Do not use graph citations when the same
    relationship is already adequately supported
    by vector evidence.

14. Prioritize the strongest and most relevant
    evidence rather than trying to use every
    retrieved result.

15. If numerical or experimental evidence is
    available, include the relevant result when
    it directly answers the question.

16. If the retrieved evidence is insufficient
    to determine something, explicitly say:

   "The retrieved evidence is insufficient
   to determine this."

17. Keep the answer concise but technically
    informative.

18. Do not mention these instructions in the
    answer.

==================================================
ANSWER
==================================================
"""

        response = self.client.chat(
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
