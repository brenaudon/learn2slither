/*!
 *  @file engine.cpp
 *  @brief Engine for the Learn2Slither project.
 *
 *  The engine implements the project’s board rules:
 *    - Grid with two green apples and one red apple.
 *    - Snake of length 3 at start, contiguous, placed randomly.
 *    - Moving into a wall or itself => game over.
 *    - Eating green => grow by +1 and respawn a green.
 *    - Eating red => shrink by 1 and respawn the red.
 */

#include "include/engine.hpp"
#include <fstream>
#include <random>
#include <unordered_map>
#include <array>
#include <string>
#include <stdbool.h>
#include <iostream>



/**
 * @brief Return the opposite of a given direction.
 *
 * @param d Input direction.
 * @return The opposite direction (or NONE for NONE).
 */
static inline Dir opposite(Dir d) {
    switch (d) {
        case Dir::UP: return Dir::DOWN;
        case Dir::DOWN: return Dir::UP;
        case Dir::LEFT: return Dir::RIGHT;
        case Dir::RIGHT: return Dir::LEFT;
        default: return Dir::NONE;
    }
}

/**
 * @brief Convert a Dir enum value to a string.
 *
 * @param d Input direction.
 * @return Corresponding string representation.
 */
static inline const char* to_str(Dir d) {
    switch (d) {
        case Dir::UP: return "UP";
        case Dir::DOWN: return "DOWN";
        case Dir::LEFT: return "LEFT";
        case Dir::RIGHT: return "RIGHT";
        default: return "NONE";
    }
}

/**
 * @brief Convert a string to a Dir enum value.
 *
 * @param s Input string.
 * @return Corresponding Dir value (or NONE if unrecognized).
 */
static inline Dir from_str(const std::string& s) {
    if (s == "UP") return Dir::UP;
    if (s == "DOWN") return Dir::DOWN;
    if (s == "LEFT") return Dir::LEFT;
    if (s == "RIGHT") return Dir::RIGHT;
    return Dir::NONE;
}

/**
 * @brief 2D vector (dx,dy) corresponding to a direction.
 *
 * @param d Direction.
 * @return Pair of delta (dx, dy).
 */
static inline std::pair<int,int> vec(Dir d) {
    switch (d) {
        case Dir::UP: return {0, -1};
        case Dir::DOWN: return {0, 1};
        case Dir::LEFT: return {-1, 0};
        case Dir::RIGHT: return {1, 0};
        default: return {0, 0};
    }
}


Engine::Engine(): rng_engine(42) {
    reset_board(10);
}

Dir Engine::get_neck_dir(const std::vector<std::pair<int,int>>& snake) {
    if (snake.size() < 2) return Dir::NONE;
    int hx = snake[0].first;
    int hy = snake[0].second;
    int nx = snake[1].first;
    int ny = snake[1].second;
    int dx = nx - hx;
    int dy = ny - hy;
    if (dx ==  0 && dy == -1) return Dir::UP;
    if (dx ==  0 && dy ==  1) return Dir::DOWN;
    if (dx == -1 && dy ==  0) return Dir::LEFT;
    if (dx ==  1 && dy ==  0) return Dir::RIGHT;
    return Dir::NONE;
}

void Engine::reset_board(int grid_size) {
    grid = grid_size;

    snake.clear();
    greens.clear();
    red = {-1, -1};
    game_over = false;

    // place snake
    std::pair<int,int> head{0, 0};
    do {
        head.first = rng_engine() % grid;
        head.second = rng_engine() % grid;
    } while (std::find(greens.begin(), greens.end(), head) != greens.end()
            || head == red);
    snake.push_back(head);
    for (int i = 0; i < 2; ++i) {
        std::pair<int,int> segment{0, 0};
        std::pair<int,int> prev = snake.back();
        do {
            segment.first = prev.first;
            segment.second = prev.second;
            int dir = rng_engine() % 4;
            switch (dir) {
                case 0: segment.second -= 1; break; // UP
                case 1: segment.second += 1; break; // DOWN
                case 2: segment.first -= 1; break; // LEFT
                case 3: segment.first += 1; break; // RIGHT
            }
        } while (std::find(snake.begin(), snake.end(), segment) != snake.end());
        snake.push_back(segment);
    }

    // place green apples
    for (int i = 0; i < 2; ++i) {
        std::pair<int,int> green{0, 0};
        do {
            green.first = rng_engine() % grid;
            green.second = rng_engine() % grid;
        } while (std::find(greens.begin(), greens.end(), green) != greens.end() ||
                std::find(snake.begin(), snake.end(), green) != snake.end());
        greens.push_back(green);
    }

    // place red apple
    do {
        red.first = rng_engine() % grid;
        red.second = rng_engine() % grid;
    } while (std::find(greens.begin(), greens.end(), red) != greens.end() ||
            std::find(snake.begin(), snake.end(), red) != snake.end());

    head_dir = opposite(get_neck_dir(snake));

    head = snake.front();
    auto [dx, dy] = vec(head_dir);
    int nx = head.first + dx;
    int ny = head.second + dy;

    while (nx < 0 || nx >= grid || ny < 0 || ny >= grid ||
            std::find(snake.begin(), snake.end(), std::make_pair(nx, ny)) != snake.end()) {
        head_dir = static_cast<Dir>((static_cast<int>(head_dir) + 1) % 4);
        std::tie(dx, dy) = vec(head_dir);
        nx = head.first + dx;
        ny = head.second + dy;
    }
}


