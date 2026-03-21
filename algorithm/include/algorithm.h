#ifndef ALGORITHM_H
#define ALGORITHM_H

#ifdef __cplusplus
extern "C" {
#endif

// struct, current state card
struct CardState {
    int interval;     // current interval
    float easiness;   // diff level
    int repetitions;  // accurace repeat
};

// struct for returning new data
struct ReviewResult {
    int next_interval;   // new interval
    float new_easiness;  // update diff level
    int repetitions;     // update quantity repeat
    int quality;         // grade
};

/**
 * main function
 * @param similarity_percent match percentage
 * @param current_state current param card
 * @return update param card for save in DB
 */
struct ReviewResult calculate_next_review(float similarity_percent, struct CardState current_state);

#ifdef __cplusplus
}
#endif

#endif