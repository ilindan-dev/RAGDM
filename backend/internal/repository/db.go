package repository

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/rs/zerolog"
)

func NewPool(ctx context.Context, connString string, maxConns, minConns int32, log *zerolog.Logger) (*pgxpool.Pool, error) {
	config, err := pgxpool.ParseConfig(connString)
	if err != nil {
		log.Error().Err(err).Msg("failed to parse database connection string")
		return nil, err
	}

	config.MaxConns = maxConns
	config.MinConns = minConns

	pool, err := pgxpool.NewWithConfig(ctx, config)
	if err != nil {
		log.Error().Err(err).Msg("failed to create database connection pool")
		return nil, err
	}

	if err := pool.Ping(ctx); err != nil {
		log.Error().Err(err).Msg("failed to ping database")
		return nil, err
	}

	log.Info().Msg("Successfully connected to PostgreSQL pool")
	return pool, nil
}
