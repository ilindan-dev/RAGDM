#include <assert.h>
#include <stdio.h>

#include "algorithm.h"

// auxiliary function
CardState apply_result_to_card(ReviewResult res) {
    CardState new_card;
    new_card.interval = res.next_interval;
    new_card.easiness = res.new_easiness;
    new_card.repetitions = res.repetitions;
    return new_card;
}

int main() {
    printf("Starting algorithm tests...\n");

    // new card
    CardState card = {0, 2.5F, 0};
    ReviewResult result;

    // test 1: bad answer
    printf("Test 1: Bad answer (< 40%%)\n");
    result = calculate_next_review(20.0F, card);

    assert(result.quality == 0);
    assert(result.next_interval == 1);
    assert(result.repetitions == 0);
    assert(result.new_easiness < 2.5F);
    card = apply_result_to_card(result);

    // test 2 perfect answer
    printf("Test 2: Perfect answer (1st time)\n");
    result = calculate_next_review(95.0F, card);

    assert(result.quality == 5);
    assert(result.repetitions == 1);
    assert(result.next_interval == 1);
    assert(result.new_easiness > card.easiness);
    card = apply_result_to_card(result);

    // test 3 perfect answer (2)
    printf("Test 3: Perfect answer (2nd time)\n");
    result = calculate_next_review(85.0F, card);

    assert(result.quality == 5);
    assert(result.repetitions == 2);
    assert(result.next_interval == 6);
    card = apply_result_to_card(result);

    // test 4 perfect answer (3)
    printf("Test 4: Perfect answer (3rd time)\n");
    result = calculate_next_review(100.0F, card);

    assert(result.quality == 5);
    assert(result.repetitions == 3);
    assert(result.next_interval > 6);
    card = apply_result_to_card(result);

    // test 5 bad answer
    printf("Test 5: Bad answer after streak\n");
    result = calculate_next_review(10.0F, card);

    assert(result.quality == 0);
    assert(result.repetitions == 0);
    assert(result.next_interval == 1);

    printf("SUCCESS! All assertions passed. Algorithm works perfectly!\n");
    return 0;
}