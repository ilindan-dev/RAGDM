package domain

import (
	"context"

	"github.com/google/uuid"
)

type CardRepository interface {
	CreateCard(ctx context.Context, front, back, source string, embedding []float32) (uuid.UUID, error)
	GetCardsToReview(ctx context.Context, limit int32) ([]ReviewCard, error)
	GetCardProgress(ctx context.Context, cardID uuid.UUID) (CardProgress, error)
	UpdateCardProgress(ctx context.Context, progress CardProgress) error
	GetCardEmbedding(ctx context.Context, cardID uuid.UUID) ([]float32, error)
	FindSimilarCards(ctx context.Context, queryVector []float32, limit int32) ([]SimilarCard, error)
}

type AlgoEngine interface {
	CalculateNextReview(similarity float32, progress CardProgress) ReviewResult
}

type CardService interface {
	CreateFlashcard(ctx context.Context, front, back, source string, embedding []float32) (uuid.UUID, error)
	GetReviewBatch(ctx context.Context, limit int32) ([]ReviewCard, error)
	ProcessAnswer(ctx context.Context, cardID uuid.UUID, similarity float32) error
	SubmitAnswer(ctx context.Context, cardID uuid.UUID, userAnswer string) (float32, error)
	SearchCards(ctx context.Context, query string, limit int32) ([]SimilarCard, error)
}

// TextEmbedder is a contract for the ML part
type TextEmbedder interface {
	// Encode turns text into a vector of dimension 384
	Encode(text string) ([]float32, error)
	// CosineSimilarity calculates the cosine similarity of two vectors (from 0.0 to 1.0)
	CosineSimilarity(v1, v2 []float32) float32
}
