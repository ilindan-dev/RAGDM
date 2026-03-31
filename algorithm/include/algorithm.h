#ifndef ALGORITHM_H
#define ALGORITHM_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Current state of the flashcard (data from DB)
 */
typedef struct {
    int64_t interval;    /**< Current interval until the next review (in days) */
    float easiness;      /**< Easiness Factor (usually >= 1.3) */
    int64_t repetitions; /**< Number of consecutive correct answers */
} CardState;

/**
 * @brief Result of the spaced repetition calculation to be saved in the DB
 */
typedef struct {
    int64_t next_interval; /**< Newly calculated interval (in days) */
    float new_easiness;    /**< Updated Easiness Factor */
    int64_t repetitions;   /**< Updated repetitions counter */
    int32_t quality;       /**< Answer quality grade (from 0 to 5) */
} ReviewResult;

/**
 * @brief Calculates the next review parameters for a card based on similarity percentage.
 * @param similarity_percent Cosine similarity percentage of the user's answer vs the reference (0.0
 * - 100.0).
 * @param current_state Struct containing the current interval, easiness, and repetitions.
 * @return ReviewResult Updated data ready to be saved in the database.
 */
ReviewResult calculate_next_review(float similarity_percent, CardState current_state);

#ifdef __cplusplus
}
#endif

#endif