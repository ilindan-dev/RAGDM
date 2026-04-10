-- +goose Up

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Enable pgvector extension for embedding storage and similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Table: card_contents
-- Purpose: Stores static flashcard content and its semantic representation (embedding).
-- Separating content from progress optimizes database performance during frequent progress updates.
CREATE TABLE IF NOT EXISTS card_contents
(
    id          UUID PRIMARY KEY     DEFAULT uuid_generate_v4(),
    front_text  TEXT        NOT NULL,
    back_text   TEXT        NOT NULL,

    -- 384-dimensional vector suitable for models paraphrase-multilingual-MiniLM-L12-v2
    embedding   vector(384),

    -- Optional metadata
    source_info TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- HNSW index for lightning-fast approximate nearest neighbor (ANN) search.
-- vector_cosine_ops specifies cosine distance metric, mapping directly to our C algorithm's similarity.
CREATE INDEX ON card_contents USING hnsw (embedding vector_cosine_ops);

-- Table: card_progress
-- Purpose: Tracks spaced repetition metrics for each card based on the SM-2 algorithm.
-- Data types (BIGINT, REAL, INT) strictly match the C-core data types for seamless FFI/Cgo binding.
CREATE TABLE IF NOT EXISTS card_progress
(
    id             UUID PRIMARY KEY     DEFAULT uuid_generate_v4(),
    card_id        UUID        NOT NULL UNIQUE REFERENCES card_contents (id) ON DELETE CASCADE,
    interval       BIGINT      NOT NULL DEFAULT 0,
    easiness       REAL        NOT NULL DEFAULT 2.5,
    repetitions    BIGINT      NOT NULL DEFAULT 0,
    next_review_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- B-Tree index to efficiently fetch cards that are due for review.
CREATE INDEX IF NOT EXISTS idx_progress_next_review ON card_progress (next_review_at);

-- +goose StatementBegin
CREATE OR REPLACE FUNCTION init_card_progress()
    RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO card_progress (card_id, interval, easiness, repetitions, next_review_at)
    VALUES (NEW.id, 0, 2.5, 0, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_init_card_progress
    AFTER INSERT ON card_contents
    FOR EACH ROW
EXECUTE FUNCTION init_card_progress();
-- +goose StatementEnd

-- +goose Down

DROP TABLE IF EXISTS card_progress;
DROP TABLE IF EXISTS card_contents;
DROP EXTENSION IF EXISTS vector;
DROP EXTENSION IF EXISTS "uuid-ossp";
DROP FUNCTION IF EXISTS init_card_progress();