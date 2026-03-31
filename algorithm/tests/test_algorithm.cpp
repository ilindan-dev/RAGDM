#include <gtest/gtest.h>

#include "algorithm.h"

// Auxiliary function to apply ReviewResult to CardState
CardState ApplyResultToCard(const ReviewResult& res) {
    CardState new_card;
    new_card.interval = res.next_interval;
    new_card.easiness = res.new_easiness;
    new_card.repetitions = res.repetitions;
    return new_card;
}

// Test fixture (base class for tests) to avoid code duplication
class AlgorithmTest : public ::testing::Test {
   protected:
    CardState default_card = {0, 2.5F, 0};
};

TEST_F(AlgorithmTest, BadAnswer) {
    const ReviewResult result = calculate_next_review(15.0F, default_card);

    EXPECT_EQ(result.quality, 0);
    EXPECT_EQ(result.next_interval, 1);
    EXPECT_EQ(result.repetitions, 0);
    EXPECT_LT(result.new_easiness, 2.5F);
}

TEST_F(AlgorithmTest, PerfectAnswerFirstTime) {
    const ReviewResult result = calculate_next_review(95.0F, default_card);

    EXPECT_EQ(result.quality, 5);
    EXPECT_EQ(result.repetitions, 1);
    EXPECT_EQ(result.next_interval, 1);
    EXPECT_GT(result.new_easiness, default_card.easiness);
}

TEST_F(AlgorithmTest, PerfectAnswerSecondTime) {
    const CardState card = ApplyResultToCard(calculate_next_review(95.0F, default_card));
    const ReviewResult result = calculate_next_review(95.0F, card);

    EXPECT_EQ(result.quality, 5);
    EXPECT_EQ(result.repetitions, 2);
    EXPECT_EQ(result.next_interval, 6);
}

TEST_F(AlgorithmTest, PerfectAnswerThirdTime) {
    const CardState card1 = ApplyResultToCard(calculate_next_review(95.0F, default_card));
    const CardState card2 = ApplyResultToCard(calculate_next_review(85.0F, card1));
    const ReviewResult result = calculate_next_review(100.0F, card2);

    EXPECT_EQ(result.quality, 5);
    EXPECT_EQ(result.repetitions, 3);
    EXPECT_GT(result.next_interval, 6);
}

TEST_F(AlgorithmTest, BadAnswerAfterStreak) {
    const CardState card1 = ApplyResultToCard(calculate_next_review(95.0F, default_card));
    const CardState card2 = ApplyResultToCard(calculate_next_review(85.0F, card1));
    const ReviewResult result = calculate_next_review(10.0F, card2);

    EXPECT_EQ(result.quality, 0);
    EXPECT_EQ(result.repetitions, 0);
    EXPECT_EQ(result.next_interval, 1);
}