#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$ROOT/.dev.pids"

# Load configuration
set -a
source "$ROOT/.env"
set +a

# Clean stale pidfile
rm -f "$PIDFILE"

echo "==> Installing dependencies..."
uv sync --quiet
(cd "$ROOT/frontend" && pnpm install --silent)

echo "==> Starting backend (port $BACKEND_PORT)..."
uv run uvicorn cv_gen.api:app --reload --port "$BACKEND_PORT" &
echo $! >> "$PIDFILE"

echo "==> Starting frontend (port $FRONTEND_PORT)..."
(cd "$ROOT/frontend" && VITE_BACKEND_URL="http://localhost:$BACKEND_PORT" pnpm dev --port "$FRONTEND_PORT") &
echo $! >> "$PIDFILE"

echo ""
echo "  Frontend:  http://localhost:$FRONTEND_PORT"
echo "  Backend:   http://localhost:$BACKEND_PORT"
echo ""
echo "  Stop with:  ./stop.sh"
echo ""

# Wait so Ctrl+C kills both
wait
