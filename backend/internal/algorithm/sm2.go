package algorithm

/*
#cgo CFLAGS: -I../../../algorithm/include
#cgo LDFLAGS: -L../../../algorithm/build -lspaced_rep -lm
#include "algorithm.h"
*/
import "C"
import (
	"github.com/ilindan-dev/RAGDM/backend/internal/domain"
)

type SM2Engine struct{}

func NewSM2Engine() *SM2Engine {
	return &SM2Engine{}
}

func (e *SM2Engine) CalculateNextReview(similarity float32, progress domain.CardProgress) domain.ReviewResult {
	cState := C.CardState{
		interval:    C.int64_t(progress.Interval),
		easiness:    C.float(progress.Easiness),
		repetitions: C.int64_t(progress.Repetitions),
	}

	res := C.calculate_next_review(C.float(similarity), cState)

	return domain.ReviewResult{
		Quality:      int32(res.quality),
		NextInterval: int64(res.next_interval),
		NewEasiness:  float32(res.new_easiness),
		Repetitions:  int64(res.repetitions),
	}
}
