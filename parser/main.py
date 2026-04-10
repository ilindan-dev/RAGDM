from pathlib import Path
from sentence_transformers import SentenceTransformer

# Импортируем из наших модулей
from parser import process_pdf_to_cards
from generators.sql_generator import generate_seed_sql

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
        print(f"Директория {data_dir} не найдена. Создаю пустую папку.")
        data_dir.mkdir(parents=True, exist_ok=True)
        return

    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"PDF файлы не найдены в {data_dir}.")
        return

    all_cards = []
    
    for pdf_path in pdf_files:
        print(f"\nНачинаю обработку документа: {pdf_path.name}")
        chapter_name = pdf_path.stem
        
        cards = process_pdf_to_cards(pdf_path, model, chapter_name)
        all_cards.extend(cards)

    # Сохраняем в SQL
    output_sql = Path(__file__).parent / "seed_cards.sql"
    generate_seed_sql(all_cards, str(output_sql))

if __name__ == "__main__":
    main()
