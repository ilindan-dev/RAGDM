"""Keyword extraction using YAKE algorithm."""
from typing import List, Tuple, Set
import string
import yake

# Russian stop words for filtering
RU_STOP_WORDS: Set[str] = {
    'что', 'это', 'как', 'за', 'из', 'на', 'при', 'в', 'с', 'по', 'к', 'до',
    'и', 'или', 'но', 'а', 'не', 'ни', 'да', 'нет', 'если', 'то',
    'для', 'от', 'об', 'о', 'без', 'через', 'между', 'перед', 'после',
    'выше', 'ниже', 'раньше', 'позже', 'всегда', 'никогда', 'часто', 'редко',
    'который', 'какой', 'какая', 'какое', 'кто', 'где', 'когда', 'почему', 'зачем',
    'я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они', 'ме', 'те', 'же', 'ее', 'его',
    'более', 'менее', 'очень', 'же', 'же',
}


def extract_keywords(text: str, top_n: int = 20) -> List[Tuple[str, str]]:
    """Extract and filter keywords/terms from text.
    
    Uses YAKE algorithm to identify single and two-word terms, then filters
    based on Russian stop words, minimum length, and stop word ratio.
    Original word forms are preserved while normalized versions are used for
    embedding generation.
    
    Args:
        text: Input text to extract keywords from.
        top_n: Maximum number of keywords to return. Defaults to 20.
        
    Returns:
        List of tuples (original_word, normalized_word) for each extracted keyword.
        Normalized words are lowercase for consistent embedding generation.
    """
    if not text.strip():
        return []
    
    # Extract single and two-word terms using YAKE
    try:
        kw_extractor = yake.KeywordExtractor(
            lan="ru", n=2, dedupLim=0.9, top=top_n*2, features=None
        )
        keywords_raw = kw_extractor.extract_keywords(text)
    except Exception:
        return []
    
    filtered_keywords: List[Tuple[str, str]] = []
    seen_normalized: Set[str] = set()
    
    for kw, score in keywords_raw:
        kw_original = kw.strip()  # Preserve original word form
        kw_normalized = kw_original.lower()  # Normalize for filtering
        
        # Skip if empty or exact match to stop word
        if not kw_normalized or kw_normalized in RU_STOP_WORDS:
            continue
        
        # Check minimum length (at least 2 characters)
        if len(kw_normalized) < 2:
            continue
        
        # Remove words containing only punctuation or digits
        if all(c in string.punctuation + string.digits for c in kw_normalized):
            continue
        
        # Remove single-word terms that are stop words
        words = kw_normalized.split()
        if all(w in RU_STOP_WORDS for w in words):
            continue
        
        # Remove phrases where more than half are stop words
        stop_word_ratio = sum(1 for w in words if w in RU_STOP_WORDS) / len(words)
        if stop_word_ratio > 0.5:
            continue
        
        # Remove duplicates by normalized form
        if kw_normalized not in seen_normalized:
            filtered_keywords.append((kw_original, kw_normalized))
            seen_normalized.add(kw_normalized)
            
            if len(filtered_keywords) >= top_n:
                break
    
    return filtered_keywords
