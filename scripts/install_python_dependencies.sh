#!/usr/bin/env bash

set -ea

python -m pip install --upgrade pip
pip install -e .
pip install -e .[dev]
pip install codecov pytest-cov
