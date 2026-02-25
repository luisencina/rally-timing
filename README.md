# Rally Timing - Rally Innovation Lab Paraguay

Sistema digital de cronometraje y ranking para rally amateur. Primer sistema autonomo de analisis de rendimiento en tramo rural de Paraguay.

## Descripcion

**Rally Timing** es una plataforma offline-first que permite registrar pilotos, autos y pasadas cronometradas en un tramo de rally de 3km. Funciona 100% autonomo en una Raspberry Pi 4 sin necesidad de electricidad fija ni internet, creando una red WiFi local a la que los usuarios se conectan desde sus celulares o notebooks.

### Caracteristicas principales

- Registro y gestion de pilotos, autos y categorias
- Cronometraje dual: entrada manual + cronometro integrado en webapp
- Sistema de penalizaciones: agregar/quitar penalizaciones por pasada con motivo y tiempo adicional
- Ranking digital con filtros por categoria, condicion del tramo y fecha (usa tiempo final con penalizaciones)
- Dashboard con estadisticas y graficos (Chart.js)
- Almacenamiento local en SQLite (archivo unico, facil de respaldar)
- Preparado para sincronizacion a la nube cuando haya internet
- Interfaz web responsive (mobile-first, dark theme) en espanol

---

## Arquitectura Tecnica

### Stack

| Componente | Tecnologia |
|------------|-----------|
| Backend | Python 3 + Flask |
| Base de datos | SQLite |
| ORM | Flask-SQLAlchemy |
| Analisis | Pandas |
| Frontend | HTML/CSS/JS vanilla |
| Graficos | Chart.js (vendored, offline) |
| Infraestructura | Raspberry Pi 4 + power bank |

### Diagrama de arquitectura

```
┌─────────────────────────────────────────────────────┐
│                  Raspberry Pi 4                      │
│                                                      │
│  ┌──────────────┐       ┌──────────────────────┐    │
│  │ Flask API     │       │ HTTP Server           │    │
│  │ puerto 5050   │       │ puerto 8080           │    │
│  │               │       │                       │    │
│  │ /api/pilots   │       │ index.html (dashboard)│    │
│  │ /api/cars     │       │ pilots.html           │    │
│  │ /api/categories│      │ cars.html             │    │
│  │ /api/runs     │       │ categories.html       │    │
│  │ /api/rankings │       │ runs.html (cronometro)│    │
│  └──────┬───────┘       │ rankings.html         │    │
│         │                └──────────┬────────────┘    │
│         │                           │                 │
│  ┌──────▼───────┐          ┌───────▼──────────┐     │
│  │  SQLite DB    │          │  Chart.js         │     │
│  │  rally.db     │          │  (vendored)       │     │
│  └──────────────┘          └──────────────────┘     │
│                                                      │
│  WiFi Hotspot: "RallyLab" (hostapd + dnsmasq)      │
└─────────────────────────────────────────────────────┘
         ▲                          ▲
         │    Red WiFi local        │
    ┌────┴────┐              ┌─────┴─────┐
    │ Celular │              │ Notebook  │
    │ piloto  │              │ operador  │
    └─────────┘              └───────────┘
```

---

## Estructura del Proyecto

