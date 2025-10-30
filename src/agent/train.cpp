#include "include/train.hpp"
#include <unordered_map>
#include <array>
#include <cstdint>


std::mt19937 rng {std::random_device{}()}; //< Global random number generator

/**
 * @struct State
 * @brief Data structure for training the snake agent.
 *
 * Contains sensory inputs about dangers and food in all four directions,
 * as well as the nearest green food direction.
 */
struct State {
    // Distances to walls / body / food in 4 directions
    // 0 = none, 1 = distance 1, 2 = distance 2-3, 3 = distance 4-7, 4 = distance 8+
    uint8_t danger_up, danger_down, danger_left, danger_right;
    uint8_t green_up, green_down, green_left, green_right;
    uint8_t red_up, red_down, red_left, red_right;
    uint8_t nearest_green_dir; // 0..4 (none, up, right, down, left)
    uint8_t nearest_green_dist; // 0 = none, 1 = distance 1, 2 = distance 2-3, 3 = distance 4-7, 4 = distance 8+

    State(std::vector<std::string> head_vision) {
        uint8_t snake_up = string_analyze(head_vision[0], 'S');
        uint8_t snake_right = string_analyze(head_vision[1], 'S');
        uint8_t snake_down = string_analyze(head_vision[2], 'S');
        uint8_t snake_left = string_analyze(head_vision[3], 'S');

        uint8_t wall_up = string_analyze(head_vision[0], 'W');
        uint8_t wall_right = string_analyze(head_vision[1], 'W');
        uint8_t wall_down = string_analyze(head_vision[2], 'W');
        uint8_t wall_left = string_analyze(head_vision[3], 'W');

        danger_up = std::min(snake_up, wall_up);
        danger_right = std::min(snake_right, wall_right);
        danger_down = std::min(snake_down, wall_down);
        danger_left = std::min(snake_left, wall_left);

        green_up = string_analyze(head_vision[0], 'G');
        green_right = string_analyze(head_vision[1], 'G');
        green_down = string_analyze(head_vision[2], 'G');
        green_left = string_analyze(head_vision[3], 'G');

        red_up = string_analyze(head_vision[0], 'R');
        red_right = string_analyze(head_vision[1], 'R');
        red_down = string_analyze(head_vision[2], 'R');
        red_left = string_analyze(head_vision[3], 'R');

        // Nearest green direction
        nearest_green_dir = 0;
        nearest_green_dist = 15;
        for (int dir = 0; dir < 4; ++dir) {
            int dist = string_analyze(head_vision[dir], 'G');
            if (dist > 0 && dist < nearest_green_dist) {
                nearest_green_dist = dist;
                nearest_green_dir = dir + 1; // +1 to make room for "none" = 0
                break;
            }
        }
    }

    static uint8_t string_analyze(const std::string& s, char target) {
        for (size_t i = 0; i < s.size(); ++i) {
            if (s[i] == target) {
                if (i == 0) return 1;
                else if (i <= 2) return 2;
                else if (i <= 6) return 3;
                else return 4;
            }
        }
        return 0;
    }

    uint64_t pack() const {
        auto pack4 = [](uint8_t v)->uint64_t { return (uint64_t)(v & 0xF); };

        uint64_t x = 0;
        auto push = [&](uint8_t v){ x = (x << 4) | pack4(v); };

        // order is arbitrary but must be consistent:
        push(danger_up); push(danger_down); push(danger_left); push(danger_right);
        push(green_up); push(green_down); push(green_left); push(green_right);
        push(red_up); push(red_down); push(red_left); push(red_right);
        push(nearest_green_dir);

        return x;
    }

    bool operator==(const State& o) const { return pack() == o.pack(); }
};

/**
 * @struct StateHash
 * @brief Hash function for State to be used in unordered containers.
 */
struct StateHash {
  size_t operator()(State const& s) const noexcept {
    return std::hash<uint64_t>{}(s.pack());
  }
};


using QValues = std::array<int,4>;
using QTable  = std::unordered_map<State, QValues, StateHash>;


/**
 * @brief Get a reference to the Q-values for a given state, inserting default if missing.
 *
 * @param Q Q-table mapping states to Q-values.
 * @param s State for which to retrieve the Q-values.
 * @return Reference to the Q-values array for the state.
 */
inline QValues& qref(QTable& Q, const State& s) {
    auto it = Q.find(s);
    if (it == Q.end()) it = Q.emplace(s, QValues{0,0,0,0}).first;
    return it->second;
}

