package repository

import (
	"context"
	"database/sql"
	"embed"
	"fmt"

	"log/slog"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/jackc/pgx/v5/stdlib"
	"github.com/pressly/goose/v3"
)

//nolint:typecheck // for embed migrations
//go:embed migrations/*.sql
var embedMigrations embed.FS

func RunMigrations(ctx context.Context, pool *pgxpool.Pool) error {
	db := stdlib.OpenDB(*pool.Config().ConnConfig)
	defer func(db *sql.DB) {
		err := db.Close()
		if err != nil {
			slog.Error("Failed to close DB connection", "error", err)
		}
	}(db)

	goose.SetBaseFS(embedMigrations)

	if err := goose.SetDialect("postgres"); err != nil {
		slog.Error("Failed to set goose dialect", "error", err)
		return fmt.Errorf("failed to set goose dialect: %w", err)
	}

	if err := goose.Up(db, "migrations"); err != nil {
		slog.Error("Failed to run migrations", "error", err)
		return fmt.Errorf("failed to run goose migrations: %w", err)
	}

	return nil
}
