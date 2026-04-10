from typing import List, Dict, Any

INSERT_VALUES_PER_STATEMENT = 50

def escape_sql_string(s: str) -> str:
    return s.replace("'", "''")

def generate_seed_sql(cards: List[Dict[str, Any]], output_file: str) -> None:
    """Создает SQL файл ТОЛЬКО с INSERT запросами, подходящий под архитектуру Go."""
    
    insert_header = (
        "INSERT INTO card_contents (front_text, back_text, embedding, source_info) VALUES\n"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("-- Автоматически сгенерированный seed-файл (Теоремы и Термины)\n")
        f.write("-- Триггер trigger_init_card_progress автоматически создаст записи в card_progress!\n\n")

        batch = []
        count = 0
        statements = 0

        def flush_batch():
            nonlocal batch, statements
            if not batch:
                return
            f.write(insert_header)
            f.write(",\n".join(batch))
            f.write(";\n\n")
            statements += 1
            batch.clear()

        for card in cards:
            emb_str = "[" + ",".join(map(str, card["embedding"])) + "]"
            
            row = (
                f"('{escape_sql_string(card['front'])}', "
                f"'{escape_sql_string(card['back'])}', "
                f"'{emb_str}', "
                f"'{escape_sql_string(card['source_info'])}')"
            )
            batch.append(row)
            count += 1

            if len(batch) >= INSERT_VALUES_PER_STATEMENT:
                flush_batch()

        flush_batch()

    print(f"\nУспех! Сгенерирован файл {output_file}.")
    print(f"Всего создано качественных карточек: {count} (SQL-вставок: {statements}).")
