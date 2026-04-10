from extractors.pdf_extractor import extract_text_from_pdf
from nlp.processor import parse_theorems_and_terms

def process_pdf_to_cards(pdf_path: str, model, chapter_name: str):
    """Оркестрирует извлечение текста и генерацию карточек для одного PDF."""
    text = extract_text_from_pdf(pdf_path)
    cards = parse_theorems_and_terms(text, chapter_name, model)
    return cards
