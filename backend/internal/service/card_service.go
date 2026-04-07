package service

import (
	"context"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/ilindan-dev/RAGDM/backend/internal/domain"
	"github.com/rs/zerolog"
)

var _ domain.CardService = (*cardService)(nil)

type cardService struct {
	repo     domain.CardRepository
	engine   domain.AlgoEngine
	embedder domain.TextEmbedder
	log      zerolog.Logger
}

func NewCardService(repo domain.CardRepository, engine domain.AlgoEngine, embedder domain.TextEmbedder,
	log *zerolog.Logger) domain.CardService {
	return &cardService{
		repo:     repo,
		engine:   engine,
		embedder: embedder,
		log:      log.With().Str("service", "card").Logger(),
	}
}

func (s *cardService) CreateFlashcard(ctx context.Context, front, back,
	source string, embedding []float32) (uuid.UUID, error) {
	cardID, err := s.repo.CreateCard(ctx, front, back, source, embedding)
	if err != nil {
		s.log.Error().Err(err).Str("method", "CreateFlashcard").
			Str("front", front).Msg("failed to create card")
		return uuid.Nil, fmt.Errorf("failed to create flashcard: %w", err)
	}
	return cardID, nil
}

func (s *cardService) GetReviewBatch(ctx context.Context, limit int32) ([]domain.ReviewCard, error) {
	cards, err := s.repo.GetCardsToReview(ctx, limit)
	if err != nil {
		s.log.Error().Err(err).Str("method", "GetReviewBatch").
			Int32("limit", limit).Msg("failed to get cards")
		return nil, fmt.Errorf("failed to get review batch: %w", err)
	}
	return cards, nil
}

func (s *cardService) ProcessAnswer(ctx context.Context, cardID uuid.UUID, similarity float32) error {
	progress, err := s.repo.GetCardProgress(ctx, cardID)
	if err != nil {
		s.log.Error().Err(err).Str("method", "ProcessAnswer").
			Stringer("card", cardID).Msg("failed to get card progress")
		return fmt.Errorf("failed to get card progress: %w", err)
	}

	result := s.engine.CalculateNextReview(similarity, progress)

	progress.Interval = result.NextInterval
	progress.Easiness = result.NewEasiness
	progress.Repetitions = result.Repetitions
	progress.NextReviewAt = time.Now().Add(time.Duration(result.NextInterval) * 24 * time.Hour)

	if err := s.repo.UpdateCardProgress(ctx, progress); err != nil {
		s.log.Error().Err(err).Str("method", "ProcessAnswer").
			Stringer("card", cardID).Msg("failed to update card")
		return fmt.Errorf("failed to update progress: %w", err)
	}

	return nil
}

func (s *cardService) SubmitAnswer(ctx context.Context, cardID uuid.UUID, userAnswer string) (float32, error) {
	userVector, err := s.embedder.Encode(userAnswer)
	if err != nil {
		s.log.Error().Err(err).Msg("failed to encode user answer")
		return 0, fmt.Errorf("failed to encode answer: %w", err)
	}

	referenceVector, err := s.repo.GetCardEmbedding(ctx, cardID)
	if err != nil {
		s.log.Error().Err(err).Stringer("cardID", cardID).Msg("failed to get reference embedding")
		return 0, fmt.Errorf("failed to get card embedding: %w", err)
	}

	similarity := s.embedder.CosineSimilarity(userVector, referenceVector)

	s.log.Debug().Float32("similarity", similarity).Msg("Calculated answer similarity")

	return similarity, s.ProcessAnswer(ctx, cardID, similarity)
}

func (s *cardService) SearchCards(ctx context.Context, query string, limit int32) ([]domain.SimilarCard, error) {
	log := s.log.With().Str("method", "SearchCards").
		Str("query", query).Str("limit", fmt.Sprint(limit)).Logger()
	queryVector, err := s.embedder.Encode(query)
	if err != nil {
		log.Error().Err(err).Msg("failed to encode query")
		return nil, fmt.Errorf("failed to encode query: %w", err)
	}

	cards, err := s.repo.FindSimilarCards(ctx, queryVector, limit)
	if err != nil {
		log.Error().Err(err).Msg("failed to find cards")
		return nil, fmt.Errorf("failed to find cards: %w", err)
	}
	return cards, nil
}
