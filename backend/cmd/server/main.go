package main

import (
	"context"
	"errors"
	"log"
	nhttp "net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/ilindan-dev/RAGDM/backend/internal/algorithm"
	"github.com/ilindan-dev/RAGDM/backend/internal/config"
	"github.com/ilindan-dev/RAGDM/backend/internal/http"
	"github.com/ilindan-dev/RAGDM/backend/internal/repository"
	"github.com/ilindan-dev/RAGDM/backend/internal/repository/gen"
	"github.com/ilindan-dev/RAGDM/backend/internal/service"
	"github.com/ilindan-dev/RAGDM/backend/internal/tokenizer"
	"github.com/rs/zerolog"
)

func main() {
	cfg, err := config.NewConfig()
	if err != nil {
		log.Fatalf("error loading config: %v", err)
	}

	output := zerolog.ConsoleWriter{Out: os.Stdout, TimeFormat: time.RFC3339}
	logger := zerolog.New(output).With().Timestamp().Logger()

	if level, err := zerolog.ParseLevel(cfg.Log.Level); err == nil {
		zerolog.SetGlobalLevel(level)
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	pool, err := repository.NewPool(ctx, cfg.DB.URL, cfg.DB.MaxConns, cfg.DB.MinConns, &logger)
	if err != nil {
		logger.Fatal().Err(err).Msg("Database connection failed")
	}
	defer pool.Close()

	logger.Info().Msg("Running database migrations...")
	if err := repository.RunMigrations(ctx, pool); err != nil {
		logger.Fatal().Err(err).Msg("Failed to run migrations")
	}
	logger.Info().Msg("Migrations completed successfully")

	seedPath := "/app/seed_cards.sql"
	if _, err := os.Stat(seedPath); err == nil {
		var count int
		err := pool.QueryRow(ctx, "SELECT COUNT(*) FROM card_contents").Scan(&count)
		if err == nil && count == 0 {
			logger.Info().Msg("Seeding database with initial cards...")
			sqlBytes, err := os.ReadFile(seedPath)
			if err != nil {
				logger.Error().Err(err).Msg("Failed to read seed file")
			} else {
				_, err = pool.Exec(ctx, string(sqlBytes))
				if err != nil {
					logger.Error().Err(err).Msg("Failed to execute seed_cards.sql")
				} else {
					logger.Info().Msg("Database seeded successfully!")
				}
			}
		} else if count > 0 {
			logger.Debug().Int("count", count).Msg("Database already contains data, skipping seed.")
		}
	}

	queries := gen.New(pool)

	cardRepo := repository.NewPgCardRepository(queries, &logger)
	algoEngine := algorithm.NewSM2Engine()
	embeder, err := tokenizer.NewOnnxEmbedder(cfg.Embeder.TokenizerPath, cfg.Embeder.ONNXModelPath,
		cfg.Embeder.ONNXLibraryPath, &logger)
	if err != nil {
		logger.Fatal().Err(err).Msg("Failed to create embedded tokenizer")
	}

	defer embeder.Close()

	cardService := service.NewCardService(cardRepo, algoEngine, embeder, &logger)

	cardHandler := http.NewHandler(cardService, &logger)

	srv := &nhttp.Server{
		Addr:        ":" + cfg.HTTP.Port,
		Handler:     cardHandler.InitRoutes(cfg.HTTP.GinMode),
		ReadTimeout: cfg.HTTP.Timeout,
	}

	go func() {
		logger.Info().Msgf("HTTP server listening on %s", cfg.HTTP.Port)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, nhttp.ErrServerClosed) {
			logger.Fatal().Err(err).Msg("Server failed")
		}
	}()

	<-ctx.Done()

	logger.Info().Msg("Shutting down gracefully...")

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		logger.Error().Err(err).Msg("Server forced to shutdown")
	}

	logger.Info().Msg("Server exited correctly")
}