```
rally-timing/
├── README.md                    # Este archivo
├── .gitignore
├── .env.example                 # Variables de entorno de ejemplo
│
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py            # Configuracion (rutas DB, etc.)
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   ├── routes/
│   │   │   ├── __init__.py      # Blueprint registration
│   │   │   ├── pilots.py        # CRUD /api/pilots
│   │   │   ├── cars.py          # CRUD /api/cars
│   │   │   ├── categories.py    # CRUD /api/categories
│   │   │   ├── runs.py          # CRUD /api/runs + penalizaciones
│   │   │   └── rankings.py      # GET /api/rankings/*
│   │   └── services/
│   │       ├── __init__.py
│   │       └── ranking_service.py  # Calculos con Pandas
│   ├── migrations/
│   │   └── 001_initial_schema.sql  # Schema inicial
│   ├── tests/
│   │   ├── test_pilots.py
│   │   ├── test_runs.py
│   │   └── test_rankings.py
│   ├── requirements.txt
│   └── run.py                   # Punto de entrada del servidor
│
├── frontend/
│   ├── index.html               # Dashboard principal
│   ├── pilots.html              # Gestion de pilotos
│   ├── cars.html                # Gestion de autos
│   ├── categories.html          # Gestion de categorias
│   ├── runs.html                # Registro de pasadas + cronometro + penalizaciones
│   ├── rankings.html            # Rankings y graficos
│   ├── css/
│   │   └── styles.css           # Estilos mobile-first
│   ├── js/
│   │   ├── api.js               # Cliente API centralizado (fetch wrapper)
│   │   ├── pilots.js            # Logica pagina pilotos
│   │   ├── cars.js              # Logica pagina autos
│   │   ├── categories.js        # Logica pagina categorias
│   │   ├── runs.js              # Logica pasadas + cronometro + penalizaciones
│   │   ├── rankings.js          # Logica rankings + Chart.js
│   │   └── utils.js             # Formateo de tiempos, helpers
│   └── lib/
│       └── chart.min.js         # Chart.js v4 (vendored, sin CDN)
│
└── scripts/
    ├── setup_pi.sh              # Configuracion inicial Raspberry Pi
    ├── start_server.sh          # Iniciar servicios (Flask + frontend)
    └── backup_db.sh             # Respaldo de base de datos
```

---

## Base de Datos

### Modelo Entidad-Relacion

```
┌──────────┐       ┌──────────┐       ┌──────────┐   ┌────────────┐
│  pilots   │──1:N──│   cars   │       │ sync_log │   │ categories │
│           │       │          │       │          │   │            │
│ id (PK)   │       │ id (PK)  │       │ id (PK)  │   │ id (PK)    │
│ first_name│       │ brand    │       │ table    │   │ name       │
│ last_name │       │ model    │       │ record_id│   │ description│
│ nickname  │       │ year     │       │ action   │   │ is_active  │
│ phone     │       │ category │       │ synced   │   └────────────┘
│ email     │       │ pilot_id │       └──────────┘
│ license_no│       │ (FK)     │
│ notes     │       └─────┬────┘
│ is_active │             │
└─────┬─────┘             │
      │                   │
      │       ┌───────────┘
      │       │
      ▼       ▼
   ┌──────────────┐         ┌──────────────┐
   │     runs      │──1:N───│  penalties    │
   │               │         │              │
   │ id (PK)       │         │ id (PK)      │
   │ pilot_id (FK) │         │ run_id (FK)  │
   │ car_id (FK)   │         │ time_ms      │  ← Tiempo adicional
   │ run_date      │         │ reason       │  ← Motivo
   │ total_time_ms │         └──────────────┘
   │ track_condition│
   │ car_category  │
   │ notes         │
   │ is_valid      │
   │ source        │
   └───────────────┘

   final_time_ms = total_time_ms + SUM(penalties.time_ms)
```

### Decisiones de diseno

| Decision | Justificacion |
|----------|--------------|
| Tiempo en milisegundos (INTEGER) | Evita problemas de precision con flotantes. 2:34.567 = 154567 ms |
| `car_category` duplicado en `runs` | Un auto puede cambiar de categoria; el registro historico debe reflejar la categoria del dia de la pasada |
| Soft deletes (`is_active`) | Nunca perder datos historicos. Un piloto retirado mantiene sus pasadas en el ranking |
| Rankings computados al vuelo | Con <1000 registros, Pandas calcula rankings instantaneamente. No necesita tabla cache |
| `source` en runs | Distinguir si el tiempo fue ingresado manualmente o via cronometro. Util para control de calidad de datos |
| `sync_log` | Registra cada operacion para futura sincronizacion a la nube |
| Categorias dinamicas | Tabla `categories` permite al usuario definir sus propias categorias en lugar de tenerlas hardcodeadas |
| Penalizaciones como tabla separada | Una pasada puede tener N penalizaciones. `final_time_ms` se computa dinamicamente (`total_time_ms + SUM(penalties)`) en lugar de almacenarse, manteniendo la integridad de los datos |
| Rankings usan `final_time_ms` | Todos los calculos de ranking incluyen penalizaciones, reflejando el tiempo real de competencia |

