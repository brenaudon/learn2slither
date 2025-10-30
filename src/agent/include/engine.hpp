#ifndef ENGINE_HPP
#define ENGINE_HPP

#include "learn2slither.hpp"

/**
 * @enum Dir
 * @brief Cardinal directions for the snake head.
 *
 * The NONE value is used as a sentinel where a direction is not applicable.
 */
enum class Dir { UP, DOWN, LEFT, RIGHT, NONE };

/**
 * @brief Engine implementing the Learn2Slither board logic.
 *
 * Fields are intentionally public to keep the implementation straightforward; use the
 * member functions to mutate state safely.
 */
struct Engine {
    int grid = 10; ///< Current grid size (width==height==grid).

    // board state
    std::vector<std::pair<int,int>> snake;  ///< Snake body, head first.
    std::vector<std::pair<int,int>> greens; ///< Two green apples.
    std::pair<int,int> red{-1, -1};         ///< Red apple (or (-1,-1) if absent).
    Dir head_dir = Dir::UP;                 ///< Current head direction.
    bool game_over = false;                 ///< Game over flag.

    std::mt19937 rng_engine;  ///< Random number generator.

    /**
     * @brief Construct the engine and initialize a 10×10 board.
     *
     * Seeds RNG from high-resolution clock.
     */
    Engine();

    /**
     * @brief Get direction from head to neck (used to forbid instant reverse).
     *
     * @param snake Body with head at index 0.
     * @return Dir toward the neck, or NONE if snake length < 2.
     */
    static Dir get_neck_dir(const std::vector<std::pair<int,int>>& snake);


    /**
     * @brief Reset the board to a fresh random state.
     *
     * Rules:
     *  - place two distinct green apples and one red apple,
     *  - place a contiguous 3-cell snake not colliding with apples,
     *  - set head_dir opposite to neck direction,
     *  - ensure the very first forward move does not immediately collide.
     *
     * @param g New grid size.
     */
    void reset_board(int grid_size);

    /**
     * @brief Move the snake forward one step according to current head_dir.
     *
     * Handles collisions, eating green/red apples, growing/shrinking.
     * Sets game_over flag if the move results in a collision or invalid state.
     */
    MOVE_RESULT step_forward(bool printing = true);

    /**
     * @brief Change the snake's head direction safely.
     *
     * Prevents instant reversal into the neck segment.
     *
     * @param new_dir_s New direction as a string ("UP", "DOWN", "LEFT", "RIGHT").
     */
    void change_dir(const std::string& new_dir_s);

    /**
     * @brief Get the current board state as a Python dictionary.
     *
     * The dictionary contains:
     *  - "snake": list of (x,y) tuples for the snake body,
     *  - "greens": list of (x,y) tuples for green apples,
     *  - "red": (x,y) tuple for red apple,
     *  - "head_dir": string for head direction,
     *  - "game_over": boolean flag.
     *
     * @return Python dictionary representing the board state.
     */
    py::dict get_board() const;

    /**
     * @brief Get the contents of the line of cells in the four cardinal directions from the head.
     *
     * For each direction (UP, RIGHT, DOWN, LEFT), returns a string indicating
     * what is in line of this direction until a wall is hit:
     *  - "0" is an empty cell,
     *  - "W" is a wall,
     *  - "S" is the snake's body,
     *  - "G" is a green apple,
     *  - "R" is the red apple,
     *
     * @return Vector of strings for each direction in order: UP, RIGHT, DOWN, LEFT.
     */
    std::vector<std::string> get_head_vision();

    /**
     * @brief Print the head vision in a formatted way.
     *
     * Displays the contents in the four cardinal directions from the head.
     */
    void print_head_vision();

};

#endif