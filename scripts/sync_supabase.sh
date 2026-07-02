#!/usr/bin/env bash
# Качване към Supabase (пусни от твоя компютър, не от ограничена среда).
# 1) cp .env.example .env  →  попълни DATABASE_URL от Supabase → Database → Connection string (URI)
# 2) chmod +x scripts/sync_supabase.sh
# Първи път (създава таблиците):  ./scripts/sync_supabase.sh --init
# След това (само скрап + upsert): ./scripts/sync_supabase.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Липсва .env — копирай .env.example като .env и сложи DATABASE_URL от Supabase."
  exit 1
fi

if [[ "${1:-}" == "--init" ]]; then
  exec python3 "$ROOT/run_pipeline.py"
else
  exec python3 "$ROOT/run_pipeline.py" --no-schema
fi
