#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/equiptracker"
BACKEND_DIR="$(dirname "$(dirname "$(realpath "$0")")")"

echo "=== Desplegando EquipTracker ==="

# 1. Copiar backend al servidor
echo "Copiando archivos..."
cp -r "$BACKEND_DIR" "$APP_DIR"

# 2. Copiar .env.production como .env si no existe
if [ ! -f "$APP_DIR/backend/.env" ]; then
    cp "$APP_DIR/backend/.env.production" "$APP_DIR/backend/.env"
    echo "Creado $APP_DIR/backend/.env desde .env.production"
    echo "!!! EDITAR .env con valores reales !!!"
fi

# 3. Construir y levantar
cd "$APP_DIR/backend"
echo "Construyendo imágenes..."
docker compose build

echo "Levantando servicios..."
docker compose up -d

# 4. Ejecutar migraciones
echo "Ejecutando migraciones..."
docker compose exec -T backend alembic upgrade head

echo "=== Deploy completo ==="
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
