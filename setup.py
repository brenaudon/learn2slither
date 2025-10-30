from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "agent._agent", # import name: `import agent`
        ["src/agent/learn2slither.cpp", "src/agent/engine.cpp"],
        cxx_std=17, # use C++17
        define_macros=[("PYBIND11_DETAILED_ERROR_MESSAGES", "1")],
    ),
]

setup(
    name="learn2slither-agent",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
