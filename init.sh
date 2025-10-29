#!/usr/bin/env bash

VENV_DIR=".venv"
REQ_FILE="requirements.txt"

die() { echo "ERROR: $*" >&2; exit 1; }

if [[ ! -f "setup.py" && ! -f "pyproject.toml" ]]; then
  die "Run this from the project root (setup.py or pyproject.toml required)."
fi


if [[ ! -d "$VENV_DIR" ]]; then
  echo ">> Creating virtualenv: $VENV_DIR"
  python -m venv "$VENV_DIR"
else
  echo ">> Using existing virtualenv: $VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo ">> Upgrading pip, setuptools, wheel"
python -m pip install --upgrade pip setuptools wheel

if [[ -f "$REQ_FILE" ]]; then
  echo ">> Installing requirements from $REQ_FILE"
  python -m pip install -r "$REQ_FILE"
else
  echo ">> No requirements.txt found; skipping"
fi

echo ">> Building and installing the agent extension (editable)"
python -m pip install -e .