inline int argmax4(const QValues& q) {
    std::vector<int> best = {0};
    for (int i = 1; i < 4; ++i) {
        if (q[i] > q[best[0]])
            best[0] = i;
        else if (q[i] == q[best[0]])
            best.push_back(i);
    }
    if (best.size() == 1)
        return best[0];
    std::uniform_int_distribution<int> Bi(0, (int)best.size() - 1);
    int idx = Bi(rng);
    return best[idx];
}

inline int move_choice(QTable& Q, const State& s, double eps) {
    std::uniform_real_distribution<double> u(0.0, 1.0);
    if (u(rng) < eps) {
        std::uniform_int_distribution<int> random_act(0,3);
        return random_act(rng);
    }
    return argmax4(qref(Q, s));
}

// One-step Q-learning update: Q(s,a) ← Q(s,a) + α [ r + γ max_a' Q(s',a') − Q(s,a) ]
inline void q_update(QTable& Q,
                     const State& s, int a, double r,
                     const State& s2, bool done,
                     double alpha, double gamma) {
    QValues& q = qref(Q, s);
    double qsa = q[a];

    double target;
    if (done) {
        target = r;
    } else {
        const QValues& q2 = qref(Q, s2);
        target = r + gamma * *std::max_element(q2.begin(), q2.end());
    }
    q[a] = qsa + alpha * (target - qsa);
}

struct StepResult {
    State s2;
    double r;
    bool done;
};

// Map action index -> your engine’s direction
inline void apply_action(Engine& env, int a) {
    switch (a) {
        case 0: env.change_dir("UP"); break;
        case 1: env.change_dir("RIGHT"); break;
        case 2: env.change_dir("DOWN"); break;
        case 3: env.change_dir("LEFT"); break;
    }
}

inline StepResult env_step(Engine& env, int a) {
    apply_action(env, a);

    State s = State(env.get_head_vision());

    MOVE_RESULT move_res = env.step_forward(false);

    State s2 = State(env.get_head_vision());

    double r;
    switch (move_res) {
        case MOVE_RESULT::MOVE_OK:
            if (s2.nearest_green_dist < s.nearest_green_dist && s2.nearest_green_dist > 0) {
                r = +5.0; // getting closer to green apple
            } else {
                r = -0.1; // small penalty for normal move
            }
            break;
        case MOVE_RESULT::MOVE_COLLISION:
            r = -100.0;
            break;
        case MOVE_RESULT::MOVE_RED_APPLE:
            r = -30.0;
            break;
        case MOVE_RESULT::MOVE_GREEN_APPLE:
            r = +50.0;
            break;
        default:
            r = -1.0;
    }

    return { s2, r, env.game_over };
}

inline void train_logic(QTable& Q, int episodes,
           double alpha, double gamma,
           double eps_start, double eps_end,
           Engine& env, int grid) {

    int best_len = 0;

    double eps = eps_start;

    for (int ep = 0; ep < episodes; ++ep) {
        if (ep % 100 == 0) {
            printf("Episode %d / %d\n", ep, episodes);
        }

        env.reset_board(grid);

        State s = State(env.get_head_vision());

        int steps = 0;
        const int max_steps = 10000; // safety cap per episode

        while (!env.game_over && steps++ < max_steps) {
            // choose action
            int a = move_choice(Q, s, eps);

            // step env
            StepResult tr = env_step(env, a);

            // Q update
            q_update(Q, s, a, tr.r, tr.s2, tr.done, alpha, gamma);

            // advance
            s = tr.s2;
        }
        best_len = std::max(best_len, (int)env.snake.size());
        if (ep % 1000 == 0) {
            printf("  Best snake length so far: %d\n", best_len);
        }

        eps = eps == eps_end ? eps_end : eps * 0.995; // decay epsilon
    }
}


void Train::train() {
    QTable Q;

    Engine env;
    int grid = 10;

    double alpha = 0.6, gamma = 0.85;
    double eps0 = 0.9, epsf = 0.001;

    train_logic(Q, 20000, alpha, gamma, eps0, epsf, env, grid);

    for (int test_run = 0; test_run < 5; ++test_run) {
        env.reset_board(grid);
        State s = State(env.get_head_vision());
        while (!env.game_over) {
            int a = move_choice(Q, s, 0.0); // no exploration
            apply_action(env, a);
            env.step_forward(false);
            s = State(env.get_head_vision());
        }
        int len_snake = (int)env.snake.size();
        printf("Training %d complete. Final snake length in test run: %d\n", test_run, len_snake);
    }
}
