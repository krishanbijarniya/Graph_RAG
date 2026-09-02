from app.vector_store.indexer import build_chunks
from app.graph_builder.pipeline import GraphBuilder


def main():

    print("=" * 70)
    print("BUILDING CHUNKS")
    print("=" * 70)

    chunks = build_chunks()

    total = len(chunks)

    print(
        f"Total chunks: {total}"
    )

    print("\n")
    print("=" * 70)
    print("STARTING GRAPH INGESTION")
    print("=" * 70)

    builder = GraphBuilder(
        model="qwen2.5:7b"
    )

    successful = 0
    failed = 0

    total_entities = 0
    total_relationships = 0

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print("\n" + "-" * 70)

        print(
            f"[{index}/{total}] "
            f"{chunk['chunk_id']}"
        )

        try:

            result = builder.process_chunk(
                chunk
            )

            entities = result.get(
                "entities",
                []
            )

            relationships = result.get(
                "relationships",
                []
            )

            successful += 1

            total_entities += len(
                entities
            )

            total_relationships += len(
                relationships
            )

            print(
                f"Entities: "
                f"{len(entities)}"
            )

            print(
                f"Relationships: "
                f"{len(relationships)}"
            )

        except Exception as e:

            failed += 1

            print(
                f"ERROR: {chunk['chunk_id']}"
            )

            print(
                f"Reason: {e}"
            )

            continue

    builder.close()

    print("\n")
    print("=" * 70)
    print("GRAPH INGESTION COMPLETE")
    print("=" * 70)

    print(
        f"Total chunks        : {total}"
    )

    print(
        f"Successful chunks   : {successful}"
    )

    print(
        f"Failed chunks       : {failed}"
    )

    print(
        f"Extracted entities  : {total_entities}"
    )

    print(
        f"Relationships        : {total_relationships}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()