import re
import pdfplumber
import yake


def parse_hall_text(pdf_path, start_page=1, end_page=None):
    """
    Извлекает текст из PDF разными методами.
    Возвращает генератор объектов {page, text}.
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
                print(f"⚠️ Страница {page_num}: текст не найден")

            page.flush_cache()

            if page_num % 10 == 0:
                print(f"⌛ Обработано {page_num} страниц...")


def filter_text(text):
    """Фильтрует текст от мусора и служебной информации."""
    text = re.sub(
        r"---algorithm---.*?---end---", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r"(?:рис|fig)\.\s*\d+[^\n]*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\(стр\.\s+\d+\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[страница\s+\d+\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_keywords(text, top_n=20):
    """Извлечение ключевых слов через алгоритм YAKE."""
    # Оффлайн NLP извлечение терминов, отсекаются общие/стоп слова
    kw_extractor = yake.KeywordExtractor(
        lan="ru", n=1, dedupLim=0.9, top=top_n, features=None
    )
    keywords = kw_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]


def split_into_blocks(text):
    """
    Разбивает текст на логические блоки (Определения, Теоремы и обычный текст).
    """
    blocks = []
    current_type = "general"
    current_text = []

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


def prepare_text_for_rag(
    pdf_path, model, chapter_name="unknown", start_page=1, end_page=None
):
    """
    Полный pipeline для RAG: парсинг → фильтрация → блоки → эмбеддинги.
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

            keywords = extract_keywords(block_text)
            embedding = model.encode(block_text).tolist()

            yield {
                "chapter_name": chapter_name,
                "keywords": keywords,
                "chunk_text": block_text,
                "embedding": embedding,
            }


def escape_sql_string(s):
    """Помощник для эскейпинга одинарных кавычек в SQL."""
    return s.replace("'", "''")


INSERT_VALUES_PER_STATEMENT = 50


def format_insert_values_row(item):
    """Одна строка для списка VALUES (...), (...), ..."""
    kw_cleaned = [
        str(kw).replace("'", "").replace('"', "") for kw in item["keywords"][:10]
    ]
    keywords_pg = "{" + ",".join(kw_cleaned) + "}"
    embedding_str = "[" + ",".join(map(str, item["embedding"])) + "]"
    return (
        f"('{escape_sql_string(item['chapter_name'])}', "
        f"'{keywords_pg}', "
        f"'{escape_sql_string(item['chunk_text'])}', "
        f"'{embedding_str}')"
    )


def generate_sql(data_generator, output_file="init.sql"):
    """
    Генерирует init.sql: DDL и пакетные INSERT (не по одной строке на команду).
    """
    init_script = [
        "-- Инициализация таблиц для RAG",
        "CREATE EXTENSION IF NOT EXISTS vector;",
        "CREATE TABLE IF NOT EXISTS documents (",
        "    id SERIAL PRIMARY KEY,",
        "    chapter_name TEXT,",
        "    keywords TEXT[],",
        "    chunk_text TEXT,",
        "    embedding vector(384)",
        ");",
        "",
        f"-- Данные: один INSERT содержит до {INSERT_VALUES_PER_STATEMENT} строк.",
        "",
    ]

    insert_header = (
        "INSERT INTO documents (chapter_name, keywords, chunk_text, embedding) VALUES\n"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        for line in init_script:
            f.write(line + "\n")

        count = 0
        batch = []
        statements = 0

        def flush_batch():
            nonlocal batch, statements
            if not batch:
                return
            f.write(insert_header)
            f.write(",\n".join(batch))
            f.write(";\n\n")
            statements += 1
            batch = []

        for item in data_generator:
            count += 1
            batch.append(format_insert_values_row(item))

            if len(batch) >= INSERT_VALUES_PER_STATEMENT:
                flush_batch()

            if count % 10 == 0:
                print(f"✍️ Обработано и записано {count} логических блоков в SQL...")

        flush_batch()

    print(
        f"✅ SQL скрипт успешно сгенерирован: {output_file}. "
        f"Всего записей (блоков): {count}, операторов INSERT: {statements}"
    )
