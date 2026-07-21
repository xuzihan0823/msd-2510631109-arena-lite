#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PORT="${PORT:-3012}"
BASE_URL="http://127.0.0.1:${PORT}"
EVIDENCE_DIR="evidence/local-uat"
mkdir -p "$EVIDENCE_DIR"
STATUS_LOG="$EVIDENCE_DIR/uat-status.txt"
SERVER_LOG="$EVIDENCE_DIR/uat-server.log"
: > "$STATUS_LOG"

npm run dev -- --hostname 127.0.0.1 --port "$PORT" > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!
cleanup() {
  kill "$SERVER_PID" 2>/dev/null || true
  wait "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 30); do
  if curl -fsS "$BASE_URL/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

assert_status() {
  local label="$1"
  local expected="$2"
  local body_file="$3"
  shift 3
  local actual
  actual="$(curl -sS -o "$body_file" -w '%{http_code}' "$@")"
  printf '%s=%s\n' "$label" "$actual" | tee -a "$STATUS_LOG"
  test "$actual" = "$expected"
}

assert_status health 200 "$EVIDENCE_DIR/health.json" "$BASE_URL/api/health"
assert_status invalid_project 400 "$EVIDENCE_DIR/invalid-project.json" \
  -X POST "$BASE_URL/api/projects" \
  -H 'Content-Type: application/json' \
  -d '{"name":"x","idea":"too short"}'
assert_status create_project 201 "$EVIDENCE_DIR/create-project.json" \
  -X POST "$BASE_URL/api/projects" \
  -H 'Content-Type: application/json' \
  -d '{"name":"LaunchSpec AI UAT","idea":"帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。"}'

PROJECT_ID="$(node -e 'const data = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")); process.stdout.write(data.project.id)' "$EVIDENCE_DIR/create-project.json")"
test -n "$PROJECT_ID"

assert_status generate_blueprint 200 "$EVIDENCE_DIR/generate-blueprint.json" \
  -X POST "$BASE_URL/api/projects/$PROJECT_ID/generate"
assert_status get_project 200 "$EVIDENCE_DIR/get-project.json" "$BASE_URL/api/projects/$PROJECT_ID"

node -e 'const fs = require("fs"); const data = JSON.parse(fs.readFileSync(process.argv[1], "utf8")); data.project.blueprint.oneSentencePitch = "从一个想法到可审查 MVP 蓝图的本地工作台。"; fs.writeFileSync(process.argv[2], JSON.stringify({ blueprint: data.project.blueprint }))' \
  "$EVIDENCE_DIR/get-project.json" "$EVIDENCE_DIR/save-blueprint-request.json"
assert_status save_blueprint 200 "$EVIDENCE_DIR/save-blueprint.json" \
  -X PUT "$BASE_URL/api/projects/$PROJECT_ID" \
  -H 'Content-Type: application/json' \
  --data-binary "@$EVIDENCE_DIR/save-blueprint-request.json"
assert_status review_blueprint 200 "$EVIDENCE_DIR/review-blueprint.json" \
  -X POST "$BASE_URL/api/projects/$PROJECT_ID/review"
assert_status export_markdown 200 "$EVIDENCE_DIR/export-project.md" \
  "$BASE_URL/api/projects/$PROJECT_ID/export"
assert_status missing_project 404 "$EVIDENCE_DIR/missing-project.json" \
  "$BASE_URL/api/projects/not-a-real-project"

printf 'project_id=%s\n' "$PROJECT_ID" | tee -a "$STATUS_LOG"
printf 'provider=demo (not real model evidence)\n' | tee -a "$STATUS_LOG"
cat "$STATUS_LOG"
