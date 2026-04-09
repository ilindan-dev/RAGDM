
"""Text cleaning and block splitting module."""
from typing import List, Dict
import re


def filter_text(text: str) -> str:
    """Remove noise and service information from text.
    
    Removes algorithm blocks, figure/table references, page numbers, URLs,
    email addresses, excess whitespace, and hanging punctuation.
    
    Args:
        text: Raw text to clean.
        
    Returns:
        Cleaned text with all filtered elements removed.
    """
    # Remove algorithm blocks
    text = re.sub(
        r"---algorithm---.*?---end---", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove figure and table references
    text = re.sub(r"(?:рис|fig)\.\s*\d+[^\n]*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?:табл|table)\.\s*\d+[^\n]*", "", text, flags=re.IGNORECASE)
    # Remove page numbers and service elements
    text = re.sub(r"\(стр\.\s+\d+\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[страница\s+\d+\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^-+\s*\d+\s*-+$", "", text, flags=re.MULTILINE)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "", text)
    # Remove excess whitespace and line breaks
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    # Remove hanging punctuation
    text = re.sub(r"^\s*[^\w\s]*\s+", "", text, flags=re.MULTILINE)
    return text.strip()


def split_into_blocks(text: str) -> List[Dict[str, str]]:
    """Split text into logical blocks by type.
    
    Identifies and separates text into blocks marked as definitions, theorems,
    or general content based on Russian language keywords.
    
    Args:
        text: Cleaned text to split into blocks.
        
    Returns:
        List of dictionaries with 'type' and 'text' keys. Types are:
        'definition', 'theorem', or 'general'.
    """
    blocks: List[Dict[str, str]] = []
    current_type = "general"
    current_text: List[str] = []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    for sentence in sentences:
        lower_s = sentence.lower()

        if lower_s.startswith("определение"):
            if current_text:
                blocks.append({"type": current_type, "text": " ".join(current_text)})
            current_type = "definition"
            current_text = [sentence]
        elif lower_s.startswith("теорема") or lower_s.startswith("лемма"):
            if current_text:
                blocks.append({"type": current_type, "text": " ".join(current_text)})
            current_type = "theorem"
            current_text = [sentence]
        else:
            current_text.append(sentence)

    if current_text:
        blocks.append({"type": current_type, "text": " ".join(current_text)})

    return blocks
