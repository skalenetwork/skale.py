#!/usr/bin/env bash

set -ea

python -m pip install --upgrade pip
pip install -e .
pip install -e .[dev]
pip install codecov pytest-cov
pip install git+git://github.com/skalenetwork/sgx.py.git@add-python-3.11-support#egg=sgx.py