MOVE_RESULT Engine::step_forward(bool printing) {
    if (game_over) return MOVE_RESULT::MOVE_COLLISION;

    const int N = grid;
    const auto [dx, dy] = vec(head_dir);
    const int hx = snake[0].first;
    const int hy = snake[0].second;
    const int nx = hx + dx;
    const int ny = hy + dy;

    // collision (wall or self)
    if (nx < 0 || nx >= N || ny < 0 || ny >= N ||
        std::find(snake.begin(), snake.end(), std::make_pair(nx, ny)) != snake.end()) {
        game_over = true;
        return MOVE_RESULT::MOVE_COLLISION;
    }

    // eat green -> grow
    auto itg = std::find(greens.begin(), greens.end(), std::make_pair(nx, ny));
    if (itg != greens.end()) {
        // remove eaten one
        greens.erase(itg);
        // spawn new green not on snake or other green (unless grid full)
        if ((int)snake.size() != N * N) {
            std::pair<int,int> green{0,0};
            do {
                green.first = rng_engine() % grid;
                green.second = rng_engine() % grid;
            } while (std::find(greens.begin(), greens.end(), green) != greens.end() ||
                    std::find(snake.begin(), snake.end(), green) != snake.end() ||
                    green == red);
            greens.push_back(green);
        }
        // grow: new head + keep all segments
        std::vector<std::pair<int,int>> newsnake;
        newsnake.emplace_back(nx, ny);
        newsnake.insert(newsnake.end(), snake.begin(), snake.end());
        snake.swap(newsnake);
        if (printing) print_head_vision();
        return MOVE_RESULT::MOVE_GREEN_APPLE;
    }

    // eat red -> shrink
    if (red == std::make_pair(nx, ny)) {
        if ((int)snake.size() == 1) {
            game_over = true;
            return MOVE_RESULT::MOVE_RED_APPLE;
        }
        // respawn red not on greens/snake (unless grid full)
        do {
            red.first = rng_engine() % grid;
            red.second = rng_engine() % grid;
        } while (std::find(greens.begin(), greens.end(), red) != greens.end() ||
                std::find(snake.begin(), snake.end(), red) != snake.end());
        // shrink: new head + drop last 2 segments
        std::vector<std::pair<int,int>> newsnake;
        newsnake.emplace_back(nx, ny);
        if (snake.size() >= 2) {
            newsnake.insert(newsnake.end(), snake.begin(), snake.end() - 2);
        }
        snake.swap(newsnake);
        if (printing) print_head_vision();
        return MOVE_RESULT::MOVE_RED_APPLE;
    }

    // normal move: new head + drop tail
    {
        std::vector<std::pair<int,int>> newsnake;
        newsnake.emplace_back(nx, ny);
        newsnake.insert(newsnake.end(), snake.begin(), snake.end() - 1);
        snake.swap(newsnake);
        if (printing) print_head_vision();
        return MOVE_RESULT::MOVE_OK;
    }
}


void Engine::change_dir(const std::string& new_dir_s) {
    Dir new_dir = from_str(new_dir_s);
    Dir neck = get_neck_dir(snake);
    if (new_dir != neck && new_dir != Dir::NONE) {
        head_dir = new_dir;
    }
}


py::dict Engine::get_board() const {
    py::dict b;
    b["snake"] = snake; // list of (x,y) tuples
    b["greens"] = greens; // list of (x,y)
    b["red"] = py::make_tuple(red.first, red.second); // (x,y) or None in your logic
    b["head_dir"] = to_str(head_dir);
    b["game_over"] = game_over;
    return b;
}


std::vector<std::string> Engine::get_head_vision() {
    std::pair<int,int> head = snake[0];
    std::vector<std::string> vision;
    for (Dir d : {Dir::UP, Dir::RIGHT, Dir::DOWN, Dir::LEFT}) {
        auto [dx, dy] = vec(d);
        int x = head.first;
        int y = head.second;
        std::string cell_contents = "";
        while (true) {
            x += dx;
            y += dy;
            if (x < 0 || x >= grid || y < 0 || y >= grid) {
                cell_contents += "W";
                break;
            }
            std::pair<int,int> pos{x, y};
            if (std::find(snake.begin(), snake.end(), pos) != snake.end()) {
                cell_contents += "S";
            } else if (std::find(greens.begin(), greens.end(), pos) != greens.end()) {
                cell_contents += "G";
            } else if (red == pos) {
                cell_contents += "R";
            } else {
                cell_contents += "0";
            }
        }
        vision.push_back(cell_contents);
    }
    return vision;
}


void Engine::print_head_vision() {
    auto vision = get_head_vision();
    const size_t left_len = vision[3].length();
    const size_t up_len = vision[0].length();
    for (int i = (int)up_len - 1; i >= 0; i--) {
        std::string line(left_len, ' ');
        line += vision[0][i];
        std::cout << line << std::endl;
    }
    std::reverse(vision[3].begin(), vision[3].end());
    std::cout << vision[3] << "H" << vision[1] << std::endl;
    for (size_t i = 0; i < vision[2].length(); ++i) {
        std::string line(left_len, ' ');
        line += vision[2][i];
        std::cout << line << std::endl;
    }
    std::cout << std::endl;
}