### Schema SQL

```sql
CREATE TABLE IF NOT EXISTS pilots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    nickname TEXT,
    phone TEXT,
    email TEXT,
    license_number TEXT,
    notes TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER,
    plate_number TEXT,
    category TEXT NOT NULL,
    pilot_id INTEGER,
    notes TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (pilot_id) REFERENCES pilots(id)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pilot_id INTEGER NOT NULL,
    car_id INTEGER NOT NULL,
    run_date TEXT NOT NULL,
    total_time_ms INTEGER NOT NULL,
    track_condition TEXT NOT NULL
        CHECK(track_condition IN ('dry', 'wet', 'humid')),
    car_category TEXT NOT NULL,
    notes TEXT,
    is_valid INTEGER DEFAULT 1,
    source TEXT DEFAULT 'manual'
        CHECK(source IN ('manual', 'stopwatch')),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (pilot_id) REFERENCES pilots(id),
    FOREIGN KEY (car_id) REFERENCES cars(id)
);

CREATE TABLE IF NOT EXISTS penalties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    time_ms INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    action TEXT NOT NULL
        CHECK(action IN ('create', 'update', 'delete')),
    synced INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_runs_pilot ON runs(pilot_id);
CREATE INDEX IF NOT EXISTS idx_runs_date ON runs(run_date);
CREATE INDEX IF NOT EXISTS idx_runs_condition ON runs(track_condition);
CREATE INDEX IF NOT EXISTS idx_runs_category ON runs(car_category);
CREATE INDEX IF NOT EXISTS idx_penalties_run ON penalties(run_id);
CREATE INDEX IF NOT EXISTS idx_sync_pending ON sync_log(synced) WHERE synced = 0;
```

---

## API REST

Base URL: `http://<ip-raspberry>:5050/api`

Formato de respuesta estandar:
```json
// Exito
{"success": true, "data": { ... }}

// Error
{"success": false, "error": "Mensaje de error"}
```

### Pilotos

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/pilots` | Listar pilotos activos. Filtro: `?search=nombre` |
| GET | `/api/pilots/<id>` | Detalle de piloto con estadisticas |
| POST | `/api/pilots` | Crear piloto |
| PUT | `/api/pilots/<id>` | Actualizar piloto |
| DELETE | `/api/pilots/<id>` | Desactivar piloto (soft delete) |

### Autos

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/cars` | Listar autos. Filtro: `?pilot_id=`, `?category=` |
| GET | `/api/cars/<id>` | Detalle de auto |
| POST | `/api/cars` | Crear auto |
| PUT | `/api/cars/<id>` | Actualizar auto |
| DELETE | `/api/cars/<id>` | Desactivar auto (soft delete) |

### Categorias

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/categories` | Listar categorias activas. Filtro: `?search=nombre` |
| GET | `/api/categories/<id>` | Detalle de categoria |
| POST | `/api/categories` | Crear categoria (nombre unico) |
| PUT | `/api/categories/<id>` | Actualizar categoria |
| DELETE | `/api/categories/<id>` | Desactivar categoria (soft delete) |

### Pasadas (Runs)

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/runs` | Listar pasadas. Filtros: `?pilot_id=`, `?date=`, `?condition=`, `?category=` |
| GET | `/api/runs/<id>` | Detalle de pasada (incluye penalizaciones) |
| POST | `/api/runs` | Registrar pasada (manual o cronometro) |
| PUT | `/api/runs/<id>` | Corregir pasada |
| DELETE | `/api/runs/<id>` | Invalidar pasada |

