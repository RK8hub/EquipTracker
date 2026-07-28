# EquipTracker — Backend API

> API REST para la gestión, asignación y mantenimiento de equipos tecnológicos empresariales.

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

## Estructura del Proyecto

```
backend/
├── .env                      # Variables de entorno (local)
├── Dockerfile                # Imagen del backend
├── docker-compose.yml        # Backend + PostgreSQL + Nginx
├── requirements.txt          # Dependencias
├── alembic.ini               # Configuración de Alembic
├── alembic/                  # Migraciones
│   ├── env.py
│   └── versions/
│       ├── 77ca..._initial_schema.py
│       └── e148..._add_users_table.py
├── nginx/
│   └── nginx.conf            # Configuración del reverse proxy
├── scripts/
│   ├── start.sh              # Entrypoint del contenedor (migraciones + servidor)
│   ├── deploy.sh             # Script de deploy automatizado
│   └── build-manifest.sh     # Genera latest.json para Tauri updater
├── updates/                  # Binarios para auto-updater
├── tests/
│   └── test_api.py           # Tests (17 tests)
└── app/
    ├── main.py               # Punto de entrada
    ├── dependencies.py       # Dependencias FastAPI (get_current_user)
    ├── core/
    │   ├── config.py         # Configuración multi-entorno
    │   └── errors.py         # BusinessError
    ├── database/
    │   └── connection.py     # Engine + sesión (SQLite/PostgreSQL)
    ├── models/               # ORM (SQLAlchemy)
    │   ├── base.py
    │   ├── user.py           # User (autenticación)
    │   ├── operator.py
    │   ├── equipment.py
    │   ├── equipment_specs.py
    │   ├── equipment_assignment.py
    │   └── equipment_history.py
    ├── schemas/              # Pydantic
    │   ├── types.py
    │   ├── auth.py           # UserCreate, Token, LoginRequest
    │   ├── operator.py
    │   ├── equipment.py
    │   ├── specs.py
    │   ├── assignment.py
    │   └── history.py
    ├── crud/                 # Operaciones BD por entidad
    │   ├── user.py
    │   ├── operator.py
    │   ├── equipment.py
    │   ├── specs.py
    │   ├── assignment.py
    │   └── history.py
    ├── services/             # Lógica de negocio
    │   ├── auth_service.py   # Registro, login, JWT
    │   ├── operators_service.py
    │   ├── equipment_service.py
    │   ├── specs_service.py
    │   ├── assignments_service.py
    │   └── history_service.py
    ├── routes/               # Endpoints REST
    │   ├── auth.py           # POST /auth/register, /auth/token
    │   ├── operators.py
    │   ├── equipment.py
    │   ├── specs.py
    │   ├── assignments.py
    │   ├── history.py
    │   └── updates.py        # GET /updates/latest.json, /updates/{platform}
    └── middleware/
        ├── auth.py           # Validación JWT (middleware)
        └── cors.py           # CORS configurable vía env
```

---

## Arquitectura por Capas

```
routes (HTTP) → services (lógica) → crud (BD) → models (ORM)
                                                    ↕
                                             database (SQLite/PostgreSQL)
```

### Autenticación

La API usa **JWT (Bearer token)**. Endpoints públicos:

> **Registro de usuarios:** `POST /auth/register` solo está disponible cuando no hay ningún usuario en la base de datos. Una vez creado el primer usuario (admin), el registro se deshabilita automáticamente.

| Path | Descripción |
|------|-------------|
| `POST /auth/register` | Registrar nuevo usuario (solo si no hay usuarios) |
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

- **Historial inmutable**: no se puede eliminar, solo actualizar (DELETE → 403)
- **Asignaciones activas**: un equipo no puede tener dos asignaciones activas simultáneas
- **Borrado protegido**: no se puede eliminar un operador/equipo con asignaciones o historial asociado (409 Conflict)
- **Specs referenciados**: no se puede eliminar una especificación si hay equipos que la usan

---

## Instalación y Ejecución (desarrollo local)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Usa SQLite por defecto (`.env` opcional). La API corre en `http://localhost:8000`, docs en `http://localhost:8000/docs`.

### Migraciones (Alembic)

```bash
alembic upgrade head                      # Aplicar migraciones
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
cd backend
cp .env.production .env      # Editar con valores reales
docker compose up -d          # Levanta postgres + backend + nginx
docker compose exec backend alembic upgrade head  # Migraciones

# Crear primer usuario (solo funciona si no hay usuarios en la BD):
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@empresa.com","password":"<password>","role":"admin"}'
```

### Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./equip_tracker.db` | URL de BD (cambiar a PostgreSQL en prod) |
| `SECRET_KEY` | `change-me-in-production` | Clave para firmar JWT |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Orígenes CORS (separados por coma) |
| `JSON_LOGS` | `false` | Activar logging en formato JSON |
| `UPDATES_DIR` | *(pendiente de definir en deploy)* | Directorio de binarios para auto-updater |

---

## Licencia

MIT
