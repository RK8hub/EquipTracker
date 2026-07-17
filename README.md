# EquipTracker — Backend API

> API REST para la gestión, asignación y mantenimiento de equipos tecnológicos empresariales.

## Stack Tecnológico

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.12+ | Lenguaje de desarrollo |
| FastAPI | 0.136+ | Framework web ASGI |
| SQLAlchemy | 2.0+ | ORM para base de datos |
| SQLite | — | Motor de base de datos embebido |
| Pydantic | 2.13+ | Validación y serialización de datos |
| Uvicorn | 0.47+ | Servidor ASGI |

## Estructura del Proyecto

```
backend/
├── .env                        # Variables de entorno
├── .gitignore                  # Archivos ignorados por git
├── requirements.txt            # Dependencias del proyecto
└── app/
    ├── main.py                 # Punto de entrada de la aplicación
    ├── core/
    │   ├── config.py           # Configuración y variables de entorno
    │   └── errors.py           # Excepción base de negocio
    ├── database/
    │   └── connection.py       # Conexión y sesión de base de datos
    ├── models/                 # Modelos ORM (SQLAlchemy)
    ├── schemas/                # Esquemas de validación (Pydantic)
    ├── crud/                   # Operaciones directas contra la BD
    ├── services/               # Lógica de negocio
    ├── routes/                 # Endpoints REST
    └── middleware/
        └── cors.py             # Configuración CORS
```

---

## Arquitectura por Capas

La aplicación sigue una separación estricta de responsabilidades en 5 capas:

```
routes (HTTP) → services (lógica) → crud (BD) → models (ORM)
                                                    ↕
                                             database (SQLite)
```

### 1. Core — `app/core/`

#### `config.py`
Carga las variables de entorno desde `.env` usando `python-dotenv`. Provee dos constantes tipadas:

- `DATABASE_URL` — URL de conexión a la base de datos.
- `SECRET_KEY` — Clave secreta para la aplicación.

```python
DATABASE_URL = "sqlite:///./equip_tracker.db"
SECRET_KEY = "change-me-in-production"
```

#### `errors.py`
Define `BusinessError`, una excepción personalizada que transporta un mensaje y un código HTTP. Es capturada por un handler global en `main.py` para retornar respuestas JSON consistentes.

```python
class BusinessError(Exception):
    def __init__(self, message: str, status_code: int = 400): ...
```

---

### 2. Database — `app/database/`

#### `connection.py`
Configura el engine de SQLAlchemy para SQLite y expone:

- `engine` — Instancia del motor SQLAlchemy.
- `SessionLocal` — Fábrica de sesiones.
- `get_db()` — Generador de dependencia para FastAPI. Crea una sesión por request y la cierra automáticamente al finalizar.

