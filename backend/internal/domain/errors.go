package domain

import "errors"

var (
	ErrInvalidRequest = errors.New("invalid request")
	ErrUnauthorized   = errors.New("unauthorized")
	ErrNotFound       = errors.New("not found")
	ErrForbidden      = errors.New("forbidden")
	ErrInternal       = errors.New("internal server error")
	ErrInvalidCardID  = errors.New("invalid card id")
)
