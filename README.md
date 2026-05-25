# EquipTracker

> Sistema de gestión, asignación y mantenimiento de equipos tecnológicos orientado a entornos empresariales.

---

# Objetivo del Proyecto

EquipTracker busca centralizar la administración de:

* operadores
* equipos tecnológicos
* asignaciones
* mantenimientos
* historial técnico

permitiendo mantener trazabilidad completa sobre los activos tecnológicos de una organización.

---

# Dominio del Sistema

```txt
IT Asset Management
```

Gestión de activos tecnológicos empresariales.

---

# Arquitectura General

## Paradigma

```txt
Cliente → API REST → Base de Datos
```

---

# Stack Tecnológico Oficial

## Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite

## Frontend

* React
* TypeScript
* Axios
* Vite

---

# Tipo de Arquitectura

## REST API

La comunicación entre frontend y backend será realizada mediante HTTP utilizando arquitectura REST.

---

# Métodos HTTP Utilizados

| Método | Uso |
|--------|-----|
| `GET` | Obtención de información |
| `POST` | Creación de nuevos recursos |
| `PUT` | Actualización de información |
| `DELETE` | Eliminación de recursos |

---

# Entidades Principales

El sistema se compone de 5 entidades fundamentales:

```txt
Operator
Equipment
Equipment Specs
Equipment Assignment
Equipment History
```

## Relaciones

```
Equipment ──────────── Equipment Specs
    │
    ├── Equipment Assignment ──── Operator
    │
    └── Equipment History
```

| Relación | Tipo | Descripción |
|----------|------|-------------|
| Equipment → Equipment Specs | 1:1 | Cada equipo tiene un único bloque de especificaciones |
| Operator → Equipment Assignment | 1:N | Un operador puede tener múltiples asignaciones |
| Equipment → Equipment Assignment | 1:N | Un equipo puede tener múltiples asignaciones históricas |
| Equipment → Equipment History | 1:N | Un equipo puede tener múltiples registros de historial |

---

# Entidad: Operator

Representa a las personas que pueden recibir equipos asignados dentro de la organización.

## Propiedades

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | Identificador único del operador |
| `name` | string | Nombre completo |
| `department` | string | Área o equipo dentro de la organización |
| `position` | string | Cargo o rol del operador |

```json
{
  "id": 1,
  "name": "Ana López",
  "department": "Atención al Cliente",
  "position": "Operador"
}
```

---

# Entidad: Equipment

Representa un dispositivo físico registrado en el sistema. Cada equipo es identificado de forma única por su número de serie y está vinculado a un registro de especificaciones.

## Propiedades

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | Identificador interno único |
| `serial` | string | Número de serie físico del dispositivo |
| `brand` | string | Nombre del fabricante |
| `model` | string | Modelo del dispositivo |
| `created_at` | datetime | Fecha y hora de registro en el sistema |
| `specs_id` | integer | Referencia al registro de `Equipment Specs` asociado |

```json
{
  "id": 1,
  "serial": "10000",
  "brand": "Lenovo",
  "model": "G50",
  "created_at": "2026-12-09T08:53:00",
  "specs_id": 1
}
```

> **Nota:** El estado del equipo (activo, en reparación, retirado) se deriva de sus registros de asignación e historial, no se almacena directamente aquí.

---

# Entidad: Equipment Specs

Almacena las especificaciones técnicas de un dispositivo. Está desacoplada de `Equipment` para permitir su reutilización en dispositivos con hardware idéntico.

## Propiedades

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | Identificador único del bloque de especificaciones |
| `cpu` | object | Información del procesador |
| `ram` | object | Capacidad y configuración de memoria |
| `storage` | object | Capacidad y tipo de almacenamiento |
| `graphics` | object | Información de la unidad gráfica (integrada o dedicada) |

```json
{
  "id": 1,
  "cpu": {
    "brand": "Intel",
    "model": "Core i5"
  },
  "ram": {
    "capacity": {
      "value": 16,
      "unit": "GB"
    },
    "mode": "dual-channel"
  },
  "storage": {
    "capacity": {
      "value": 500,
      "unit": "GB"
    },
    "type": "HDD"
  },
  "graphics": {
    "brand": "Intel",
    "model": "UHD Graphics",
    "type": "integrated",
    "memory": {
      "value": 128,
      "unit": "MB"
    }
  }
}
```

> **Nota:** `graphics.type` puede ser `"integrated"` o `"dedicated"`. Para GPUs integradas, `graphics.memory` refleja la memoria compartida del sistema.

---

# Entidad: Equipment Assignment

Registra la relación entre un equipo y el operador que lo utiliza. Una asignación se considera **activa** cuando `returned_at` es `null`.

## Propiedades

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | Identificador único de la asignación |
| `equipment_id` | integer | Referencia al `Equipment` asignado |
| `operator_id` | integer | Referencia al `Operator` que recibe el equipo |
| `assigned_by` | integer | Referencia al admin o usuario que realizó la asignación |
| `assigned_at` | datetime | Fecha y hora en que se asignó el equipo |
| `returned_at` | datetime \| null | Fecha y hora de devolución. `null` indica que sigue asignado |
| `status` | string | Estado de la asignación: `active` o `inactive` |

```json
{
  "id": 1,
  "equipment_id": 1,
  "operator_id": 1,
  "assigned_by": 1,
  "assigned_at": "2026-05-25T10:00:00",
  "returned_at": null,
  "status": "active"
}
```

> **Regla:** Al cerrar una asignación, `returned_at` debe registrar la fecha de devolución y `status` debe cambiar a `"inactive"`.

---

# Entidad: Equipment History