```python
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### 3. Modelos ORM — `app/models/`

5 entidades que mapean directamente a tablas SQLite.

#### `base.py`
Clase base declarativa `Base` que hereda de `DeclarativeBase`. Todos los modelos la extienden.

#### `Operator` — `app/models/operator.py`
Tabla: `operators`

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `id` | integer | PK, autoincremental |
| `name` | string(100) | NOT NULL |
| `department` | string(100) | NOT NULL |
| `position` | string(100) | NOT NULL |

Relaciones:
- `assignments` → `EquipmentAssignment` (1:N, como operador asignado)
- `reported_history_records` → `EquipmentHistory` (1:N, como reportador)
- `technical_history_records` → `EquipmentHistory` (1:N, como técnico)

#### `EquipmentSpecs` — `app/models/equipment_specs.py`
Tabla: `equipment_specs`

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `id` | integer | PK, autoincremental |
| `cpu` | JSON | NOT NULL |
| `ram` | JSON | NOT NULL |
| `storage` | JSON | NOT NULL |
| `graphics` | JSON | NOT NULL |

Relaciones:
- `equipment` → `Equipment` (1:1, referenciado por `Equipment.specs_id`)

Los campos JSON almacenan estructuras anidadas. Ver esquemas Pydantic en `schemas/specs.py`.

#### `Equipment` — `app/models/equipment.py`
Tabla: `equipments`

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `id` | integer | PK, autoincremental |
| `serial` | string(30) | UNIQUE, NOT NULL |
| `brand` | string(100) | NOT NULL |
| `model` | string(100) | NOT NULL |
| `created_at` | datetime(tz) | server_default = `now()` |
| `specs_id` | integer | FK → `equipment_specs.id`, NOT NULL |

Relaciones:
- `specs` → `EquipmentSpecs` (1:1)
- `assignments` → `EquipmentAssignment` (1:N)
- `history_records` → `EquipmentHistory` (1:N)

#### `EquipmentAssignment` — `app/models/equipment_assignment.py`
Tabla: `equipment_assignments`

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `id` | integer | PK, autoincremental |
| `equipment_id` | integer | FK → `equipments.id`, NOT NULL |
| `operator_id` | integer | FK → `operators.id`, NOT NULL |
| `assigned_by` | integer | FK → `operators.id`, NOT NULL |
| `assigned_at` | datetime(tz) | server_default = `now()` |
| `returned_at` | datetime(tz) \| NULL | Nullable |
| `status` | string(20) | default = `"active"` |

Relaciones:
- `equipment` → `Equipment`
- `operator` → `Operator` (operador asignado)
- `assigner` → `Operator` (admin que asignó)

#### `EquipmentHistory` — `app/models/equipment_history.py`
Tabla: `equipment_history`

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `id` | integer | PK, autoincremental |
| `equipment_id` | integer | FK → `equipments.id`, NOT NULL |
| `type` | string(50) | NOT NULL (repair, maintenance, upgrade, etc.) |
| `reason` | string(500) | NOT NULL |
| `status` | string(20) | default = `"open"` |
| `reported_by` | integer | FK → `operators.id`, NOT NULL |
| `technician_id` | integer | FK → `operators.id`, NOT NULL |
| `created_at` | datetime(tz) | server_default = `now()` |
| `resolved_at` | datetime(tz) \| NULL | Nullable |

Relaciones:
- `equipment` → `Equipment`
- `reporter` → `Operator`
- `technician` → `Operator`

### Diagrama de Relaciones

```
EquipmentSpecs (1) ──── (1) Equipment (1) ──── (N) EquipmentAssignment (N) ──── (1) Operator
                                    │
                                    └── (N) EquipmentHistory (N) ──── (1) Operator (reporter)
                                                                  └── (1) Operator (technician)
