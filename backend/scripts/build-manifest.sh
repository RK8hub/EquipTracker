#!/usr/bin/env bash
# Genera el manifiesto latest.json para el auto-updater de Tauri
# Uso: ./scripts/build-manifest.sh <version> <backend_url>
# Ej:  ./scripts/build-manifest.sh 0.2.0 http://172.16.120.163:8000

set -euo pipefail

VERSION="${1:?Uso: $0 <version> <backend_url>}"
BASE_URL="${2:?Uso: $0 <version> <backend_url>}"
UPDATES_DIR="${UPDATES_DIR:-/opt/equiptracker/updates}"

if [ ! -d "$UPDATES_DIR" ]; then
    echo "Error: $UPDATES_DIR no existe"
    exit 1
fi

cat > "$UPDATES_DIR/latest.json" <<MANIFEST
{
  "version": "$VERSION",
  "notes": "Ver changelog en el repositorio",
  "pub_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "platforms": {
    "linux": {
      "url": "${BASE_URL}/updates/linux",
      "signature": ""
    },
    "windows": {
      "url": "${BASE_URL}/updates/windows",
      "signature": ""
    },
    "macos": {
      "url": "${BASE_URL}/updates/macos",
      "signature": ""
    }
  }
}
MANIFEST

echo "Manifiesto generado: $UPDATES_DIR/latest.json"
