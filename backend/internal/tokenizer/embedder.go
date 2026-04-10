package tokenizer

import (
	"fmt"
	"math"

	"github.com/daulet/tokenizers"
	"github.com/rs/zerolog"
	ort "github.com/yalue/onnxruntime_go"

	"github.com/ilindan-dev/RAGDM/backend/internal/domain"
)

var _ domain.TextEmbedder = (*OnnxEmbedder)(nil)

type OnnxEmbedder struct {
	tk      *tokenizers.Tokenizer
	session *ort.DynamicAdvancedSession
	log     zerolog.Logger
}

func NewOnnxEmbedder(tokenizerPath, onnxModelPath, onnxLibraryPath string, log *zerolog.Logger) (*OnnxEmbedder, error) {
	logger := log.With().Str("logger", "onnx").Logger()
	ort.SetSharedLibraryPath(onnxLibraryPath)
	err := ort.InitializeEnvironment()
	if err != nil {
		logger.Error().Err(err).Msg("Failed to initialize onnx")
		return nil, fmt.Errorf("failed to init ONNX environment: %w", err)
	}

	tk, err := tokenizers.FromFile(tokenizerPath)
	if err != nil {
		return nil, fmt.Errorf("failed to load tokenizer: %w", err)
	}

	inputNames := []string{"input_ids", "attention_mask", "token_type_ids"}
	outputNames := []string{"last_hidden_state"}

	session, err := ort.NewDynamicAdvancedSession(
		onnxModelPath,
		inputNames,
		outputNames,
		nil,
	)
	if err != nil {
		if err := tk.Close(); err != nil {
			logger.Error().Err(err).Msg("Failed to close tokenizer")
		}
		if err := ort.DestroyEnvironment(); err != nil {
			logger.Error().Err(err).Msg("Failed to destroy onnx")
		}
		logger.Error().Err(err).Msg("Failed to create tokenizer")
		return nil, fmt.Errorf("failed to load ONNX session: %w", err)
	}

	return &OnnxEmbedder{
		tk:      tk,
		session: session,
		log:     logger,
	}, nil
}

func (e *OnnxEmbedder) Close() {
	if e.session != nil {
		err := e.session.Destroy()
		if err != nil {
			e.log.Error().Err(err).Msg("Failed to close session")
		}
	}
	if e.tk != nil {
		err := e.tk.Close()
		if err != nil {
			e.log.Error().Err(err).Msg("Failed to close tokenizer")
		}
	}
	err := ort.DestroyEnvironment()
	if err != nil {
		e.log.Error().Err(err).Msg("Failed to destroy onnx")
	}
}

func (e *OnnxEmbedder) Encode(text string) ([]float32, error) {
	tokens, _ := e.tk.Encode(text, true)
	seqLen := int64(len(tokens))

	inputIDs := make([]int64, seqLen)
	attentionMask := make([]int64, seqLen)
	tokenTypeIDs := make([]int64, seqLen)

	for i, id := range tokens {
		inputIDs[i] = int64(id)
		attentionMask[i] = 1
		tokenTypeIDs[i] = 0
	}

	shape := ort.NewShape(1, seqLen)

	inputIDsTensor, err := ort.NewTensor(shape, inputIDs)
	if err != nil {
		return nil, err
	}
	defer func(inputIDsTensor *ort.Tensor[int64]) {
		err := inputIDsTensor.Destroy()
		if err != nil {
			e.log.Error().Err(err).Msg("Failed to destroy inputIDs")
		}
	}(inputIDsTensor)

	attnMaskTensor, err := ort.NewTensor(shape, attentionMask)
	if err != nil {
		return nil, err
	}
	defer func(attnMaskTensor *ort.Tensor[int64]) {
		err := attnMaskTensor.Destroy()
		if err != nil {
			e.log.Error().Err(err).Msg("Failed to destroy attnMask")
		}
	}(attnMaskTensor)

	typeIDsTensor, err := ort.NewTensor(shape, tokenTypeIDs)
	if err != nil {
		return nil, err
	}
	defer func(typeIDsTensor *ort.Tensor[int64]) {
		err := typeIDsTensor.Destroy()
		if err != nil {
			e.log.Error().Err(err).Msg("Failed to destroy typeIDs")
		}
	}(typeIDsTensor)

	outShape := ort.NewShape(1, seqLen, 384)
	outData := make([]float32, seqLen*384)

	outTensor, err := ort.NewTensor(outShape, outData)
	if err != nil {
		return nil, err
	}
	defer func(outTensor *ort.Tensor[float32]) {
		err := outTensor.Destroy()
		if err != nil {
			e.log.Error().Err(err).Msg("Failed to destroy output tensor")
		}
	}(outTensor)

	err = e.session.Run(
		[]ort.ArbitraryTensor{inputIDsTensor, attnMaskTensor, typeIDsTensor},
		[]ort.ArbitraryTensor{outTensor},
	)
	if err != nil {
		return nil, fmt.Errorf("ONNX inference failed: %w", err)
	}

	pooled := make([]float32, 384)

	for i := int64(0); i < seqLen; i++ {
		for j := int64(0); j < 384; j++ {
			pooled[j] += outData[i*384+j]
		}
	}

	for j := 0; j < 384; j++ {
		pooled[j] /= float32(seqLen)
	}

	return pooled, nil
}

func (e *OnnxEmbedder) CosineSimilarity(v1, v2 []float32) float32 {
	if len(v1) != len(v2) || len(v1) == 0 {
		return 0.0
	}

	var dotProduct, normA, normB float64

	for i := 0; i < len(v1); i++ {
		val1 := float64(v1[i])
		val2 := float64(v2[i])

		dotProduct += val1 * val2
		normA += val1 * val1
		normB += val2 * val2
	}

	if normA == 0 || normB == 0 {
		return 0.0
	}

	return float32(dotProduct / (math.Sqrt(normA) * math.Sqrt(normB)))
}