```

---

### 4. Esquemas Pydantic — `app/schemas/`

Definen la validación, serialización y documentación automática (OpenAPI) de los datos que entran y salen por la API.

#### `types.py`
Tipos reutilizables:

| Tipo | Descripción |
|------|-------------|
| `NonEmptyStr` | String con `strip_whitespace`, `min_length=1` |
| `SerialString` | String con formato `^[A-Z0-9-]+$`, max 30 chars |
| `Id` | Entero positivo ≥ 1 |

#### `operator.py`
| Esquema | Campos | Uso |
|---------|--------|-----|
| `OperatorBase` | name, department, position | Base |
| `OperatorCreate` | Hereda de Base | Creación |
| `OperatorRead` | Base + id | Lectura |
| `OperatorUpdate` | Todos opcionales | Actualización parcial |

#### `equipment.py`
| Esquema | Campos | Uso |
|---------|--------|-----|
| `EquipmentBase` | serial, brand, model, specs_id | Base |
| `EquipmentCreate` | Hereda de Base | Creación |
| `EquipmentRead` | Base + id, created_at | Lectura |
| `EquipmentUpdate` | Todos opcionales, extra=forbid | Actualización parcial |

#### `specs.py`
| Esquema | Campos |
|---------|--------|
| `CPUInfo` | brand, model |
| `CapacityInfo` | value (>0), unit (MB\|GB\|TB) |
| `RAMInfo` | capacity (CapacityInfo), mode (single\|dual) |
| `StorageInfo` | capacity (CapacityInfo), type (HDD\|SSD\|NVMe) |
| `GraphicsInfo` | brand, model, type (integrated\|dedicated), memory (CapacityInfo \| None) |
| `SpecsBase` | cpu, ram, storage, graphics |
| `SpecsCreate` | Hereda de Base |
| `SpecsRead` | Base + id |
| `SpecsUpdate` | Todos opcionales |

#### `assignment.py`
| Esquema | Campos |
|---------|--------|
| `AssignmentBase` | equipment_id, operator_id, assigned_by, assigned_at, returned_at, status (active\|inactive) |
| `AssignmentCreate` | equipment_id, operator_id, assigned_by, assigned_at (opcional) |
| `AssignmentRead` | Base + id |
| `AssignmentUpdate` | returned_at, status (ambos opcionales, extra=forbid) |

#### `history.py`
| Esquema | Campos |
|---------|--------|
| `HistoryBase` | equipment_id, type, reason, status (open\|closed), reported_by, technician_id, created_at, resolved_at |
| `HistoryCreate` | equipment_id, type, reason, reported_by, technician_id |
| `HistoryRead` | Base + id |
| `HistoryUpdate` | type, reason, status, technician_id, resolved_at (todos opcionales, extra=forbid) |

---

### 5. Capa CRUD — `app/crud/`

Operaciones directas de base de datos por entidad. Cada archivo contiene funciones con transacciones atómicas y rollback ante errores.

Patrón común en todas las entidades:

| Operación | Función | Descripción |
|-----------|---------|-------------|
| Obtener uno | `get_*(db, id)` | Búsqueda por PK, retorna None si no existe |
| Listar | `get_*(db, skip, limit)` | Paginado offset/limit |
| Crear | `create_*(db, data)` | Inserta y hace commit+refresh |
| Actualizar | `update_*(db, id, data)` | Actualiza solo campos presentes (exclude_unset) |
| Eliminar | `delete_*(db, id)` | Elimina y hace commit, retorna True o None |

Todas las operaciones de escritura envuelven el bloque en try/except para hacer rollback ante `SQLAlchemyError`.

#### Detalles específicos:

- **`crud/assignment.py`** — Al crear establece `returned_at=None` y `status="active"`.
- **`crud/specs.py`** — Los campos JSON (`cpu`, `ram`, `storage`, `graphics`) se serializan con `.model_dump()` antes de insertar.
- **`crud/operator.py`** — Creación explícita campo por campo (no usa `**data.model_dump()`).

---

### 6. Capa de Servicios — `app/services/`

Contiene la lógica de negocio. Cada servicio valida reglas antes de delegar al CRUD.

#### `operators_service.py`
| Función | Reglas de negocio |
|---------|-------------------|
| `create_operator` | Sin validaciones adicionales |
| `delete_operator` | Bloquea si el operador tiene asignaciones (`409`) o registros de historial como reportador/técnico (`409`) |

#### `equipment_service.py`
| Función | Reglas de negocio |
|---------|-------------------|
| `create_equipment` | Valida que `specs_id` exista (`404`) |
| `update_equipment` | Valida que `specs_id` exista si se provee (`404`) |
| `delete_equipment` | Bloquea si el equipo tiene asignaciones (`409`) o historial (`409`) |

#### `specs_service.py`
| Función | Reglas de negocio |
|---------|-------------------|
| `delete_spec` | Bloquea si hay algún equipo referenciando este specs (`409`) |

#### `assignments_service.py`
| Función | Reglas de negocio |
|---------|-------------------|
| `create_assignment` | Valida existencia de operator, assigner y equipment (`404`). Bloquea si el equipo ya tiene una asignación activa (`409`) |
| `update_assignment` | Si `returned_at` se establece, fuerza `status="inactive"`. Si `status="inactive"` sin `returned_at`, rechaza (`400`) |
| `delete_assignment` | Sin validaciones adicionales |

#### `history_service.py`
| Función | Reglas de negocio |
|---------|-------------------|
| `create_history_record` | Valida existencia de equipment, reporter y technician (`404`) |
| `update_history_record` | Si `status="closed"` sin `resolved_at`, rechaza (`400`). Si `status="open"` con `resolved_at`, lo fuerza a `None` |
| `delete_history_record` | **Siempre rechaza** (`403`). Los registros de historial son inmutables |

---

### 7. Rutas (Endpoints REST) — `app/routes/`

Cada archivo define un `APIRouter` con prefijo y tags. Todos los endpoints usan `get_db` como dependencia para la sesión.

#### `GET /health`
- **Tags:** meta
- **Respuesta:** `{"status": "ok"}`

#### `GET/POST /operators`
#### `GET/PUT/DELETE /operators/{operator_id}`

| Método | Path | Códigos de respuesta |
|--------|------|----------------------|
| GET | `/operators` | 200 — Lista paginada (skip, limit, max 100) |
| GET | `/operators/{id}` | 200 / 404 |
| POST | `/operators` | 201 — Crea operador |
| PUT | `/operators/{id}` | 200 / 404 |
| DELETE | `/operators/{id}` | 204 / 404 / 409 |

#### `GET/POST /equipment`
#### `GET/PUT/DELETE /equipment/{equipment_id}`

| Método | Path | Códigos de respuesta |
|--------|------|----------------------|
| GET | `/equipment` | 200 — Lista paginada (skip, limit, max 100) |
| GET | `/equipment/{id}` | 200 / 404 |
| POST | `/equipment` | 201 — Crea equipo |
| PUT | `/equipment/{id}` | 200 / 404 |
| DELETE | `/equipment/{id}` | 204 / 404 / 409 |

#### `GET/POST /specs`
#### `GET/PUT/DELETE /specs/{spec_id}`

| Método | Path | Códigos de respuesta |
|--------|------|----------------------|
| GET | `/specs` | 200 — Lista paginada (skip, limit, max 100) |
| GET | `/specs/{id}` | 200 / 404 |
| POST | `/specs` | 201 — Crea especificaciones |
| PUT | `/specs/{id}` | 200 / 404 |
| DELETE | `/specs/{id}` | 204 / 404 / 409 |

#### `GET/POST /assignments`
#### `GET/PUT/DELETE /assignments/{assignment_id}`

| Método | Path | Códigos de respuesta |
|--------|------|----------------------|
| GET | `/assignments` | 200 — Lista paginada (skip, limit, max 100) |
| GET | `/assignments/{id}` | 200 / 404 |
| POST | `/assignments` | 201 — Crea asignación |
| PUT | `/assignments/{id}` | 200 / 404 / 400 |
| DELETE | `/assignments/{id}` | 204 / 404 |

#### `GET/POST /history`
#### `GET/PUT/DELETE /history/{history_id}`

| Método | Path | Códigos de respuesta |
|--------|------|----------------------|
| GET | `/history` | 200 — Lista paginada (skip, limit, max 100) |
| GET | `/history/{id}` | 200 / 404 |
| POST | `/history` | 201 — Crea registro histórico |
| PUT | `/history/{id}` | 200 / 404 / 400 |
| DELETE | `/history/{id}` | 403 — Historial inmutable |

---

### 8. Middleware — `app/middleware/cors.py`

Configura CORS para permitir peticiones desde el frontend en desarrollo:

- **Orígenes permitidos:** `http://localhost:5173`, `http://127.0.0.1:5173` (Vite default)
- **Métodos permitidos:** `*`
- **Headers permitidos:** `*`
- **Credentials:** habilitado

