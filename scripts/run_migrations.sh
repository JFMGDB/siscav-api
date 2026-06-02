#!/usr/bin/env bash
# Run Alembic migrations against Supabase (or any DATABASE_URL in .env.supabase).
# Usage from repo root: ./scripts/run_migrations.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== Running Alembic Migrations ==="

export PYTHONPATH="$REPO_ROOT"

ENV_FILE="${ENV_FILE:-.env.supabase}"
if [[ -f "$ENV_FILE" ]]; then
  echo "Loading environment from $ENV_FILE..."
  set -a
  # shellcheck disable=SC1090
  source <(grep -v '^#' "$ENV_FILE" | grep -v '^[[:space:]]*$' | sed 's/\r$//')
  set +a
else
  echo "WARNING: $ENV_FILE not found. Export DATABASE_URL before running." >&2
  exit 1
fi

if [[ -d "venv/bin" ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

echo "Verifying database URL (masked)..."
python -c "
import sys
sys.path.insert(0, '.')
from apps.api.src.api.v1.core.config import get_settings
url = get_settings().database_url
print('DATABASE_URL:', url[:60] + '...' if len(url) > 60 else url)
"

echo "Current revision:"
alembic current

echo "Upgrading to head..."
alembic upgrade head

echo "=== Migrations completed ==="
alembic current
