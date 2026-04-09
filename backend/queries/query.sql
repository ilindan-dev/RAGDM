-- name: CreateCardContent :one
-- Creates a new flashcard with its static content and vector embedding.
INSERT INTO card_contents (front_text,
                           back_text,
                           embedding,
                           source_info)
VALUES ($1, $2, $3, $4)
RETURNING id;


-- name: CreateCardProgress :one
-- Initializes the SM-2 tracking state for a newly created card.
INSERT INTO card_progress (card_id,
                           interval,
                           easiness,
                           repetitions,
                           next_review_at)
VALUES ($1, $2, $3, $4, $5)
RETURNING id;


-- name: GetCardsToReview :many
-- Fetches a batch of cards that are due for review based on the SM-2 schedule.
SELECT c.id AS card_id,
       c.front_text,
       c.back_text,
       c.source_info,
       p.interval,
       p.easiness,
       p.repetitions,
       p.next_review_at
FROM card_contents c
         JOIN card_progress p ON c.id = p.card_id
WHERE p.next_review_at <= NOW()
ORDER BY p.next_review_at ASC
LIMIT $1;


-- name: UpdateCardProgress :exec
-- Updates the SM-2 metrics after a user reviews a card.
UPDATE card_progress
SET interval       = $2,
    easiness       = $3,
    repetitions    = $4,
    next_review_at = $5,
    updated_at     = NOW()
WHERE card_id = $1;


-- name: FindSimilarCards :many
-- Performs an Approximate Nearest Neighbor (ANN) search using pgvector.
-- The <=> operator calculates cosine distance. 
-- We return 1 - distance to represent cosine similarity for the C-core algorithm.
SELECT id,
       front_text,
       back_text,
       source_info,
       -- Calculate similarity (1.0 = exact match)
       (1 - (embedding <=> $1))::float8 AS similarity
FROM card_contents
-- Filter threshold: (embedding <=> $1) < 0.3 is equivalent to similarity > 0.7
WHERE (embedding <=> $1) < 0.3
ORDER BY embedding <=> $1 ASC
LIMIT $2;


-- name: GetCardByID :one
-- Fetches a single card with its content and current progress.
SELECT c.id AS card_id,
       c.front_text,
       c.back_text,
       p.interval,
       p.easiness,
       p.repetitions,
       p.next_review_at
FROM card_contents c
         JOIN card_progress p ON c.id = p.card_id
WHERE c.id = $1
LIMIT 1;

-- name: GetCardEmbedding :one
-- Fetches an embedding card with need id.
SELECT embedding
FROM card_contents
WHERE id = $1
LIMIT 1;