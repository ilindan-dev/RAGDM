from pathlib import Path
from sentence_transformers import SentenceTransformer
from pdf_extractor import extract_text_from_pdf
from parser import parse_theorems_and_terms
from sql_generator import generate_seed_sql

def main():
    print("Инициализация модели sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2...")
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        cache_folder=str(models_dir),
    )

    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print(f"Директория {data_dir} не найдена.")
        return

    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"PDF файлы не найдены в {data_dir}.")
        return

    all_cards = []
    
    for pdf_path in pdf_files:
        print(f"\nОбработка документа: {pdf_path.name}")
        chapter_name = pdf_path.stem
        
        # 1. Извлекаем чистый текст без колонтитулов
        text = extract_text_from_pdf(pdf_path)
        
        # 2. Выделяем карточки (Теоремы и Термины)
        cards = parse_theorems_and_terms(text, chapter_name, model)
        all_cards.extend(cards)

    # 3. Генерируем SQL seed-файл (БЕЗ DDL, только INSERT)
    output_sql = Path(__file__).parent / "seed_cards.sql"
    generate_seed_sql(all_cards, str(output_sql))

if __name__ == "__main__":
    main()
