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

---

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

## GET

Obtención de información.

---

## POST

Creación de nuevos recursos.

---

## PUT

Actualización de información.

---

## DELETE

Eliminación de recursos.

---

# Entidades Principales

El sistema se compone de 4 entidades fundamentales:

```txt
Operadores
Equipos
especifiaciones_Equipo
Reparaciones
```

---

# Entidad: Operador

Representa trabajadores responsables de equipos tecnológicos.

## Propiedades

```txt
nombre
estado
cargo
trabajador_id
area
```

---

# Estado del Operador

El estado será controlado mediante valores predefinidos.

## Estados Iniciales

```txt
ACTIVO
INACTIVO
```

---

# Entidad: Equipo

Representa activos tecnológicos administrados por el sistema.

## Propiedades

```txt
numero_serie
modelo
especifiaciones
operador_asignado
historial_reparaciones
```

---

# Decisión Arquitectónica Importante

El campo:

```txt
numero_serie
```

funcionará como identificador único natural del sistema.

## Principio Aplicado

```txt
Clave primaria natural
```

No se utilizará un ID artificial para los equipos.

---

# Entidad: especifiaciones_Equipo

Representa las especificaciones técnicas de hardware.

## Propiedades

```txt
ram
procesador
almacenamiento
grafica
```

---

# Principio Aplicado

## Separación de Responsabilidades

Las especificaciones técnicas estarán desacopladas de la entidad principal `Equipo`.

---

# Entidad: Reparacion

Representa mantenimientos o incidencias técnicas.

## Propiedades

```txt
fecha_inicio
fecha_salida
razon
descripcion
operador_solicitante
```

---

# Principios de Historial

Las reparaciones representan:

* trazabilidad
* historial técnico
* auditoría

Por lo tanto normalmente no deben eliminarse.

---

# Relaciones del Sistema

## Operador → Equipos

```txt
1:N
```

Un operador puede poseer múltiples equipos asignados.

---

## Equipo → Reparaciones

```txt
1:N
```

Un equipo puede poseer múltiples registros históricos de mantenimiento.

---

## Equipo → especifiaciones_Equipo

```txt
1:1
```

Cada equipo posee un único bloque de especificaciones técnicas.

---

# Filosofía Arquitectónica

EquipTracker seguirá principios de:

* modularidad
* mantenibilidad
* escalabilidad
* separación de responsabilidades
* tipado fuerte
* arquitectura desacoplada

---

# Organización Backend

```txt
backend/
│
├── app/
│   │
│   ├── routes/
│   │   ├── operadores.py
│   │   ├── equipos.py
│   │   └── reparaciones.py
│   │
│   ├── models/
│   │   ├── operador.py
│   │   ├── equipo.py
│   │   ├── detalle_equipo.py
│   │   └── reparacion.py
│   │
│   ├── schemas/
│   │   ├── operador.py
│   │   ├── equipo.py
│   │   ├── detalle_equipo.py
│   │   └── reparacion.py
│   │
│   ├── services/
│   │   ├── operadores_service.py
│   │   ├── equipos_service.py
│   │   └── reparaciones_service.py
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

---

# Responsabilidades Backend

## routes/

Definición de endpoints REST.

---

## models/

Representación ORM y tablas SQL.

---

## schemas/

Validación y serialización de datos mediante Pydantic.

---

## services/

Lógica de negocio y procesos internos.

---

## database/

Configuración y conexión de base de datos.

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
│   │   │   ├── EquipoCard.tsx
│   │   │   └── OperadorCard.tsx
│   │   │
│   │   ├── modals/
│   │   │   ├── EquipoModal.tsx
│   │   │   └── OperadorModal.tsx
│   │   │
│   │   └── layout/
│   │       ├── Navbar.tsx
│   │       └── Sidebar.tsx
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Equipos.tsx
│   │   ├── Operadores.tsx
│   │   └── Reparaciones.tsx
│   │
│   ├── services/
│   │   └── api.ts
│   │
│   ├── hooks/
│   │   ├── useEquipos.ts
│   │   ├── useOperadores.ts
│   │   └── useReparaciones.ts
│   │
│   ├── types/
│   │   ├── Equipo.ts
│   │   ├── Operador.ts
│   │   ├── Reparacion.ts
│   │   └── especifiaciones_Equipo.ts
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

---

# Responsabilidades Frontend

## components/

Componentes reutilizables de interfaz.

---

## pages/

Pantallas principales del sistema.

---

## services/

Comunicación HTTP con la API mediante Axios.

---

## hooks/

Reutilización de lógica y manejo de estados.

---

## types/

Tipado y estructuras TypeScript.

---

## context/

Estados globales compartidos.

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

## REST

Comunicación desacoplada basada en recursos.

---

## Separación de Capas

Cada módulo posee responsabilidades específicas.

---

## Validación de Datos

Nunca confiar completamente en datos provenientes del frontend.

---

## Variables de Entorno

Los datos sensibles deben desacoplarse del código fuente.

## Ejemplo

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

El nombre:

```txt
EquipTracker
```

transmite:

* seguimiento
* control
* monitoreo
* trazabilidad

de activos tecnológicos empresariales.
