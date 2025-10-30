#ifndef LEARN2SLITHER_HPP
#define LEARN2SLITHER_HPP

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <random>

namespace py = pybind11;

enum MOVE_RESULT {
    MOVE_OK,
    MOVE_COLLISION,
    MOVE_RED_APPLE,
    MOVE_GREEN_APPLE
};

#endif