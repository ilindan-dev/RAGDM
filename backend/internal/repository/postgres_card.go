package repository

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/pgvector/pgvector-go"
	"github.com/rs/zerolog"

	"github.com/ilindan-dev/RAGDM/backend/internal/domain"
	"github.com/ilindan-dev/RAGDM/backend/internal/repository/gen"
)

var _ domain.CardRepository = (*pgCardRepository)(nil)

type pgCardRepository struct {
	q   gen.Querier
	log zerolog.Logger
}

func NewPgCardRepository(q gen.Querier, log *zerolog.Logger) domain.CardRepository {
	return &pgCardRepository{
		q:   q,
		log: log.With().Str("repository", "postgres_card").Logger(),
	}
}

func (r *pgCardRepository) CreateCard(ctx context.Context, front, back,
	source string, embedding []float32) (uuid.UUID, error) {
	log := r.log.With().Str("method", "CreateCard").Str("front", front).Logger()

	var sourcePtr *string
	if source != "" {
		sourcePtr = &source
	}

	vector := pgvector.NewVector(embedding)
	cardID, err := r.q.CreateCardContent(ctx, gen.CreateCardContentParams{
		FrontText:  front,
		BackText:   back,
		Embedding:  &vector,
		SourceInfo: sourcePtr,
	})
	if err != nil {
		log.Error().Err(err).Str("front", front).Msg("failed to create card")
		return uuid.Nil, fmt.Errorf("failed to create card: %w", err)
	}

	_, err = r.q.CreateCardProgress(ctx, gen.CreateCardProgressParams{
		CardID:       cardID,
		Interval:     0,
		Easiness:     2.5,
		Repetitions:  0,
		NextReviewAt: time.Now(),
	})
	if err != nil {
		log.Error().Err(err).Str("front", front).Msg("failed to create card progress")
		return uuid.Nil, fmt.Errorf("failed to create card progress: %w", err)
	}

	return cardID, nil
}

func (r *pgCardRepository) GetCardsToReview(ctx context.Context, limit int32) ([]domain.ReviewCard, error) {
	rows, err := r.q.GetCardsToReview(ctx, limit)
	if err != nil {
		r.log.Error().Err(err).Str("method", "GetCardsToReview").
			Int32("limit", limit).Msg("failed to get card to review")
		return nil, fmt.Errorf("failed to get card to review: %w", err)
	}

	res := make([]domain.ReviewCard, len(rows))
	for i, row := range rows {
		source := ""
		if row.SourceInfo != nil {
			source = *row.SourceInfo
		}

		res[i] = domain.ReviewCard{
			CardID:       row.CardID,
			FrontText:    row.FrontText,
			BackText:     row.BackText,
			SourceInfo:   source,
			Interval:     row.Interval,
			Easiness:     row.Easiness,
			Repetitions:  row.Repetitions,
			NextReviewAt: row.NextReviewAt,
		}
	}
	return res, nil
}

func (r *pgCardRepository) GetCardEmbedding(ctx context.Context, cardID uuid.UUID) ([]float32, error) {
	log := r.log.With().Str("method", "GetCardEmbedding").Stringer("cardID", cardID).Logger()
	embedding, err := r.q.GetCardEmbedding(ctx, cardID)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			log.Warn().Msg("Card embedding not found")
			return nil, domain.ErrNotFound
		}
		r.log.Error().Err(err).Str("method", "GetCardEmbedding").
			Stringer("cardID", cardID).Msg("failed to get card embedding")
		return nil, fmt.Errorf("failed to get card embedding: %w", err)
	}
	return embedding.Slice(), nil
}

func (r *pgCardRepository) GetCardProgress(ctx context.Context, cardID uuid.UUID) (domain.CardProgress, error) {
	log := r.log.With().Str("method", "GetCardProgress").Stringer("cardID", cardID).Logger()

	row, err := r.q.GetCardByID(ctx, cardID)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			log.Warn().Msg("Card progress not found")
			return domain.CardProgress{}, domain.ErrNotFound
		}
		r.log.Error().Err(err).Str("method", "GetCardProgress").
			Stringer("cardID", cardID).Msg("failed to get card progress")
		return domain.CardProgress{}, fmt.Errorf("failed to get card progress: %w", err)
	}

	return domain.CardProgress{
		CardID:       row.CardID.String(),
		Interval:     row.Interval,
		Easiness:     row.Easiness,
		Repetitions:  row.Repetitions,
		NextReviewAt: row.NextReviewAt,
	}, nil
}

func (r *pgCardRepository) UpdateCardProgress(ctx context.Context, progress domain.CardProgress) error {
	log := r.log.With().Str("method", "UpdateCardProgress").Str("cardID", progress.CardID).Logger()
	cardUUID, err := uuid.Parse(progress.CardID)
	if err != nil {
		log.Error().Err(err).Msg("failed to parse card id")
		return fmt.Errorf("failed to parse card id: %w", domain.ErrInvalidCardID)
	}
	err = r.q.UpdateCardProgress(ctx, gen.UpdateCardProgressParams{
		CardID:       cardUUID,
		Interval:     progress.Interval,
		Easiness:     progress.Easiness,
		Repetitions:  progress.Repetitions,
		NextReviewAt: progress.NextReviewAt,
	})
	if err != nil {
		log.Error().Err(err).Msg("failed to update card")
		return fmt.Errorf("failed to update card: %w", err)
	}
	return nil
}

func (r *pgCardRepository) FindSimilarCards(ctx context.Context, queryVector []float32, limit int32) ([]domain.SimilarCard, error) {

	vector := pgvector.NewVector(queryVector)
	rows, err := r.q.FindSimilarCards(ctx, gen.FindSimilarCardsParams{
		Embedding: &vector,
		Limit:     limit,
	})
	if err != nil {
		r.log.Error().Err(err).Str("method", "FindSimilarCards").Err(errors.New("failed to find similar cards"))
		return nil, fmt.Errorf("failed to find similar cards: %w", err)
	}

	res := make([]domain.SimilarCard, len(rows))
	for i, row := range rows {
		source := ""
		if row.SourceInfo != nil {
			source = *row.SourceInfo
		}

		res[i] = domain.SimilarCard{
			ID:         row.ID.String(),
			FrontText:  row.FrontText,
			BackText:   row.BackText,
			SourceInfo: source,
			Similarity: row.Similarity,
		}
	}

	return res, nil
}
