# Plan de Escalado — EquipTracker: Servidor + App Desktop

## Objetivo

Escalar EquipTracker de un proyecto local backend-only a una arquitectura con:

- **Backend** montado en un servidor dentro de la LAN empresarial
- **Frontend** empaquetado como app de escritorio nativa con Tauri

> **Público objetivo:** Solo personal de IT / soporte técnico.
> **Red:** Únicamente LAN local, servidor no expuesto fuera de la red.
> **Seguridad:** Autenticación JWT con capa de codificación en la comunicación HTTP.
> **Infraestructura:** Sin servidor frontend — la app desktop apunta directo al backend.

---

## Fase 1: Backend — Preparación para servidor

### 1.1 Migración SQLite → PostgreSQL

- Agregar dependencias: `asyncpg`, `psycopg2-binary`, `alembic`
- Crear configuración de Alembic con migración inicial
- Actualizar `DATABASE_URL` para soportar multi-entorno:
  - Dev local: SQLite
  - Producción: PostgreSQL
- Agregar `docker-compose.yml` con servicio PostgreSQL

### 1.2 Autenticación JWT

- Agregar dependencias: `python-jose`, `passlib`, `bcrypt`
- Crear modelo `User` (id, email, hashed_password, role, created_at)
- Endpoints:
  - `POST /auth/register`
  - `POST /auth/token` (login)
- Dependencia `get_current_user` para proteger rutas
- Reemplazar sistema actual de API Key por JWT

### 1.3 Dockerización

- `Dockerfile` para el backend (Python 3.12-slim)
- `docker-compose.yml` con:
  - Backend (FastAPI + Uvicorn)
  - PostgreSQL
  - Nginx (reverse proxy, SSL opcional en LAN)
- `.env.production` con variables de servidor
- Scripts de deploy automatizado

### 1.4 Endpoint `/updates` — Auto Updater

- Servir archivos binarios para Tauri Updater:
  - `https://<backend-ip>/updates/latest.json` — manifiesto de versión
  - `https://<backend-ip>/updates/equiptracker_x.y.z_amd64.deb`
  - `https://<backend-ip>/updates/equiptracker_x.y.z_x64-setup.msi`
  - `https://<backend-ip>/updates/equiptracker_x.y.z_x64.dmg`
- El JSON contiene: versión, URL del binario, suma de verificación y notas de publicación
- Tauri Updater consulta este endpoint al iniciar y descarga/instala automáticamente si hay nueva versión

### 1.5 Seguridad y Producción

- Rate limiting con slowapi
- Logging estructurado (JSON logs)
- Health check endpoint mejorado
- CORS configurable vía variables de entorno
- HTTPS opcional (solo si se requiere en la LAN)

---

## Fase 2: Frontend — App de Escritorio con Tauri

### 2.1 Scaffolding

- Inicializar con `pnpm create tauri-app` (React + TypeScript + Vite)
- Tauri v2 con Rust backend mínimo
- Configurar `tauri.conf.json` (ventana, icono, nombre de la app)

### 2.2 UI (siguiendo plan existente)

- React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui
- React Router 7 para navegación entre secciones
- Axios para comunicación HTTP con el backend remoto

### 2.3 Login / Auth Flow

- Pantalla de login con email + contraseña
- Almacenar JWT en `tauri-plugin-store` (keyring del SO)
- Interceptor de Axios para adjuntar token automáticamente
- Refresh token automático al expirar

### 2.4 Conexión al servidor — IP hardcodeada vía `.env`

- La IP del backend se define en un `.env` en la raíz del proyecto:
  ```env
  VITE_API_URL=http://192.168.1.100:8000
  ```
- Vite inyecta esta variable en tiempo de compilación
- Si la IP del servidor cambia, solo se edita el `.env` y se recompila
- Sin necesidad de settings dentro de la app — la URL es fija en el binario
- Sin Vite proxy — la app apunta directo al backend

### 2.5 Funcionalidad CRUD

- Operadores, Equipos, Especificaciones, Asignaciones, Historial
- Componentes: DataTable, ConfirmDialog, StatusBadge, Pagination
- Formularios con validación

### 2.6 Auto Updater (Tauri)

- Configurar `tauri.conf.json` con el endpoint de actualizaciones:
  ```json
  {
    "plugins": {
      "updater": {
        "endpoints": ["http://192.168.1.100:8000/updates/latest.json"],
        "pubkey": "..."
      }
    }
  }
  ```
- Al iniciar la app, consulta el endpoint `/updates`
- Si hay una versión más nueva, descarga e instala automáticamente
- Las actualizaciones son silenciosas (opcional: notificar al usuario)

### 2.7 Empaquetado Nativo

- Linux: `.deb` / `.AppImage`
- macOS: `.dmg`
- Windows: `.msi`
- Build script que genera los binarios y los copia al directorio servido por `/updates`

---

## Arquitectura General

```
[App Tauri Desktop] --HTTP/JWT--> [FastAPI Backend] --> [PostgreSQL]
       |                                  |
       |-- /updates (auto updater) -------|
```

- **Frontend (Tauri):** App de escritorio nativa. Sin servidor web. La URL del backend va hardcodeada en el binario vía `.env` de compilación.
- **Backend (FastAPI):** API REST dentro de la LAN. Sirve datos y también los binarios de actualización.
- **Base de datos:** PostgreSQL en el mismo servidor o contenedor.
- **Actualizaciones:** Endpoint `/updates` en el propio backend. Sin infraestructura extra.
- **Migración futura:** Si se requiere acceso web, el mismo frontend React se sirve desde Nginx sin cambiar una línea de código.

---

## Resumen de tecnologías nuevas

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Backend | PostgreSQL | Base de datos para servidor |
| Backend | Alembic | Migraciones de base de datos |
| Backend | Docker + docker-compose | Contenerización y deploy |
| Backend | python-jose + passlib + bcrypt | JWT + hashing de passwords |
| Backend | slowapi | Rate limiting |
| Frontend | Tauri v2 | App de escritorio nativa |
| Frontend | tauri-plugin-store | Almacenamiento seguro de tokens |
| Frontend | Tauri updater | Actualizaciones automáticas |

---

## Orden de implementación sugerido

1. Backend: PostgreSQL + Alembic
2. Backend: JWT auth
3. Backend: Dockerización
4. Backend: Endpoint `/updates` + estructura para binarios
5. Frontend: Scaffolding Tauri + React + UI base
6. Frontend: Login flow con JWT
7. Frontend: CRUD completo
8. Frontend: Auto Updater (Tauri)
9. Pruebas integración backend + frontend
10. Empaquetado y deploy con build script