---

### 9. Manejadores de Errores — `app/main.py`

| Excepción | Código | Respuesta |
|-----------|--------|-----------|
| `BusinessError` | Variable (400-409) | `{"detail": "<mensaje>"}` |
| `SQLAlchemyError` | 500 | `{"detail": "database error"}` |
| `RequestValidationError` | 422 | Error estándar de FastAPI |

---

## Configuración del Entorno

`.env` (en `backend/`)
```env
DB_URL=sqlite:///./equip_tracker.db
API_KEY=  # Opcional. Si se deja vacío, se genera una automáticamente al iniciar.
```

---

## Instalación y Ejecución

```bash
# 1. Crear y activar entorno virtual
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar servidor de desarrollo
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`. La documentación interactiva (Swagger UI) en `http://localhost:8000/docs`.

### Autenticación

Todos los endpoints (excepto `/health` y `/docs`) requieren el header `X-API-Key`.  
Al iniciar el servidor, se mostrará en la terminal la API Key generada. Opcionalmente, defínela en `.env`:

```env
API_KEY=mi-clave-secreta
```

Ejemplo de uso con curl:

```bash
curl -H "X-API-Key: mi-clave-secreta" http://localhost:8000/operators
```

### Tests

```bash
cd backend
pytest tests/ -v
```

---

## Limitaciones Conocidas

- **SQLite unipersonal**: No soporta escrituras concurrentes. Para múltiples usuarios, migrar a PostgreSQL (cambiar `DB_URL` en `.env`).
- **Sin migraciones automáticas**: Los cambios de esquema requieren eliminar/recrear la BD o ejecutar SQL manual. Evaluar Alembic para futuras versiones.
- **Sin rate limiting**: No hay límite de requests. Recomendable agregar en despliegues públicos.
- **Autenticación simple**: API Key única. Sin roles ni usuarios. Escalar a JWT si se requiere multi-usuario.

---

## Licencia

MIT
