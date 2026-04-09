"""
Main parser module orchestrating the RAG pipeline.
Combines PDF extraction, NLP processing, and SQL data generation.
"""
from typing import Generator, Dict, Any, Optional, List
from extractors import parse_hall_text
from nlp import filter_text, split_into_blocks, extract_keywords
from generators import generate_sql


def prepare_text_for_rag(
    pdf_path: str,
    model: Any,
    chapter_name: str = "unknown",
    start_page: int = 1,
    end_page: Optional[int] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Complete RAG pipeline: extraction → cleaning → blocking → embeddings.
    
    Processes PDF document through complete pipeline including text extraction,
    cleaning, block identification, keyword extraction, and embedding generation
    for both individual terms and full text blocks.
    
    Args:
        pdf_path: Path to the PDF file.
        model: Sentence Transformer model for encoding text and terms.
        chapter_name: Identifier for the chapter/document. Defaults to 'unknown'.
        start_page: Starting page number (1-indexed). Defaults to 1.
        end_page: Ending page number (inclusive). If None, processes all pages.
        
    Yields:
        Dictionary with keys:
        - chapter_name (str): Document identifier.
        - terms (List[str]): Original term forms from text.
        - definitions (List[str]): Context/definition text for each term.
        - chunk_text (str): Full text block.
        - terms_embeddings (List[List[float]]): Embeddings of normalized terms.
        - chunk_embedding (List[float]): Embedding of full chunk.
    """
    chunks = parse_hall_text(pdf_path, start_page, end_page)

    for chunk in chunks:
        cleaned = filter_text(chunk["text"])
        if not cleaned.strip():
            continue

        blocks = split_into_blocks(cleaned)

        for block in blocks:
            block_text = block["text"]
            if not block_text.strip():
                continue

            # Extract keywords (original and normalized forms)
            keyword_pairs = extract_keywords(block_text)
            
            # Separate original and normalized terms
            terms_original: List[str] = [orig for orig, norm in keyword_pairs]
            terms_normalized: List[str] = [norm for orig, norm in keyword_pairs]
            
            # Generate embeddings for each normalized term
            terms_embeddings: List[List[float]] = []
            for norm_term in terms_normalized:
                term_embedding = model.encode(norm_term).tolist()
                terms_embeddings.append(term_embedding)
            
            # Generate embedding for entire chunk
            chunk_embedding: List[float] = model.encode(block_text).tolist()
            
            # Use full block text as definition context for each term
            definitions: List[str] = [block_text] * len(terms_original)

            yield {
                "chapter_name": chapter_name,
                "terms": terms_original,
                "definitions": definitions,
                "chunk_text": block_text,
                "terms_embeddings": terms_embeddings,
                "chunk_embedding": chunk_embedding,
            }


__all__ = ["prepare_text_for_rag", "generate_sql"]
