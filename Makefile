# Environment Variables
# Include variables from .env file if it exists
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Default database connection string for Goose migrations
DB_DSN ?= "postgres://$(DB_USER):$(DB_PASSWORD)@localhost:$(DB_PORT)/$(DB_NAME)?sslmode=disable"

.PHONY: help db-up db-down migrate-up migrate-down

# Docker Commands
## db-up: Start only the database container
db-up:
	docker compose up -d db
## db-down: Down the database container
db-down:
	docker compose down db -v
## env-up: Start the entire application (DB + Backend)
env-up:
	docker compose up --build -d
## env-down: Stop and remove all containers
env-down:
	docker compose down

# Database Migrations (Goose)
## migrate-up: Apply all pending migrations
migrate-up:
	goose -dir migrations postgres $(DB_DSN) up
## migrate-down: Rollback the last migration
migrate-down:
	goose -dir migrations postgres $(DB_DSN) down