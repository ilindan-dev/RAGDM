from pathlib import Path
from sentence_transformers import SentenceTransformer
from parser import prepare_text_for_rag, generate_sql


def main():
    print(
        "⏳ Инициализация модели "
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2..."
    )
    # Сохраняем модель локально в /parser/models/, как сказано в ТЗ:
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    try:
        model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            cache_folder=str(models_dir),
        )
    except Exception as e:
        print(f"❌ Ошибка при загрузке модели: {e}")
        return

    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print(
            f"⚠️ Папка {data_dir} не найдена. "
            "Создаю пустую папку (положите в нее PDF-файлы)."
        )
        data_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"⚠️ В папке {data_dir} нет PDF файлов.")
        return

    print(f"🔍 Найдено {len(pdf_files)} PDF файлов для обработки.")

    def all_pdfs_generator():
        for pdf_path in pdf_files:
            print(f"📖 Читаем документ: {pdf_path.name}")
            # Извлекаем title / chapter_name из имени файла (к примеру)
            chapter_name = pdf_path.stem
            yield from prepare_text_for_rag(pdf_path, model, chapter_name=chapter_name)

    output_sql = Path(__file__).parent / "init.sql"
    generate_sql(all_pdfs_generator(), output_file=str(output_sql))


if __name__ == "__main__":
    main()
