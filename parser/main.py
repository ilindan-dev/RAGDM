"""Entry point for RAG document processing pipeline."""

from pathlib import Path
from typing import Generator, Dict, Any
from sentence_transformers import SentenceTransformer
from parser import prepare_text_for_rag
from generators import generate_sql


def main() -> None:
    """Initialize model and execute RAG pipeline on all PDF files in data directory."""
    print(
        "Initializing model "
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2..."
    )
    # Cache models locally in /parser/models/
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    try:
        model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            cache_folder=str(models_dir),
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print(
            f"Data directory {data_dir} not found. "
            "Creating empty directory (add PDF files to it)."
        )
        data_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {data_dir}.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")

    def all_pdfs_generator() -> Generator[Dict[str, Any], None, None]:
        """Generate processed data from all PDF files."""
        for pdf_path in pdf_files:
            print(f"Processing document: {pdf_path.name}")
            # Extract chapter name from filename
            chapter_name = pdf_path.stem
            yield from prepare_text_for_rag(pdf_path, model, chapter_name=chapter_name)

    output_sql = Path(__file__).parent / "init.sql"
    generate_sql(all_pdfs_generator(), output_file=str(output_sql))


if __name__ == "__main__":
    main()
