#include <pybind11/pybind11.h>
#include <pybind11/stl.h>      // std::vector, std::pair, std::array -> Python lists/tuples
#include <pybind11/functional.h>
#include <fstream>
#include <random>
#include <unordered_map>
#include <array>
#include <string>
#include <stdbool.h>

namespace py = pybind11;

enum class Dir { UP, DOWN, LEFT, RIGHT, NONE };

static inline Dir opposite(Dir d) {
    switch (d) {
        case Dir::UP: return Dir::DOWN;
        case Dir::DOWN: return Dir::UP;
        case Dir::LEFT: return Dir::RIGHT;
        case Dir::RIGHT: return Dir::LEFT;
        default: return Dir::NONE;
    }
}

static inline const char* to_str(Dir d) {
    switch (d) {
        case Dir::UP: return "UP";
        case Dir::DOWN: return "DOWN";
        case Dir::LEFT: return "LEFT";
        case Dir::RIGHT: return "RIGHT";
        default: return "NONE";
    }
}

static inline Dir from_str(const std::string& s) {
    if (s == "UP") return Dir::UP;
    if (s == "DOWN") return Dir::DOWN;
    if (s == "LEFT") return Dir::LEFT;
    if (s == "RIGHT") return Dir::RIGHT;
    return Dir::NONE;
}

static inline std::pair<int,int> vec(Dir d) {
    switch (d) {
        case Dir::UP: return {0, -1};
        case Dir::DOWN: return {0, 1};
        case Dir::LEFT: return {-1, 0};
        case Dir::RIGHT: return {1, 0};
        default: return {0, 0};
    }
}

struct Engine {
    // --- config / params
    int grid = 10;

    // --- board state
    std::vector<std::pair<int,int>> snake; // head first
    std::vector<std::pair<int,int>> greens; // 2 greens
    std::pair<int,int> red{-1, -1}; // red apple or (-1,-1) if none
    Dir head_dir = Dir::UP;
    bool game_over = false;

    std::mt19937 rng;

    Engine()
     : rng(static_cast<unsigned>(
               std::chrono::high_resolution_clock::now().time_since_epoch().count())) {
        reset_board(10);
    }

    static Dir get_neck_dir(const std::vector<std::pair<int,int>>& snake) {
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

    void reset_board(int grid_size) {
        grid = grid_size;

        snake.clear();
        greens.clear();
        red = {-1, -1};
        game_over = false;

        // place green apples
        for (int i = 0; i < 2; ++i) {
            std::pair<int,int> green{0, 0};
            do {
                green.first = rng() % grid;
                green.second = rng() % grid;
            } while (std::find(greens.begin(), greens.end(), green) != greens.end());
            greens.push_back(green);
        }

        // place red apple
        do {
            red.first = rng() % grid;
            red.second = rng() % grid;
        } while (std::find(greens.begin(), greens.end(), red) != greens.end());

        // place snake
        std::pair<int,int> head{0, 0};
        do {
            head.first = rng() % grid;
            head.second = rng() % grid;
        } while (std::find(greens.begin(), greens.end(), head) != greens.end()
                || head == red);
        snake.push_back(head);
        for (int i = 0; i < 2; ++i) {
            std::pair<int,int> segment{0, 0};
            std::pair<int,int> prev = snake.back();
            do {
                segment.first = prev.first;
                segment.second = prev.second;
                int dir = rng() % 4;
                switch (dir) {
                    case 0: segment.second -= 1; break; // UP
                    case 1: segment.second += 1; break; // DOWN
                    case 2: segment.first -= 1; break; // LEFT
                    case 3: segment.first += 1; break; // RIGHT
                }
            } while (std::find(snake.begin(), snake.end(), segment) != snake.end()
                    || std::find(greens.begin(), greens.end(), segment) != greens.end()
                    || segment == red);
            snake.push_back(segment);
        }

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


    void step_forward() {
        if (game_over) return;

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
            return;
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
                    green.first = rng() % grid;
                    green.second = rng() % grid;
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
            return;
        }

        // eat red -> shrink
        if (red == std::make_pair(nx, ny)) {
            if ((int)snake.size() == 1) {
                game_over = true;
                return;
            }
            // respawn red not on greens/snake (unless grid full)
            do {
                red.first = rng() % grid;
                red.second = rng() % grid;
            } while (std::find(greens.begin(), greens.end(), red) != greens.end() ||
                    std::find(snake.begin(), snake.end(), red) != snake.end());
            // shrink: new head + drop last 2 segments
            std::vector<std::pair<int,int>> newsnake;
            newsnake.emplace_back(nx, ny);
            if (snake.size() >= 2) {
                newsnake.insert(newsnake.end(), snake.begin(), snake.end() - 2);
            }
            snake.swap(newsnake);
            return;
        }

        // normal move: new head + drop tail
        {
            std::vector<std::pair<int,int>> newsnake;
            newsnake.emplace_back(nx, ny);
            newsnake.insert(newsnake.end(), snake.begin(), snake.end() - 1);
            snake.swap(newsnake);
        }
    }

    void change_dir(std::string& new_dir_s) {
        Dir new_dir = from_str(new_dir_s);
        Dir neck = get_neck_dir(snake);
        if (new_dir != neck && new_dir != Dir::NONE) {
            head_dir = new_dir;
        }
    }

    // return data in Python-native shapes
    py::dict get_board() const {
        py::dict b;
        b["snake"] = snake; // list of (x,y) tuples
        b["greens"] = greens; // list of (x,y)
        b["red"] = py::make_tuple(red.first, red.second); // (x,y) or None in your logic
        b["head_dir"] = to_str(head_dir);
        b["game_over"] = game_over;
        return b;
    }
};

PYBIND11_MODULE(_agent, m) {
    m.doc() = "Learn2Slither C++ agent exposed to Python via pybind11";

    py::class_<Engine>(m, "Engine")
        .def(py::init<>())
        // release the GIL during heavy work to keep Python UI responsive
        .def("reset_board", &Engine::reset_board, py::arg("grid"),
             py::call_guard<py::gil_scoped_release>())
        .def("step_forward", &Engine::step_forward,
             py::call_guard<py::gil_scoped_release>())
        .def("change_dir", &Engine::change_dir, py::arg("new_dir"))
        .def("get_board", &Engine::get_board);
}