Registra eventos relacionados con un equipo a lo largo de su ciclo de vida: reparaciones, mantenimientos, actualizaciones, etc. Los registros de historial normalmente no deben eliminarse ya que representan trazabilidad y auditoría.

## Propiedades

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | Identificador único del registro |
| `equipment_id` | integer | Referencia al `Equipment` relacionado |
| `type` | string | Categoría del evento: `repair`, `maintenance`, `upgrade`, etc. |
| `reason` | string | Descripción del motivo del evento |
| `status` | string | Estado del evento: `open` o `closed` |
| `reported_by` | integer | Referencia al operador o usuario que reportó el evento |
| `technician_id` | integer | Referencia al técnico que atendió el evento |
| `created_at` | datetime | Fecha y hora en que se reportó el evento |
| `resolved_at` | datetime \| null | Fecha y hora de resolución. `null` si aún está abierto |

```json
{
  "id": 55,
  "equipment_id": 1,
  "type": "repair",
  "reason": "Placa en corto por humedad",
  "status": "closed",
  "reported_by": 1,
  "technician_id": 1,
  "created_at": "2026-02-12T09:23:00",
  "resolved_at": "2026-02-13T07:00:00"
}
```

> **Regla:** Cuando `status` es `"closed"`, `resolved_at` debe tener un valor datetime válido.

---

# Organización Backend

```txt
backend/
│
├── app/
│   │
│   ├── routes/
│   │   ├── operators.py
│   │   ├── equipment.py
│   │   ├── assignments.py
│   │   └── history.py
│   │
│   ├── models/
│   │   ├── operator.py
│   │   ├── equipment.py
│   │   ├── equipment_specs.py
│   │   ├── equipment_assignment.py
│   │   └── equipment_history.py
│   │
│   ├── schemas/
│   │   ├── operator.py
│   │   ├── equipment.py
│   │   ├── equipment_specs.py
│   │   ├── equipment_assignment.py
│   │   └── equipment_history.py
│   │
│   ├── services/
│   │   ├── operators_service.py
│   │   ├── equipment_service.py
│   │   ├── assignments_service.py
│   │   └── history_service.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── config.py
│   │
│   ├── middleware/
│   │   └── cors.py
│   │
│   └── main.py
│
├── requirements.txt
├── .env
└── README.md
```

## Responsabilidades

| Módulo | Responsabilidad |
|--------|----------------|
| `routes/` | Definición de endpoints REST |
| `models/` | Representación ORM y tablas SQL |
| `schemas/` | Validación y serialización de datos mediante Pydantic |
| `services/` | Lógica de negocio y procesos internos |
| `database/` | Configuración y conexión de base de datos |

---

# Organización Frontend

```txt
frontend/
│
├── public/
│
├── src/
│   │
│   ├── components/
│   │   ├── cards/
│   │   │   ├── EquipmentCard.tsx
│   │   │   └── OperatorCard.tsx
│   │   │
│   │   ├── modals/
│   │   │   ├── EquipmentModal.tsx
│   │   │   ├── AssignmentModal.tsx
│   │   │   └── OperatorModal.tsx
│   │   │
│   │   └── layout/
│   │       ├── Navbar.tsx
│   │       └── Sidebar.tsx
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Equipment.tsx
│   │   ├── Operators.tsx
│   │   ├── Assignments.tsx
│   │   └── History.tsx
│   │
│   ├── services/
│   │   └── api.ts
│   │
│   ├── hooks/
│   │   ├── useEquipment.ts
│   │   ├── useOperators.ts
│   │   ├── useAssignments.ts
│   │   └── useHistory.ts
│   │
│   ├── types/
│   │   ├── Equipment.ts
│   │   ├── EquipmentSpecs.ts
│   │   ├── EquipmentAssignment.ts
│   │   ├── EquipmentHistory.ts
│   │   └── Operator.ts
│   │
│   ├── context/
│   │   └── AppContext.tsx
│   │
│   ├── App.tsx
│   └── main.tsx
│
├── .env
├── package.json
└── vite.config.ts
```

## Responsabilidades

| Módulo | Responsabilidad |
|--------|----------------|
| `components/` | Componentes reutilizables de interfaz |
| `pages/` | Pantallas principales del sistema |
| `services/` | Comunicación HTTP con la API mediante Axios |
| `hooks/` | Reutilización de lógica y manejo de estados |
| `types/` | Tipado y estructuras TypeScript |
| `context/` | Estados globales compartidos |

---

# Flujo General del Sistema

```txt
Frontend React
        ↓
Axios HTTP Requests
        ↓
FastAPI REST API
        ↓
Services
        ↓
SQLAlchemy ORM
        ↓
SQLite Database
```

---

# Principios Técnicos Aplicados

| Principio | Descripción |
|-----------|-------------|
| REST | Comunicación desacoplada basada en recursos |
| Separación de capas | Cada módulo posee responsabilidades específicas |
| Validación de datos | Nunca confiar completamente en datos del frontend |
| Variables de entorno | Los datos sensibles se desacoplan del código fuente |
| Historial inmutable | Los registros de `Equipment History` no deben eliminarse |

```env
VITE_API_URL=
DB_URL=
SECRET_KEY=
```

---

# Objetivos Técnicos del Proyecto

EquipTracker busca servir como práctica real de:

* arquitectura backend
* diseño REST
* modelado relacional
* SQLAlchemy
* FastAPI
* React + TypeScript
* consumo de APIs
* separación de responsabilidades
* organización profesional
* tipado fuerte
* mantenimiento escalable

---

# Identidad Conceptual

El nombre `EquipTracker` transmite seguimiento, control, monitoreo y trazabilidad de activos tecnológicos empresariales.
