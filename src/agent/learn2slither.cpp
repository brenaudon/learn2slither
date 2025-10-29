#include <pybind11/pybind11.h>
#include <pybind11/stl.h>      // std::vector, std::pair, std::array -> Python lists/tuples
#include <pybind11/functional.h>
#include <fstream>
#include <random>
#include <unordered_map>
#include <array>
#include <string>

namespace py = pybind11;

struct Env {
    // --- config / params
    int grid = 10;
    double alpha = 0.1, gamma = 0.95, epsilon = 0.1;
    std::mt19937 rng{123};

    // --- board state
    std::vector<std::pair<int,int>> snake;    // head first
    std::vector<std::pair<int,int>> greens;   // 2 greens
    std::pair<int,int> red{7,7};
    std::string head_dir = "UP";
    bool learning = true;

    // --- (optional) Q-table placeholder (hash-> 4 actions)
    // using a simple map: key is packed state, value is Q for [UP,RIGHT,DOWN,LEFT]
    std::unordered_map<uint64_t, std::array<double,4>> Q;

    Env() { reset(10, 123); }

    // helpers
    std::pair<int,int> add_wrap(std::pair<int,int> p, int dx, int dy) const {
        int x = (p.first  + dx + grid) % grid;
        int y = (p.second + dy + grid) % grid;
        return {x, y};
    }

    void reset(int g, int seed=0) {
        grid = g;
        rng.seed(seed ? seed : 123);
        head_dir = "UP";
        snake.clear();
        int cx = grid/2, cy = grid/2;
        snake.push_back({cx, cy});
        snake.push_back({cx, cy+1});
        snake.push_back({cx, cy+2});

        greens = {{2,3},{grid-2,1}};
        red = {grid-3, grid-3};
    }

    // very small “movement” (no collisions/eating yet—fill in your logic)
    void step(py::object human_action = py::none()) {
        if (!human_action.is_none()) {
            std::string a = human_action.cast<std::string>();
            if (a=="UP"||a=="DOWN"||a=="LEFT"||a=="RIGHT") head_dir = a;
        }
        int dx = (head_dir=="RIGHT")-(head_dir=="LEFT");
        int dy = (head_dir=="DOWN") -(head_dir=="UP");
        auto new_head = add_wrap(snake.front(), dx, dy);
        snake.insert(snake.begin(), new_head);
        snake.pop_back();
        // Here you would compute reward r, next state s', update Q(s,a) with Q-learning
        // and respawn apples, check game over, etc.
    }

    // return data in Python-native shapes
    py::dict get_board() const {
        py::dict b;
        b["snake"]  = snake;          // list of (x,y) tuples
        b["greens"] = greens;         // list of (x,y)
        b["red"]    = py::make_tuple(red.first, red.second); // (x,y) or None in your logic
        return b;
    }

    void set_config(double a, double g, double e, bool learn=true) {
        alpha = a; gamma = g; epsilon = e; learning = learn;
    }

    // stub save/load to show the pattern; replace with your real Q-table model IO
    void save_model(const std::string& path) const {
        std::ofstream out(path);
        if (!out) throw std::runtime_error("Cannot open: " + path);
        out << "grid " << grid << "\n";
        out << "alpha " << alpha << " gamma " << gamma << " epsilon " << epsilon << "\n";
        // dump Q size to prove we did something
        out << "qsize " << Q.size() << "\n";
    }

    void load_model(const std::string& path) {
        std::ifstream in(path);
        if (!in) throw std::runtime_error("Cannot open: " + path);
        std::string k;
        in >> k >> grid; // "grid N"
        std::string k2; double a,g,e;
        in >> k >> a >> k2 >> g >> k >> e; // "alpha a gamma g epsilon e"
        set_config(a,g,e,learning);
        // you would also restore Q here
    }
};

PYBIND11_MODULE(_agent, m) {
    m.doc() = "Learn2Slither C++ agent exposed to Python via pybind11";

    py::class_<Env>(m, "Env")
        .def(py::init<>())
        // release the GIL during heavy work to keep Python UI responsive
        .def("reset", &Env::reset, py::arg("grid"), py::arg("seed")=0,
             py::call_guard<py::gil_scoped_release>())
        .def("step",  &Env::step,  py::arg("human_action")=py::none(),
             py::call_guard<py::gil_scoped_release>())
        .def("get_board", &Env::get_board)
        .def("set_config", &Env::set_config, py::arg("alpha"), py::arg("gamma"),
             py::arg("epsilon"), py::arg("learn")=true)
        .def("save_model", &Env::save_model)
        .def("load_model", &Env::load_model)
        .def_readwrite("head_dir", &Env::head_dir)
        .def_readwrite("learning", &Env::learning)
        .def_readonly("grid", &Env::grid);
}
