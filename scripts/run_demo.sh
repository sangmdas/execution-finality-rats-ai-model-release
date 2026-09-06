#!/usr/bin/env sh
set -eu
PYTHONPATH="${PYTHONPATH:-}:src" python -m execution_finality.demo
