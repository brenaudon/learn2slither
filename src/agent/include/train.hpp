#ifndef TRAIN_HPP
#define TRAIN_HPP

#include "learn2slither.hpp"
#include "engine.hpp"

/**
 * @brief Lightweight wrapper so Python can do: agent.Train().train()
 */
struct Train {

    /**
     * @brief Train the snake agent using Q-learning.
     */
    void train();
};


#endif