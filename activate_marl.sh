#!/usr/bin/env bash

source ".venv/bin/activate"
export MPLCONFIGDIR="${PWD}/.mplconfig"
export UV_CACHE_DIR="${PWD}/.uv-cache"
export UV_PYTHON_INSTALL_DIR="${PWD}/.uv-python"
export PYTHONPATH="${PWD}/src${PYTHONPATH:+:${PYTHONPATH}}"
