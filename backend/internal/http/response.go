package http

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ilindan-dev/RAGDM/backend/internal/domain"
)

type errorDetail struct {
	Code    string `json:"code"`
	Message string `json:"message"`
}

type errorResponse struct {
	Error errorDetail `json:"error"`
}

func (h *CardHandler) handleError(c *gin.Context, err error, msg string) {
	if err == nil {
		return
	}

	h.log.Error().Err(err).Msg(msg)

	var status int
	var code string

	switch {
	case errors.Is(err, domain.ErrNotFound):
		status = http.StatusNotFound
		code = "NOT_FOUND"
	case errors.Is(err, domain.ErrUnauthorized):
		status = http.StatusUnauthorized
		code = "UNAUTHORIZED"
	case errors.Is(err, domain.ErrForbidden):
		status = http.StatusForbidden
		code = "FORBIDDEN"
	case errors.Is(err, domain.ErrInvalidCardID):
		status = http.StatusBadRequest
		code = "INVALID_CARD_ID"
	default:
		status = http.StatusInternalServerError
		code = "INTERNAL_ERROR"
	}

	c.AbortWithStatusJSON(status, errorResponse{
		Error: errorDetail{
			Code:    code,
			Message: err.Error(),
		},
	})
}
