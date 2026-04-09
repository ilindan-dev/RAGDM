package http

import (
	"github.com/gin-gonic/gin"
	"github.com/ilindan-dev/RAGDM/backend/internal/domain"
	"github.com/rs/zerolog"
)

type CardHandler struct {
	svc domain.CardService
	log zerolog.Logger
}

func NewHandler(service domain.CardService, log *zerolog.Logger) *CardHandler {
	return &CardHandler{
		svc: service,
		log: log.With().Str("handler", "card").Logger(),
	}
}

func (h *CardHandler) InitRoutes(ginMode string) *gin.Engine {
	switch ginMode {
	case "debug":
		gin.SetMode(gin.DebugMode)
	case "release":
		gin.SetMode(gin.ReleaseMode)
	default:
		gin.SetMode(gin.DebugMode)
	}

	router := gin.New()
	router.Use(gin.Recovery())

	router.StaticFile("/", "./frontend/index.html")

	card := router.Group("/api/v1/cards")
	card.GET("/review", h.GetReviewBatch)
	card.POST("/:id/answer", h.SubmitAnswer)
	card.GET("/search", h.SearchTermin)

	return router
}
