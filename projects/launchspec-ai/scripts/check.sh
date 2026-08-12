#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

npm run test
npm run lint
npm run build
git diff --check

SECRET_PATTERN='sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|glpat-[A-Za-z0-9_-]{20,}|-----BEGIN (OPENSSH|RSA|DSA|EC|PRIVATE) PRIVATE KEY-----'
if rg -n --hidden \
  --glob '!.git/**' \
  --glob '!node_modules/**' \
  --glob '!.next/**' \
  --glob '!.env*' \
  "$SECRET_PATTERN" .; then
  echo "possible secret detected; remove it before committing" >&2
  exit 1
fi

echo "check: passed"
