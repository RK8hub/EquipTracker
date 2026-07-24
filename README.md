# EquipTracker

> Sistema de tracking de equipos IT — API REST (FastAPI) + Cliente de escritorio (Tauri + React).
> Gestión, asignación y mantenimiento de equipos tecnológicos empresariales.

## Stack Tecnológico

| Tecnología | Propósito |
|------------|-----------|
| Python 3.12+ / FastAPI | Framework web ASGI |
| SQLAlchemy 2.0+ / Alembic | ORM + migraciones |
| PostgreSQL 16 (prod) / SQLite (dev) | Base de datos |
| Pydantic v2 | Validación y serialización |
| Uvicorn | Servidor ASGI |
| Docker + Docker Compose | Contenerización y deploy |
| Nginx | Reverse proxy |
| python-jose / passlib / bcrypt | JWT + hashing |
| slowapi | Rate limiting |
| React 19 / TypeScript 6 / Tailwind CSS v4 | Frontend web (shadcn/ui) |
| Tauri v2 | Cliente de escritorio nativo |
| Vite 8 | Bundler frontend |

## Estructura del Proyecto

```
EquipTracker/
├── backend/                  ← API REST (FastAPI)
│   ├── .env                  # Variables de entorno (local)
│   ├── .env.production       # Plantilla para producción
│   ├── Dockerfile            # Imagen del backend
│   ├── docker-compose.yml    # Backend + PostgreSQL + Nginx
│   ├── requirements.txt      # Dependencias Python
│   ├── alembic.ini           # Configuración de Alembic
│   ├── alembic/              # Migraciones
│   ├── nginx/nginx.conf      # Reverse proxy
│   ├── scripts/
│   │   ├── start.sh          # Entrypoint del contenedor
│   │   ├── deploy.sh         # Deploy automatizado vía rsync
│   │   └── build-manifest.sh # Manifiesto para auto-updater
│   ├── updates/              # Binarios para auto-updater
│   ├── tests/
│   │   └── test_api.py       # 17 tests
│   └── app/
│       ├── main.py           # Entrypoint FastAPI
│       ├── dependencies.py   # get_current_user
│       ├── core/             # config.py, errors.py
│       ├── database/         # connection.py (SQLite/PostgreSQL)
│       ├── models/           # 6 modelos SQLAlchemy
│       ├── schemas/          # Pydantic por entidad
│       ├── crud/             # Operaciones BD
│       ├── services/         # Lógica de negocio
│       ├── routes/           # 8 routers REST
│       └── middleware/       # auth.py (JWT), cors.py
│
└── frontend/                 ← Cliente Tauri + React
    ├── src/
    │   ├── components/ui/    # 11 componentes shadcn/ui
    │   ├── pages/            # Pendiente de implementar
    │   ├── api/client.ts     # Axios + interceptor 401
    │   ├── hooks/            # Pendiente
    │   ├── types/            # Pendiente
    │   ├── App.tsx           # Router + Toaster
    │   ├── main.tsx          # BrowserRouter
    │   └── index.css         # Tailwind
    ├── src-tauri/            # Tauri v2 (store + updater plugins)
    └── vite.config.ts        # Proxy /api → :8000
```

### Ramas Git

| Rama | Estado | Descripción |
|------|--------|-------------|
| `main` | ✅ Completa | Backend fase 1 completo. Último fix: `.env` excluido de rsync |
| `frontend` | ⏳ En desarrollo | Frontend Tauri + React, 4 commits |
| `backend` | ❌ Eliminada | Contenido mergeado a `main`. Aún existe en `origin/backend` |

---

## Arquitectura por Capas

```
routes (HTTP) → services (lógica) → crud (BD) → models (ORM)
                                                    ↕
                                             database (SQLite/PostgreSQL)
```

### Autenticación

La API usa **JWT (Bearer token)**. Endpoints públicos:

> **Registro de usuarios:** `/auth/register` solo está disponible cuando no hay ningún usuario en la base de datos. Una vez creado el primer usuario (admin), el registro se deshabilita automáticamente. Usar la consola del servidor o la API con token de admin para crear más usuarios.

Endpoints públicos:

| Path | Descripción |
|------|-------------|
| `POST /auth/register` | Registrar nuevo usuario |
| `POST /auth/token` | Login, devuelve `access_token` |
| `GET /health` | Health check |
| `GET /docs` | Swagger UI |
| `/updates/*` | Auto-updater de Tauri |

Todos los demás endpoints requieren header:

```
Authorization: Bearer <token>
```

El token expira en **24 horas**. El hash de contraseñas usa **bcrypt** via passlib.

### Endpoints

