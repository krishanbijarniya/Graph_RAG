from pathlib import Path


def create_structure() -> None:
    directories = [
        Path("data/papers"),
        Path("app/ingestion"),
        Path("app/embeddings"),
        Path("app/vector_store"),
        Path("app/retrieval"),
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    files_to_create = [
        Path("app/__init__.py"),
        Path("app/ingestion/__init__.py"),
        Path("app/embeddings/__init__.py"),
        Path("app/vector_store/__init__.py"),
        Path("app/retrieval/__init__.py"),
        Path("data/papers/.gitkeep"),
    ]

    for file_path in files_to_create:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            file_path.touch()


if __name__ == "__main__":
    create_structure()
    print("Project structure created successfully.")
