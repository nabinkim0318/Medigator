#!/usr/bin/env bash
# Canonical local/demo container smoke for this research prototype.
# Builds, starts, polls HTTP health, optionally checks the demo UI and
# SQLite persistence, then always shuts Compose down.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker/docker-compose.yml)
SMOKE_FRONTEND="${SMOKE_FRONTEND:-1}"
SMOKE_PERSISTENCE="${SMOKE_PERSISTENCE:-1}"
TIMEOUT="${SMOKE_TIMEOUT:-120}"
API_URL="${API_URL:-http://127.0.0.1:8082}"
UI_URL="${UI_URL:-http://127.0.0.1:3000}"
HEALTH_URL="${API_URL}/health"
DEMO_ACCESS_CODE="${DEMO_ACCESS_CODE:-replace-me-locally}"
BODY_FILE="$(mktemp)"
KEEP_UP="${SMOKE_KEEP_UP:-0}"

cleanup() {
  rm -f "$BODY_FILE"
  if [[ "$KEEP_UP" != "1" ]]; then
    "${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

wait_http() {
  local url="$1"
  local label="${2:-$url}"
  local deadline=$((SECONDS + TIMEOUT))
  local code=""
  while (( SECONDS < deadline )); do
    code="$(curl -sS -o "$BODY_FILE" -w '%{http_code}' --max-time 4 "$url" || true)"
    if [[ "$code" == "200" ]]; then
      echo "${label}: HTTP ${code}"
      return 0
    fi
    sleep 2
  done
  echo "timed out waiting for HTTP 200 from ${label} (last status: ${code:-none})" >&2
  if [[ -s "$BODY_FILE" ]]; then
    echo "last body:" >&2
    head -c 500 "$BODY_FILE" >&2 || true
    echo >&2
  fi
  "${COMPOSE[@]}" logs --no-color >&2 || true
  return 1
}

assert_health_body() {
  python3 - "$BODY_FILE" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as fh:
    body = json.load(fh)
status = body.get("status")
if status != "healthy":
    raise SystemExit(f"unexpected /health body status={status!r} body={body!r}")
print("backend health body: status=healthy")
PY
}

echo "Building and starting canonical Compose services (repository-root context)..."
if [[ "$SMOKE_FRONTEND" == "1" ]]; then
  "${COMPOSE[@]}" up --build -d
else
  "${COMPOSE[@]}" up --build -d api
fi

wait_http "$HEALTH_URL" "backend /health"
assert_health_body

if [[ "$SMOKE_FRONTEND" == "1" ]]; then
  wait_http "$UI_URL" "frontend /"
fi

if [[ "$SMOKE_PERSISTENCE" == "1" ]]; then
  session_id="demo-docker-persist-$(date +%s)-$$"
  echo "Writing synthetic appointment through POST /api/v1/patient/appointment..."
  write_code="$(curl -sS -o "$BODY_FILE" -w '%{http_code}' --max-time 15 \
    -X POST "${API_URL}/api/v1/patient/appointment" \
    -H "Content-Type: application/json" \
    -d "{
      \"session_id\": \"${session_id}\",
      \"patientData\": {
        \"name\": \"Demo Patient\",
        \"age\": 40,
        \"gender\": \"Female\",
        \"bloodGroup\": \"O+\",
        \"phone\": \"5550101234\",
        \"email\": \"demo.patient@example.com\"
      },
      \"appointmentData\": {\"q1\": \"chest pain\", \"q2\": \"middle of chest\"}
    }")"
  if [[ "$write_code" != "200" ]]; then
    echo "synthetic write failed: HTTP ${write_code}" >&2
    cat "$BODY_FILE" >&2 || true
    exit 1
  fi

  db_path="${ROOT}/data/medigator.db"
  if [[ ! -f "$db_path" ]]; then
    echo "canonical SQLite file missing after write: ${db_path}" >&2
    exit 1
  fi
  echo "SQLite path: ${db_path}"

  echo "Restarting api container to check volume persistence..."
  "${COMPOSE[@]}" restart api
  wait_http "$HEALTH_URL" "backend /health after restart"
  assert_health_body

  token="$(python3 - "$API_URL" "$DEMO_ACCESS_CODE" <<'PY'
import json
import sys
import urllib.request

api_url, access_code = sys.argv[1], sys.argv[2]
req = urllib.request.Request(
    f"{api_url}/api/v1/auth/demo-operator",
    data=json.dumps({"access_code": access_code}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=10) as response:
    payload = json.loads(response.read().decode("utf-8"))
token = payload.get("operator_session")
if not token:
    raise SystemExit(f"demo-operator did not return a session: {payload!r}")
print(token)
PY
)"
  listed="$(python3 - "$API_URL" "$token" <<'PY'
import json
import sys
import urllib.request

api_url, token = sys.argv[1], sys.argv[2]
req = urllib.request.Request(
    f"{api_url}/api/v1/patient/profile",
    headers={"Authorization": f"Bearer {token}"},
)
with urllib.request.urlopen(req, timeout=10) as response:
    payload = json.loads(response.read().decode("utf-8"))
profiles = payload.get("profiles") or []
if not profiles:
    raise SystemExit(f"no profiles after restart: {payload!r}")
print(f"persistence across restart: PASS ({len(profiles)} profile(s))")
PY
)"
  echo "$listed"
fi

echo "docker-smoke: PASS"
