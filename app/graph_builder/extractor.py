import json

from ollama import chat


class EntityRelationshipExtractor:

    def __init__(
        self,
        model="qwen2.5:7b"
    ):
        self.model = model

    def extract(self, text):

        prompt = f"""
You are a precise knowledge graph extractor for scientific
and AI research papers.

Your job is to extract:

1. Important technical entities
2. ONLY factual relationships explicitly stated in the text

Do NOT guess.
Do NOT infer.
Do NOT invent relationships.

The graph will be used for GraphRAG, so precision is more
important than extracting many relationships.

==================================================
ENTITY RULES
==================================================

Extract important technical entities such as:

- AI models
- LLMs
- algorithms
- methods
- architectures
- techniques
- datasets
- benchmarks
- systems
- important technical concepts

Entity names must be:

- short
- canonical
- technically meaningful

Examples:

"selfextend"
-> "SelfExtend"

"context window"
-> "Context Window"

"pretrained large language models"
-> "Pretrained Language Models"

"grouped attention"
-> "Grouped Attention"

"neighbor attention"
-> "Neighbor Attention"

"long-range dependencies"
-> "Long-Range Dependencies"

DO NOT extract:

- authors
- universities
- email addresses
- citations
- references
- generic words
- complete sentences
- long explanations
- descriptions
- vague phrases

==================================================
IMPORTANT: TOPICS ARE NOT AUTOMATIC RELATIONSHIPS
==================================================

A list of topics does NOT mean that the main entity
has a relationship with every topic.

For example:

"The review covers architectural innovations,
training strategies, context length improvements,
fine-tuning, robotics, datasets and benchmarking."

DO NOT produce:

LLMs -- EXTENDS --> Architectural Innovations
LLMs -- EXTENDS --> Robotics
LLMs -- EXTENDS --> Datasets

Those relationships are NOT explicitly stated.

If the text only says that a paper discusses several topics,
do NOT invent relationships between the entities.

When appropriate, the relationship may instead be:

Document/Paper -- RELATED_TO --> Topic

BUT only if Document/Paper is explicitly represented as
an entity.

Otherwise, simply extract the entities and no relationships.

==================================================
RELATIONSHIP RULES
==================================================

A relationship must represent an explicit factual statement.

Use ONLY:

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

==================================================
RELATIONSHIP SEMANTICS
==================================================

EXTENDS

Use ONLY when the text explicitly says that one method,
model, or technique extends another concept.

Example:

"SelfExtend extends the context window."

Correct:

SelfExtend -- EXTENDS --> Context Window

Do NOT use EXTENDS to mean:

- discusses
- relates to
- works with
- is about
- includes in a list

--------------------------------------------------

USES

Use when the text explicitly says that a method or system
uses another method, model, technique, or component.

Example:

"Method A uses grouped attention."

Correct:

Method A -- USES --> Grouped Attention

--------------------------------------------------

IMPROVES

Use when the text explicitly states that something improves
another concept.

Example:

"Method A improves long-context performance."

Correct:

Method A -- IMPROVES --> Long-Context Performance

--------------------------------------------------

PROPOSES

Use when a paper or method explicitly proposes a technique.

Example:

"The authors propose SelfExtend."

Correct:

Paper -- PROPOSES --> SelfExtend

--------------------------------------------------

CONTAINS

Use when one technical component explicitly contains another.

Example:

"Bi-level attention consists of grouped attention and
neighbor attention."

Correct:

Bi-Level Attention -- CONTAINS --> Grouped Attention

Bi-Level Attention -- CONTAINS --> Neighbor Attention

--------------------------------------------------

CAPTURES

Use when the text explicitly says that a method/component
captures a dependency, representation, or information.

Example:

"Grouped attention captures long-range dependencies."

Correct:

Grouped Attention -- CAPTURES --> Long-Range Dependencies

--------------------------------------------------

BASED_ON

Use when the text explicitly says that one method is based
on another model, method, or concept.

--------------------------------------------------

TRAINS

Use when the text explicitly describes training.

--------------------------------------------------

EVALUATES

Use when one entity explicitly evaluates another.

--------------------------------------------------

COMPARES_WITH

Use only when an explicit comparison is made.

--------------------------------------------------

AVOIDS

Use when the text explicitly says that something avoids,
does not require, or works without another technique.

Example:

"SelfExtend works without fine-tuning."

Correct:

SelfExtend -- AVOIDS --> Fine-tuning

Incorrect:

SelfExtend -- USES --> Fine-tuning

--------------------------------------------------

RELATED_TO

Use only when the text explicitly establishes a meaningful
relationship but none of the more specific relationships
apply.

==================================================
NEGATION
==================================================

Pay extremely close attention to negation.

Example:

"SelfExtend does not require fine-tuning."

DO NOT produce:

SelfExtend -- USES --> Fine-tuning

Possible:

SelfExtend -- AVOIDS --> Fine-tuning

Example:

"Method A is not based on Method B."

DO NOT produce:

Method A -- BASED_ON --> Method B

Instead, omit the relationship.

==================================================
SOURCE AND TARGET RULE
==================================================

Every relationship must satisfy:

source ∈ entities

AND

target ∈ entities

Never use a description as a relationship target.

Bad:

Grouped Attention
-- CAPTURES -->
"dependencies among tokens that are far apart"

Good:

Grouped Attention
-- CAPTURES -->
Long-Range Dependencies

If the target is not important enough to be an entity,
DO NOT create the relationship.

==================================================
NO RELATIONSHIP INFERENCE
==================================================

Do not assume relationships from:

- entity proximity
- lists
- sentence structure alone
- common knowledge
- domain knowledge
- titles
- citations
- references

Only extract what the text explicitly supports.

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Use exactly this schema:

{{
    "entities": [
        "Entity 1",
        "Entity 2"
    ],
    "relationships": [
        {{
            "source": "Entity 1",
            "relationship": "USES",
            "target": "Entity 2"
        }}
    ]
}}

If there are no valid relationships:

{{
    "entities": [
        "Entity 1",
        "Entity 2"
    ],
    "relationships": []
}}

==================================================
TEXT
==================================================

{text}
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

        return result