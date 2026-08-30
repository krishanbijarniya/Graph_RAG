from pathlib import Path

from app.ingestion.pdf_loader import extract_text


PDF_DIR = Path("data/papers")


for pdf_path in PDF_DIR.glob("*.pdf"):
    print("\n" + "=" * 80)
    print(f"FILE: {pdf_path.name}")
    print("=" * 80)

    pages = extract_text(pdf_path)

    print(f"Total pages: {len(pages)}")

    for page in pages[:1]:
        print(f"\nPAGE {page['page']}")
        print(page["text"][:1000])