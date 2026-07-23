#!/usr/bin/env bash
set -euo pipefail

echo "== python tests =="
python -m pytest -q

echo "== python syntax =="
python -m compileall -q app tests

echo "== whitespace check =="
git diff --check

echo "local checks passed"
