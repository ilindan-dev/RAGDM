"""SQL generation and data formatting for database initialization."""
from typing import Dict, Any, List

INSERT_VALUES_PER_STATEMENT = 50


def escape_sql_string(s: str) -> str:
    """Escape single quotes in SQL string values.
    
    Args:
        s: String to escape.
        
    Returns:
        String with single quotes escaped for SQL.
    """
    return s.replace("'", "''")


def format_insert_values_rows(item: Dict[str, Any]) -> List[str]:
    """Format data items as multiple SQL VALUES rows (one per term).
    
    Converts extracted terms and their embeddings into individual card_contents
    records. Each term becomes a separate flashcard with its definition and
    embedding.
    
    Args:
        item: Dictionary with keys: chapter_name, terms, definitions,
              chunk_text, terms_embeddings.
              
    Returns:
        List of SQL VALUES rows, one per extracted term.
    """
    rows = []
    
    # Iterate through terms and create a card for each
    for i, (term, definition, embedding) in enumerate(
        zip(item["terms"], item["definitions"], item["terms_embeddings"])
    ):
        # Format embedding as PostgreSQL vector
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        
        # Create source info: chapter + chunk context
        source_info = f"{item['chapter_name']}|{item['chunk_text'][:200]}"
        
        row = (
            f"('{escape_sql_string(term)}', "
            f"'{escape_sql_string(definition[:500])}', "
            f"'{embedding_str}', "
            f"'{escape_sql_string(source_info)}')"
        )
        rows.append(row)
    
    return rows


def generate_sql(
    data_generator: Any, output_file: str = "init.sql"
) -> None:
    """Generate SQL initialization script with DDL and batch INSERT statements.
    
    Creates a PostgreSQL initialization script containing table creation
    (with vector extension) and batch INSERT statements for card_contents and
    card_progress tables. Batches are sized for optimal performance.
    
    Args:
        data_generator: Generator/iterable yielding data dictionaries.
        output_file: Path where SQL script will be written. Defaults to 'init.sql'.
        
    Returns:
        None. Writes directly to output_file.
    """
    init_script = [
        "-- RAG Flashcard Schema",
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
        "CREATE EXTENSION IF NOT EXISTS vector;",
        "",
        "-- Table: card_contents",
        "-- Stores individual terms with embeddings and source context",
        "CREATE TABLE IF NOT EXISTS card_contents (",
        "    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
        "    front_text  TEXT NOT NULL,",
        "    back_text   TEXT NOT NULL,",
        "    embedding   vector(384),",
        "    source_info TEXT,",
        "    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()",
        ");",
        "",
        "-- HNSW index for similarity search",
        "CREATE INDEX ON card_contents USING hnsw (embedding vector_cosine_ops);",
        "",
        "-- Table: card_progress",
        "-- Tracks spaced repetition metrics for each card",
        "CREATE TABLE IF NOT EXISTS card_progress (",
        "    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
        "    card_id        UUID NOT NULL UNIQUE REFERENCES card_contents (id) ON DELETE CASCADE,",
        "    interval       BIGINT NOT NULL DEFAULT 0,",
        "    easiness       REAL NOT NULL DEFAULT 2.5,",
        "    repetitions    INT NOT NULL DEFAULT 0,",
        "    next_review_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),",
        "    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()",
        ");",
        "",
        "CREATE INDEX IF NOT EXISTS idx_progress_next_review ON card_progress (next_review_at);",
        "",
        f"-- Data: each INSERT contains up to {INSERT_VALUES_PER_STATEMENT} rows.",
        "",
    ]

    insert_header = (
        "INSERT INTO card_contents (front_text, back_text, embedding, source_info) VALUES\n"
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
            # Each item can produce multiple rows (one per term)
            rows = format_insert_values_rows(item)
            for row in rows:
                count += 1
                batch.append(row)

                if len(batch) >= INSERT_VALUES_PER_STATEMENT:
                    flush_batch()

            if count % 100 == 0:
                print(f"Processed and written {count} flashcards to SQL...")

        flush_batch()

    print(
        f"SQL script generated successfully: {output_file}. "
        f"Total flashcards: {count}, INSERT statements: {statements}"
    )