### Penalizaciones (anidadas bajo pasadas)

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/runs/<id>/penalties` | Listar penalizaciones de una pasada |
| POST | `/api/runs/<id>/penalties` | Agregar penalizacion (time_ms + reason) |
| DELETE | `/api/runs/<id>/penalties/<pid>` | Quitar penalizacion |

**Body de ejemplo para POST /api/runs:**
```json
{
    "pilot_id": 1,
    "car_id": 2,
    "run_date": "2026-03-15",
    "total_time_ms": 154567,
    "track_condition": "dry",
    "notes": "Buena pasada, mejoro en curva 3",
    "source": "stopwatch"
}
```

### Rankings (solo lectura)

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/rankings/best-times` | Mejor tiempo por piloto. Filtros: `?condition=`, `?category=` |
| GET | `/api/rankings/history/<pilot_id>` | Progresion de tiempos de un piloto |
| GET | `/api/rankings/records` | Records: general, por categoria, por condicion |
| GET | `/api/rankings/summary` | Stats para dashboard: total pasadas, pilotos, record actual |

---

## Frontend

### Paginas

#### 1. Dashboard (`index.html`)
- Total de pilotos registrados
- Total de pasadas
- Record actual del tramo (mejor tiempo, quien, cuando)
- Ultimas 5 pasadas
- Grafico de actividad (pasadas por semana)

#### 2. Pilotos (`pilots.html`)
- Tabla con nombre, apodo, total pasadas, mejor tiempo
- Boton "Agregar Piloto" abre formulario/modal
- Editar y desactivar por fila

#### 3. Autos (`cars.html`)
- Tabla con marca, modelo, categoria, piloto asignado
- CRUD con formulario/modal
- Filtro por categoria (cargado dinamicamente desde la API de categorias)

#### 4. Categorias (`categories.html`)
- Tabla con nombre y descripcion de categoria
- CRUD con modal (nombre unico, validacion case-insensitive)
- Las categorias definidas aqui aparecen en los selects de autos y filtros de rankings

#### 5. Pasadas (`runs.html`) - **Pagina principal**
- Seleccion de piloto y auto (dropdowns con agrupacion por piloto)
- Fecha (default: hoy), condicion del tramo (radio buttons)
- **Dos modos de ingreso de tiempo:**
  - **Manual:** campos minutos / segundos / milisegundos
  - **Cronometro:** boton grande INICIAR/DETENER con display en tiempo real
- Notas (textarea)
- Tabla de pasadas del dia actual con columnas: Piloto, Auto, Tiempo, Penalizacion, Tiempo Final, Condicion, Acciones
- **Modal de penalizaciones:** desde cada pasada se pueden agregar/quitar penalizaciones indicando tiempo adicional (min/seg/ms) y motivo
- El tiempo final (`final_time_ms`) se muestra resaltado cuando hay penalizaciones

#### 6. Rankings (`rankings.html`)
- Filtros: categoria, condicion, rango de fechas
- Tabla de ranking (posicion, piloto, auto, mejor tiempo, fecha)
- Grafico de barras: mejores tiempos por piloto
- Grafico de linea: progresion de un piloto seleccionado
- Seccion de records

### Cronometro integrado

El cronometro usa `performance.now()` para precision sub-milisegundo:

```javascript
let startTime = null;
let isRunning = false;

function startStopwatch() {
    startTime = performance.now();
    isRunning = true;
    updateDisplay(); // requestAnimationFrame loop
}

function stopStopwatch() {
    const elapsedMs = Math.round(performance.now() - startTime);
    isRunning = false;
    fillTimeFields(elapsedMs); // Auto-rellena el formulario
}
```

---

## Despliegue

### En Raspberry Pi (produccion en el tramo)

