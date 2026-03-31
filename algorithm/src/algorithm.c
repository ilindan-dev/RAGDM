#include "algorithm.h"

#include <math.h>

// --- SM-2 Algorithm Constants ---

// Thresholds for converting cosine similarity (0.0 - 100.0) to a quality grade (0 - 5)
static const float THRESHOLD_GRADE_1 = 20.0F;
static const float THRESHOLD_GRADE_2 = 40.0F;
static const float THRESHOLD_GRADE_3 = 60.0F;
static const float THRESHOLD_GRADE_4 = 80.0F;
static const float THRESHOLD_GRADE_5 = 95.0F;

// Base constraints and intervals (in days)
static const float MIN_EASINESS_FACTOR = 1.3F;
static const int64_t INTERVAL_FIRST_STEP = 1;
static const int64_t INTERVAL_SECOND_STEP = 6;

/**
 * @brief Helper function: converts similarity percentage into a discrete grade from 0 to 5.
 * Hidden from other translation units via the static modifier.
 */
static int32_t determine_quality_grade(const float similarity_percent) {
    if (similarity_percent < THRESHOLD_GRADE_1)
        return 0;  // Complete blackout / completely incorrect
    if (similarity_percent < THRESHOLD_GRADE_2)
        return 1;  // Incorrect, but remembered the correct answer
    if (similarity_percent < THRESHOLD_GRADE_3)
        return 2;  // Incorrect, but the answer seemed familiar
    if (similarity_percent < THRESHOLD_GRADE_4)
        return 3;  // Correct, but with significant difficulty
    if (similarity_percent < THRESHOLD_GRADE_5) return 4;  // Correct, after a slight hesitation
    return 5;                                              // Perfect and quick response
}

ReviewResult calculate_next_review(const float similarity_percent, const CardState current_state) {
    ReviewResult result;

    // Determine response quality
    result.quality = determine_quality_grade(similarity_percent);

    // Calculate new Easiness Factor (EF)
    // Original SM-2 formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    const float q_diff = 5.0F - (float)result.quality;
    const float ef_modifier = 0.1F - (q_diff * (0.08F + (q_diff * 0.02F)));

    result.new_easiness = current_state.easiness + ef_modifier;

    // EF must not drop below the minimum threshold
    if (result.new_easiness < MIN_EASINESS_FACTOR) {
        result.new_easiness = MIN_EASINESS_FACTOR;
    }

    // Calculate repetitions counter and next interval
    if (result.quality < 3) {
        // Grades 0, 1, or 2 indicate forgetting. Reset progress.
        result.repetitions = 0;
        result.next_interval = INTERVAL_FIRST_STEP;
    } else {
        // Successful review (grades 3, 4, 5)
        result.repetitions = current_state.repetitions + 1;

        if (result.repetitions == 1) {
            result.next_interval = INTERVAL_FIRST_STEP;
        } else if (result.repetitions == 2) {
            result.next_interval = INTERVAL_SECOND_STEP;
        } else {
            // Mathematically correct rounding instead of the (int)(... + 0.5F) hack
            const float next_interval_calc = (float)current_state.interval * result.new_easiness;
            result.next_interval = (int64_t)roundf(next_interval_calc);
        }
    }

    return result;
}