| Método | Path | Descripción |
|--------|------|-------------|
| POST | `/auth/register` | Crear usuario (email, password, role). **Solo funciona si no hay usuarios registrados.** |
| POST | `/auth/token` | Login → JWT |
| GET/POST | `/operators` | Listar / crear operadores |
| GET/PUT/DELETE | `/operators/{id}` | CRUD operador |
| GET/POST | `/equipment` | Listar / crear equipos |
| GET/PUT/DELETE | `/equipment/{id}` | CRUD equipo |
| GET/POST | `/specs` | Listar / crear especificaciones |
| GET/PUT/DELETE | `/specs/{id}` | CRUD specs |
| GET/POST | `/assignments` | Listar / crear asignaciones |
| GET/PUT/DELETE | `/assignments/{id}` | CRUD asignación |
| GET/POST | `/history` | Listar / crear historial |
| GET/PUT | `/history/{id}` | Leer / actualizar historial (DELETE = 403) |
| GET | `/updates/latest.json` | Manifiesto del auto-updater |
| GET | `/updates/{platform}` | Descargar binario (linux/windows/macos) |
| GET | `/health` | Health check |

### Reglas de negocio clave

- **Historial inmutable**: no se puede eliminar, solo actualizar
- **Asignaciones activas**: un equipo no puede tener dos asignaciones activas simultáneas
- **Borrado protegido**: no se puede eliminar un operador/equipo con asignaciones o historial asociado
- **Specs referenciados**: no se puede eliminar una especificación si hay equipos que la usan

### Decisiones de arquitectura

- **Rol `staff` en vez de `operator`**: el modelo `User` usa `role` con default `"staff"` para evitar confusión con la entidad `Operator` (empleado que recibe equipos).
- **Token JWT 24h sin refresh**: `ACCESS_TOKEN_EXPIRE_MINUTES = 1440`. No existe endpoint `/auth/refresh`. Al expirar, el frontend muestra "Sesión expirada".
- **Conexión configurable sin recompilar**: la IP del backend no se hardcodea. Pantalla de setup inicial donde el usuario ingresa la URL. Persistencia vía `tauri-plugin-store`.
- **Driver PostgreSQL**: `psycopg2-binary` (compatible con SQLAlchemy y Alembic).
- **Rama única de trabajo**: el frontend se desarrolla en su rama y al finalizar se mergea a `main` + tag semántico. Sin ramas intermedias.

---

## Roadmap

### Fase 1 — Backend ✅ Completada
- API REST con 5 entidades (operators, equipment, specs, assignments, history)
- Autenticación JWT + roles (admin/staff)
- PostgreSQL + Alembic + Docker
- Rate limiting, logging, CORS configurable
- Auto-updater endpoint para Tauri
- Deploy script con rsync

### Fase 2 — Frontend Tauri (⏳ en ejecución)

| Paso | Descripción | Estado |
|------|-------------|--------|
| P1 | Login / Auth Flow (pantalla login, JWT en store) | ⏳ Pendiente |
| P2 | Conexión configurable (setup inicial, settings) | ⏳ Pendiente |
| P3 | Tipos TypeScript (5 entidades) | ⏳ Pendiente |
| P4 | Capa API (client + 5 módulos) | ⏳ Pendiente |
| P5 | Layout base (Sidebar + Router) | ⏳ Pendiente |
| P6 | Componentes UI comunes (DataTable, Pagination) | ⏳ Pendiente |
| P7-P11 | Páginas CRUD (operadores, equipos, specs, asignaciones, historial) | ⏳ Pendiente |
| P12 | Dashboard | ⏳ Pendiente |
| P13 | Auto Updater + empaquetado (.deb / .AppImage) | ⏳ Pendiente |

**Estimado total fase 2:** ~10-12h de desarrollo efectivo.

---

## Instalación y Ejecución (desarrollo local)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Usa SQLite por defecto (`.env`). La API en `http://localhost:8000`, docs en `http://localhost:8000/docs`.

### Migraciones (Alembic)

```bash
alembic upgrade head        # Aplicar migraciones
alembic revision --autogenerate -m "descripcion"  # Nueva migración
```

### Tests

```bash
cd backend
pytest tests/ -v
```

---

## Docker / Producción

```bash
# En el servidor:
cd /opt/equiptracker/backend
docker compose up -d          # Levanta postgres + backend + nginx
docker compose exec backend alembic upgrade head  # Migraciones

# .env no se sincroniza — se crea manualmente en el servidor.
```

> ⚠ **El `.env` está excluido del rsync**. Se genera directamente en el servidor.
> El script `deploy.sh` genera credenciales aleatorias (openssl rand) en cada deploy.

### Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./equip_tracker.db` | URL de BD (SQLite local / PostgreSQL prod) |
| `SECRET_KEY` | `change-me-in-production` | Clave para firmar JWT |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Orígenes CORS (separados por coma) |
| `JSON_LOGS` | `false` | Activar logging en formato JSON |
| `UPDATES_DIR` | `/opt/equiptracker/updates` | Directorio de binarios para auto-updater |
| `API_KEY` | Autogenerada (token_urlsafe) | API key de respaldo |
| `DB_URL` | — | Fallback si no existe `DATABASE_URL` |

---

## Licencia

MIT
