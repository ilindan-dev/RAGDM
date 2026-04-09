"""PDF text extraction module."""
from typing import Generator, Dict, Optional
import pdfplumber


def parse_hall_text(
    pdf_path: str, start_page: int = 1, end_page: Optional[int] = None
) -> Generator[Dict[str, object], None, None]:
    """Extract text from PDF using multiple fallback methods.
    
    Attempts to extract text from each page using pdfplumber. If initial extraction
    fails or produces insufficient text, falls back to adjusted tolerance settings
    and table extraction.
    
    Args:
        pdf_path: Path to the PDF file.
        start_page: Starting page number (1-indexed). Defaults to 1.
        end_page: Ending page number (inclusive). If None, processes all pages.
        
    Yields:
        Dictionary containing 'page' (int) and 'text' (str) keys.
        Only yields pages with extracted text length > 10 characters.
    """
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            if page_num < start_page:
                continue
            if end_page and page_num > end_page:
                break

            text = page.extract_text()

            if not text or len(text.strip()) < 10:
                try:
                    text = page.extract_text(x_tolerance=2, y_tolerance=2)
                except Exception:
                    pass

            if not text or len(text.strip()) < 10:
                tables = page.extract_tables()
                if tables:
                    text = "\n".join(
                        [
                            "\n".join([str(cell) for cell in row])
                            for table in tables
                            for row in table
                        ]
                    )

            if text and len(text.strip()) > 10:
                yield {
                    "page": page_num,
                    "text": text,
                }
            else:
                print(f"Warning: Page {page_num} - no text extracted")

            page.flush_cache()

            if page_num % 10 == 0:
                print(f"Processed {page_num} pages...")