1. La Raspberry Pi crea red WiFi propia con `hostapd` + `dnsmasq`
   - SSID: `RallyLab`
   - Sin internet, solo red local
2. Flask corre en puerto 5050 (API)
3. Frontend servido en puerto 8080 (`python -m http.server`)
4. Usuarios se conectan al WiFi y abren `http://192.168.4.1:8080`

### En desarrollo (notebook)

```bash
# Terminal 1: Backend
cd backend
python run.py

# Terminal 2: Frontend
cd frontend
python -m http.server 8080
```

Abrir `http://localhost:8080`

---

## Sincronizacion Hibrida (post-MVP)

### Estrategia: Change Log + Push Manual

1. Cada operacion de crear/actualizar/eliminar escribe en `sync_log`
2. Cuando hay internet, el usuario presiona "Sincronizar"
3. El sistema empaqueta cambios pendientes como JSON y los envia al servidor cloud
4. La Raspberry Pi es **fuente unica de verdad**, la nube es espejo de solo lectura

```
[Raspberry Pi local]                    [Servidor nube (futuro)]
       │                                        │
  Crea pasada → SQLite + sync_log               │
       │                                        │
  ... (sin internet en el tramo) ...             │
       │                                        │
  Click "Sincronizar" (con internet)             │
  → POST /api/sync/receive ──────────────────►   │
       │                               inserta datos
  ◄── marca sync_log como sincronizado ──────────┘
```

---

## Plan de Implementacion por Fases

### Fase 1 - Fundacion
- [x] Crear estructura de carpetas y README
- [x] Inicializar git, .gitignore, requirements.txt, .env.example
- [x] Flask app factory con CORS y health check
- [x] Schema SQLite + modelos SQLAlchemy
- [x] CRUD Pilotos (API + pagina frontend)
- [x] CRUD Autos (API + pagina frontend)
- [x] CRUD Categorias (API + pagina frontend)

### Fase 2 - Core
- [x] CRUD Pasadas con entrada manual de tiempo
- [x] Cronometro integrado en frontend
- [x] Validaciones frontend y backend
- [x] Sistema de penalizaciones (agregar/quitar por pasada, con motivo)

### Fase 3 - Rankings y Dashboard
- [x] Servicio de rankings con Pandas (usa final_time_ms con penalizaciones)
- [x] API endpoints de rankings
- [x] Pagina rankings con Chart.js
- [x] Dashboard con estadisticas

### Fase 4 - Deployment
- [x] Scripts para Raspberry Pi (setup WiFi, auto-start, backup)
- [x] Infraestructura de sync_log
- [ ] Prueba real en el tramo con 2 pilotos

### Futuro (post-MVP)
- [ ] Sincronizacion a la nube
- [ ] Generacion de reportes PDF
- [ ] Sectores intermedios (dividir el tramo en segmentos)
- [ ] Rankings publicos en web
- [ ] Procesamiento de archivos GPX

---

## Requisitos

### Hardware minimo
- Raspberry Pi 4 (o notebook para desarrollo)
- Power bank
- Celular o notebook para acceder a la webapp

### Software
- Python 3.9+
- pip

### Instalacion

```bash
# Clonar repositorio
git clone <url-del-repo>
cd rally-timing

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python run.py

# Frontend (otra terminal)
cd frontend
python -m http.server 8080
```

---

## Contexto del Proyecto

Este proyecto nace como iniciativa del **Rally Innovation Lab Paraguay**, impulsado desde la comision directiva del Centro de Pilotos. El objetivo es profesionalizar el entrenamiento en el tramo rural de 3km mediante tecnologia accesible y autonoma.

**Vision a 12 meses:**
- Base historica de tiempos
- Ranking anual oficial
- Hackathon "Rally Tech Challenge"
- Sponsor tecnologico
- Cobertura en medios
- Tramo digitalizado exportable a simuladores

---

## Licencia

Por definir.
