package domain

import (
	"time"

	"github.com/google/uuid"
)

// CardContent represents the immutable part of the card (text and vector)
type CardContent struct {
	ID         string
	FrontText  string
	BackText   string
	SourceInfo string
	CreatedAt  time.Time
}

// CardProgress presents the dynamic part of the SM-2 algorithm
type CardProgress struct {
	ID           string
	CardID       string
	Interval     int64
	Easiness     float32
	Repetitions  int64
	NextReviewAt time.Time
}

// ReviewResult is what we get from our algorithm in C
type ReviewResult struct {
	Quality      int32
	NextInterval int64
	NewEasiness  float32
	Repetitions  int64
}

// ReviewCard combines content and progress for front/repeat
type ReviewCard struct {
	CardID       uuid.UUID
	FrontText    string
	BackText     string
	SourceInfo   string
	Interval     int64
	Easiness     float32
	Repetitions  int64
	NextReviewAt time.Time
}

// SimilarCard represents the similar card for request
type SimilarCard struct {
	ID         string
	FrontText  string
	BackText   string
	SourceInfo string
	Similarity float64
}
