#include "algorithm.h"

struct ReviewResult calculate_next_review(float similarity_percent,
                                          struct CardState current_state) {
    struct ReviewResult result;
    int quality = 0;

    // percent -> grade
    if (similarity_percent < 40.0F) {
        quality = 0;  // bad
    } else if (similarity_percent < 60.0F) {
        quality = 2;  // normal
    } else if (similarity_percent < 80.0F) {
        quality = 4;  // good
    } else {
        quality = 5;  // perfect
    }

    result.quality = quality;

    // new Easiness Factor (EF) on formula SM-2
    // EF = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    float q_diff = 5.0F - (float)quality;
    float new_ef = current_state.easiness + (0.1F - (q_diff * (0.08F + (q_diff * 0.02F))));

    // EF != <1.3
    if (new_ef < 1.3F) {
        new_ef = 1.3F;
    }
    result.new_easiness = new_ef;

    // update counter
    if (quality < 3) {
        // bad answer -> progress 0
        result.repetitions = 0;
        result.next_interval = 1;
    } else {
        // good answer -> +1 counter
        result.repetitions = current_state.repetitions + 1;

        // calculation new interval
        if (result.repetitions == 1) {
            result.next_interval = 1;
        } else if (result.repetitions == 2) {
            result.next_interval = 6;
        } else {
            // + 0.5F for correct rounding
            result.next_interval =
                (int)((((float)current_state.interval) * result.new_easiness) + 0.5F);
        }
    }

    return result;
}