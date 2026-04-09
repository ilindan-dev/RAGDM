package config

import (
	"fmt"
	"time"

	"github.com/ilyakaznacheev/cleanenv"
)

type HTTPConfig struct {
	Port    string        `yaml:"port" env:"HTTP_PORT" env-default:"8080"`
	Timeout time.Duration `yaml:"timeout" env:"API_TIMEOUT" env-default:"5s"`
	GinMode string        `yaml:"gin_mode" env:"GIN_MODE" env-default:"debug"`
}

type LogConfig struct {
	Level string `env-default:"info" yaml:"log_level" env:"LOG_LEVEL"`
}

type DBConfig struct {
	URL      string `env:"DATABASE_URL" env-required:"true"`
	MaxConns int32  `yaml:"max_conns" env:"DB_MAX_CONNS" env-default:"10"`
	MinConns int32  `yaml:"min_conns" env:"DB_MIN_CONNS" env-default:"2"`
}

type EmbederConfig struct {
	TokenizerPath   string `yaml:"tokenizer_path" env:"TOKENIZER_PATH" env-default:"/app/models/tokenizer.json"`
	ONNXModelPath   string `yaml:"onnx_model_path" env:"ONNX_MODEL_PATH" env-default:"/app/models/model.onnx"`
	ONNXLibraryPath string `yaml:"onnx_library_path" env:"ONNX_LIBRARY_PATH" env-default:"/usr/local/lib/libonnxruntime.so"`
}

type Config struct {
	HTTP    HTTPConfig    `yaml:"http"`
	Log     LogConfig     `yaml:"logger"`
	DB      DBConfig      `yaml:"postgres"`
	Embeder EmbederConfig `yaml:"embeder"`
}

func NewConfig() (*Config, error) {
	cfg := &Config{}

	_ = cleanenv.ReadConfig("config.yaml", cfg)
	err := cleanenv.ReadEnv(cfg)
	if err != nil {
		return nil, fmt.Errorf("config error: %w", err)
	}

	return cfg, nil
}
