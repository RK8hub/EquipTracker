#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# deploy.sh — Deploy remoto del backend EquipTracker
# Uso: ./backend/scripts/deploy.sh [branch]
# Ej:  ./backend/scripts/deploy.sh main
# ============================================================

BRANCH="${1:-main}"
SERVER="equiptracker@172.16.120.163"
REMOTE_DIR="/opt/equiptracker"
LOCAL_BACKEND="$(dirname "$(dirname "$(realpath "$0")")")"

echo "=== Deploy EquipTracker a $SERVER ($BRANCH) ==="

# ── 1. Generar credenciales ──────────────────────────────────
POSTGRES_PASSWORD=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
echo "  ✓ Credenciales generadas"

# ── 2. Sync código por rsync ─────────────────────────────────
echo "  Sincronizando código..."
rsync -avz --delete \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='equip_tracker.db' \
  "$LOCAL_BACKEND/" "$SERVER:$REMOTE_DIR/backend/"
echo "  ✓ Código sincronizado"

# ── 3. Crear .env en servidor ────────────────────────────────
ssh "$SERVER" "cat > $REMOTE_DIR/backend/.env << 'ENVEOF'
POSTGRES_DB=equiptracker
POSTGRES_USER=equiptracker
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
SECRET_KEY=$SECRET_KEY
ENVEOF"
echo "  ✓ .env creado en servidor"

# ── 4. Build + levantar contenedores ─────────────────────────
echo "  Construyendo imágenes..."
ssh "$SERVER" "cd $REMOTE_DIR/backend && docker compose build"

echo "  Levantando servicios..."
ssh "$SERVER" "cd $REMOTE_DIR/backend && docker compose up -d"

# ── 5. Esperar a que postgres esté listo ─────────────────────
echo "  Esperando servicios..."
sleep 5

# ── 6. Ejecutar migraciones ──────────────────────────────────
echo "  Ejecutando migraciones..."
ssh "$SERVER" "cd $REMOTE_DIR/backend && docker compose exec -T backend alembic upgrade head"
echo "  ✓ Migraciones ejecutadas"

# ── 7. Verificar health ──────────────────────────────────────
echo "  Verificando health..."
sleep 3
HEALTH=$(ssh "$SERVER" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health")
if [ "$HEALTH" = "200" ]; then
    echo "  ✓ API saludable (HTTP $HEALTH)"
else
    echo "  ⚠ Health check respondió HTTP $HEALTH — revisar logs: docker compose logs"
fi

# ── 8. Resumen ───────────────────────────────────────────────
echo ""
echo "=== Deploy completado ==="
echo "  API:     http://$SERVER:8000"
echo "  Docs:    http://$SERVER:8000/docs"
echo "  Postgres user: equiptracker"
echo "  Postgres pass: $POSTGRES_PASSWORD"
echo "  Secret key:    $SECRET_KEY"
echo ""
echo "⚠ Guarda estas credenciales en lugar seguro."
echo "  Para registrar usuario inicial:"
echo "    curl -X POST http://$SERVER:8000/auth/register \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"email\":\"admin@equiptracker\",\"password\":\"$POSTGRES_PASSWORD\",\"role\":\"admin\"}'"