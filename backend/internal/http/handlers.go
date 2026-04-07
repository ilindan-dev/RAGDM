package http

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/ilindan-dev/RAGDM/backend/internal/domain"
)

type SubmitAnswerReq struct {
	Answer string `json:"answer" binding:"required"`
}

type SubmitAnswerResp struct {
	Message    string  `json:"message"`
	Similarity float32 `json:"similarity"`
}

type ReviewBatchResp struct {
	Message string              `json:"message"`
	Cards   []domain.ReviewCard `json:"cards"`
	Total   int                 `json:"total"`
}

type SearchTerminResp struct {
	Message string               `json:"message"`
	Terms   []domain.SimilarCard `json:"terms"`
}

func (h *CardHandler) GetReviewBatch(c *gin.Context) {
	limitStr := c.DefaultQuery("limit", "10")
	limit, err := strconv.ParseInt(limitStr, 10, 32)
	if err != nil {
		h.handleError(c, domain.ErrInvalidRequest, "invalid limit parameter")
		return
	}

	cards, err := h.svc.GetReviewBatch(c.Request.Context(), int32(limit))
	if err != nil {
		h.handleError(c, err, "failed to get review batch")
		return
	}
	c.JSON(http.StatusOK, ReviewBatchResp{
		Message: "success get review batch",
		Cards:   cards,
		Total:   len(cards)},
	)
}

func (h *CardHandler) SubmitAnswer(c *gin.Context) {
	cardIDStr := c.Param("id")
	cardID, err := uuid.Parse(cardIDStr)
	if err != nil {
		h.handleError(c, domain.ErrInvalidCardID, "invalid card id format")
		return
	}

	var req SubmitAnswerReq
	if err := c.ShouldBindJSON(&req); err != nil {
		h.handleError(c, domain.ErrInvalidRequest, "invalid request body")
		return
	}

	similarity, err := h.svc.SubmitAnswer(c.Request.Context(), cardID, req.Answer)
	if err != nil {
		h.handleError(c, err, "failed to submit answer")
		return
	}

	c.JSON(http.StatusOK, SubmitAnswerResp{
		Message:    "answer processed successfully",
		Similarity: similarity,
	})
}

func (h *CardHandler) SearchTermin(c *gin.Context) {
	phrase := c.Query("phrase")
	if phrase == "" {
		h.handleError(c, domain.ErrInvalidRequest, "search phrase cannot be empty")
		return
	}
	limitStr := c.DefaultQuery("limit", "10")
	limit, err := strconv.ParseInt(limitStr, 10, 32)
	if err != nil {
		h.handleError(c, domain.ErrInvalidRequest, "invalid limit parameter")
		return
	}
	cards, err := h.svc.SearchCards(c.Request.Context(), phrase, int32(limit))
	if err != nil {
		h.handleError(c, err, "failed to search cards")
		return
	}

	c.JSON(http.StatusOK, SearchTerminResp{
		Message: "success search terminated cards",
		Terms:   cards,
	})
}
