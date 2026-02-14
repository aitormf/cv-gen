#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$ROOT/.dev.pids"

if [ ! -f "$PIDFILE" ]; then
  echo "No running processes found (.dev.pids missing)"
  exit 0
fi

echo "==> Stopping dev servers..."
while read -r pid; do
  if kill -0 "$pid" 2>/dev/null; then
    kill -- -"$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    echo "  Stopped PID $pid"
  fi
done < "$PIDFILE"

rm -f "$PIDFILE"
echo "Done."
