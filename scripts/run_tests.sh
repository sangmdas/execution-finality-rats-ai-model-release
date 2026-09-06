#!/usr/bin/env sh
set -eu
PYTHONPATH="${PYTHONPATH:-}:src" python -m unittest discover -s tests -v
