#!/usr/bin/env bash
set -euo pipefail

echo "=== Ejecutando migraciones ==="
alembic upgrade head

echo "=== Iniciando servidor ==="
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
