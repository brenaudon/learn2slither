/*!
 *  @file learn2slither.cpp
 *  @brief Pybind11 bindings and engine for the Learn2Slither project.
 *
 *  This module exposes a C++ "Engine" to Python, so the Python front-end can:
 *    - reset the board,
 *    - move the snake forward one step,
 *    - change the direction safely (no instant reversal into the neck),
 *    - fetch the current board snapshot (snake, apples, flags).
 *
 */

#include "include/learn2slither.hpp"
#include "include/engine.hpp"
#include "include/train.hpp"


/**
 * @brief Pybind11 module definition.
 *
 * Exposes:
 *   - reset_board(grid:int)
 *   - change_dir(new_dir: Engine.Dir)
 *   - step_forward()
 *   - get_board() -> dict
 *   - train()
 */
PYBIND11_MODULE(_agent, m) {
    m.doc() = "Learn2Slither C++ agent exposed to Python via pybind11";

    py::class_<Engine>(m, "Engine")
        .def(py::init<>())
        .def("reset_board", &Engine::reset_board, py::arg("grid"))
        .def("step_forward", &Engine::step_forward)
        .def("change_dir", &Engine::change_dir, py::arg("new_dir"))
        .def("get_board", &Engine::get_board);

    py::class_<Train>(m, "Train")
        .def(py::init<>())
        .def("train", &Train::train);
}
