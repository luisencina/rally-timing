SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Rally Timing API",
        "description": "API de cronometraje y ranking para rally amateur - Rally Innovation Lab Paraguay",
        "version": "1.0.0",
        "contact": {"name": "Rally Innovation Lab Paraguay"},
    },
    "basePath": "/api",
    "schemes": ["http"],
    "tags": [
        {"name": "Health", "description": "Estado del servidor"},
        {"name": "Pilotos", "description": "Gestion de pilotos"},
        {"name": "Autos", "description": "Gestion de autos"},
        {"name": "Categorias", "description": "Gestion de categorias"},
        {"name": "Pasadas", "description": "Registro y gestion de pasadas cronometradas"},
        {"name": "Penalizaciones", "description": "Penalizaciones por pasada"},
        {"name": "Rankings", "description": "Rankings, records y estadisticas"},
    ],
    "definitions": {
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "data": {"type": "object"},
            },
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": False},
                "error": {"type": "string", "example": "Mensaje de error"},
            },
        },
        "Pilot": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "first_name": {"type": "string", "example": "Carlos"},
                "last_name": {"type": "string", "example": "Martinez"},
                "nickname": {"type": "string", "example": "Carlitos", "x-nullable": True},
                "phone": {"type": "string", "example": "+595981123456", "x-nullable": True},
                "email": {"type": "string", "example": "carlos@email.com", "x-nullable": True},
                "license_number": {"type": "string", "example": "PY-2024-001", "x-nullable": True},
                "notes": {"type": "string", "x-nullable": True},
                "is_active": {"type": "integer", "example": 1},
                "created_at": {"type": "string", "example": "2026-02-24T12:00:00"},
                "updated_at": {"type": "string", "example": "2026-02-24T12:00:00"},
            },
        },
        "PilotInput": {
            "type": "object",
            "required": ["first_name", "last_name"],
            "properties": {
                "first_name": {"type": "string", "example": "Carlos"},
                "last_name": {"type": "string", "example": "Martinez"},
                "nickname": {"type": "string", "example": "Carlitos"},
                "phone": {"type": "string", "example": "+595981123456"},
                "email": {"type": "string", "example": "carlos@email.com"},
                "license_number": {"type": "string", "example": "PY-2024-001"},
                "notes": {"type": "string"},
            },
        },
        "Car": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "brand": {"type": "string", "example": "Toyota"},
                "model": {"type": "string", "example": "Yaris GR"},
                "year": {"type": "integer", "example": 2023, "x-nullable": True},
                "plate_number": {"type": "string", "x-nullable": True},
                "category": {"type": "string", "example": "N"},
                "pilot_id": {"type": "integer", "example": 1, "x-nullable": True},
                "pilot_name": {"type": "string", "example": "Carlos Martinez", "x-nullable": True},
                "notes": {"type": "string", "x-nullable": True},
                "is_active": {"type": "integer", "example": 1},
                "created_at": {"type": "string"},
                "updated_at": {"type": "string"},
            },
        },
        "CarInput": {
            "type": "object",
            "required": ["brand", "model", "category"],
            "properties": {
                "brand": {"type": "string", "example": "Toyota"},
                "model": {"type": "string", "example": "Yaris GR"},
                "year": {"type": "integer", "example": 2023},
                "plate_number": {"type": "string"},
                "category": {"type": "string", "example": "N"},
                "pilot_id": {"type": "integer", "example": 1},
                "notes": {"type": "string"},
            },
        },
        "Category": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "N"},
                "description": {"type": "string", "example": "Nacional", "x-nullable": True},
                "is_active": {"type": "integer", "example": 1},
                "created_at": {"type": "string"},
                "updated_at": {"type": "string"},
            },
        },
        "CategoryInput": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string", "example": "N"},
                "description": {"type": "string", "example": "Nacional"},
            },
        },
        "Penalty": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "run_id": {"type": "integer", "example": 1},
                "time_ms": {"type": "integer", "example": 5000},
                "reason": {"type": "string", "example": "Derribo de cono"},
                "created_at": {"type": "string"},
            },
        },
        "PenaltyInput": {
            "type": "object",
            "required": ["time_ms", "reason"],
            "properties": {
                "time_ms": {"type": "integer", "example": 5000, "description": "Tiempo de penalizacion en milisegundos"},
                "reason": {"type": "string", "example": "Derribo de cono"},
            },
        },
        "Run": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "pilot_id": {"type": "integer", "example": 1},
                "car_id": {"type": "integer", "example": 1},
                "run_date": {"type": "string", "example": "2026-03-15"},
                "total_time_ms": {"type": "integer", "example": 154567},
                "penalty_total_ms": {"type": "integer", "example": 5000},
                "final_time_ms": {"type": "integer", "example": 159567},
                "penalties": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Penalty"},
                },
                "track_condition": {"type": "string", "enum": ["dry", "wet", "humid"], "example": "dry"},
                "car_category": {"type": "string", "example": "N"},
                "notes": {"type": "string", "x-nullable": True},
                "is_valid": {"type": "integer", "example": 1},
                "source": {"type": "string", "enum": ["manual", "stopwatch"], "example": "stopwatch"},
                "pilot_name": {"type": "string", "example": "Carlos Martinez"},
                "car_name": {"type": "string", "example": "Toyota Yaris GR"},
                "created_at": {"type": "string"},
                "updated_at": {"type": "string"},
            },
        },
        "RunInput": {
            "type": "object",
            "required": ["pilot_id", "car_id", "run_date", "total_time_ms", "track_condition"],
            "properties": {
                "pilot_id": {"type": "integer", "example": 1},
                "car_id": {"type": "integer", "example": 1},
                "run_date": {"type": "string", "example": "2026-03-15"},
                "total_time_ms": {"type": "integer", "example": 154567, "description": "Tiempo total en milisegundos"},
                "track_condition": {"type": "string", "enum": ["dry", "wet", "humid"], "example": "dry"},
                "notes": {"type": "string", "example": "Buena pasada"},
                "source": {"type": "string", "enum": ["manual", "stopwatch"], "example": "stopwatch", "default": "manual"},
            },
        },
    },
    "paths": {
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check",
                "description": "Verifica que el servidor esta corriendo",
                "responses": {
                    "200": {
                        "description": "Servidor OK",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {
                                    "type": "object",
                                    "properties": {"status": {"type": "string", "example": "ok"}},
                                },
                            },
                        },
                    }
                },
            }
        },
        # --- Pilots ---
        "/pilots": {
            "get": {
                "tags": ["Pilotos"],
                "summary": "Listar pilotos activos",
                "parameters": [
                    {
                        "name": "search",
                        "in": "query",
                        "type": "string",
                        "description": "Buscar por nombre, apellido o apodo",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Lista de pilotos",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Pilot"}},
                            },
                        },
                    }
                },
            },
            "post": {
                "tags": ["Pilotos"],
                "summary": "Crear piloto",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/PilotInput"},
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Piloto creado",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"$ref": "#/definitions/Pilot"},
                            },
                        },
                    },
                    "400": {"description": "Datos invalidos", "schema": {"$ref": "#/definitions/ErrorResponse"}},
                },
            },
        },
        "/pilots/{pilot_id}": {
            "get": {
                "tags": ["Pilotos"],
                "summary": "Obtener piloto por ID",
                "parameters": [{"name": "pilot_id", "in": "path", "type": "integer", "required": True}],
                "responses": {
                    "200": {"description": "Detalle del piloto"},
                    "404": {"description": "Piloto no encontrado", "schema": {"$ref": "#/definitions/ErrorResponse"}},
                },
            },
            "put": {
                "tags": ["Pilotos"],
                "summary": "Actualizar piloto",
                "parameters": [
                    {"name": "pilot_id", "in": "path", "type": "integer", "required": True},
                    {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/PilotInput"}},
                ],
                "responses": {
                    "200": {"description": "Piloto actualizado"},
                    "404": {"description": "Piloto no encontrado"},
                },
            },
            "delete": {
                "tags": ["Pilotos"],
                "summary": "Desactivar piloto (soft delete)",
                "parameters": [{"name": "pilot_id", "in": "path", "type": "integer", "required": True}],
                "responses": {
                    "200": {"description": "Piloto desactivado"},
                    "404": {"description": "Piloto no encontrado"},
                },
            },
        },
        # --- Cars ---
        "/cars": {
            "get": {
                "tags": ["Autos"],
                "summary": "Listar autos activos",
                "parameters": [
                    {"name": "pilot_id", "in": "query", "type": "integer", "description": "Filtrar por piloto"},
                    {"name": "category", "in": "query", "type": "string", "description": "Filtrar por categoria"},
                ],
                "responses": {
                    "200": {
                        "description": "Lista de autos",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Car"}},
                            },
                        },
                    }
                },
            },
            "post": {
                "tags": ["Autos"],
                "summary": "Crear auto",
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/CarInput"}}
                ],
                "responses": {
                    "201": {"description": "Auto creado"},
                    "400": {"description": "Datos invalidos"},
                },
            },
        },
        "/cars/{car_id}": {
            "get": {
                "tags": ["Autos"],
                "summary": "Obtener auto por ID",
                "parameters": [{"name": "car_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Detalle del auto"}, "404": {"description": "Auto no encontrado"}},
            },
            "put": {
                "tags": ["Autos"],
                "summary": "Actualizar auto",
                "parameters": [
                    {"name": "car_id", "in": "path", "type": "integer", "required": True},
                    {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/CarInput"}},
                ],
                "responses": {"200": {"description": "Auto actualizado"}, "404": {"description": "Auto no encontrado"}},
            },
            "delete": {
                "tags": ["Autos"],
                "summary": "Desactivar auto (soft delete)",
                "parameters": [{"name": "car_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Auto desactivado"}, "404": {"description": "Auto no encontrado"}},
            },
        },
        # --- Categories ---
        "/categories": {
            "get": {
                "tags": ["Categorias"],
                "summary": "Listar categorias activas",
                "parameters": [
                    {"name": "search", "in": "query", "type": "string", "description": "Buscar por nombre"}
                ],
                "responses": {
                    "200": {
                        "description": "Lista de categorias",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Category"}},
                            },
                        },
                    }
                },
            },
            "post": {
                "tags": ["Categorias"],
                "summary": "Crear categoria",
                "description": "El nombre debe ser unico (case-insensitive)",
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/CategoryInput"}}
                ],
                "responses": {
                    "201": {"description": "Categoria creada"},
                    "400": {"description": "Nombre duplicado o datos invalidos"},
                },
            },
        },
        "/categories/{category_id}": {
            "get": {
                "tags": ["Categorias"],
                "summary": "Obtener categoria por ID",
                "parameters": [{"name": "category_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Detalle de categoria"}, "404": {"description": "No encontrada"}},
            },
            "put": {
                "tags": ["Categorias"],
                "summary": "Actualizar categoria",
                "parameters": [
                    {"name": "category_id", "in": "path", "type": "integer", "required": True},
                    {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/CategoryInput"}},
                ],
                "responses": {"200": {"description": "Categoria actualizada"}, "404": {"description": "No encontrada"}},
            },
            "delete": {
                "tags": ["Categorias"],
                "summary": "Desactivar categoria (soft delete)",
                "parameters": [{"name": "category_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Categoria desactivada"}, "404": {"description": "No encontrada"}},
            },
        },
        # --- Runs ---
        "/runs": {
            "get": {
                "tags": ["Pasadas"],
                "summary": "Listar pasadas validas",
                "parameters": [
                    {"name": "pilot_id", "in": "query", "type": "integer", "description": "Filtrar por piloto"},
                    {"name": "date", "in": "query", "type": "string", "description": "Filtrar por fecha (YYYY-MM-DD)"},
                    {"name": "condition", "in": "query", "type": "string", "enum": ["dry", "wet", "humid"], "description": "Filtrar por condicion"},
                    {"name": "category", "in": "query", "type": "string", "description": "Filtrar por categoria del auto"},
                ],
                "responses": {
                    "200": {
                        "description": "Lista de pasadas",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Run"}},
                            },
                        },
                    }
                },
            },
            "post": {
                "tags": ["Pasadas"],
                "summary": "Registrar pasada",
                "description": "Registra una pasada cronometrada (manual o stopwatch). El car_category se copia automaticamente del auto.",
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/RunInput"}}
                ],
                "responses": {
                    "201": {
                        "description": "Pasada registrada",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"$ref": "#/definitions/Run"},
                            },
                        },
                    },
                    "400": {"description": "Datos invalidos"},
                    "404": {"description": "Piloto o auto no encontrado"},
                },
            },
        },
        "/runs/{run_id}": {
            "get": {
                "tags": ["Pasadas"],
                "summary": "Obtener pasada por ID",
                "description": "Incluye penalizaciones y tiempo final calculado",
                "parameters": [{"name": "run_id", "in": "path", "type": "integer", "required": True}],
                "responses": {
                    "200": {
                        "description": "Detalle de pasada con penalizaciones",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"$ref": "#/definitions/Run"},
                            },
                        },
                    },
                    "404": {"description": "Pasada no encontrada"},
                },
            },
            "put": {
                "tags": ["Pasadas"],
                "summary": "Corregir pasada",
                "parameters": [
                    {"name": "run_id", "in": "path", "type": "integer", "required": True},
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "total_time_ms": {"type": "integer"},
                                "track_condition": {"type": "string", "enum": ["dry", "wet", "humid"]},
                                "run_date": {"type": "string"},
                                "notes": {"type": "string"},
                            },
                        },
                    },
                ],
                "responses": {"200": {"description": "Pasada actualizada"}, "404": {"description": "Pasada no encontrada"}},
            },
            "delete": {
                "tags": ["Pasadas"],
                "summary": "Invalidar pasada",
                "description": "Soft delete: marca is_valid=0",
                "parameters": [{"name": "run_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Pasada invalidada"}, "404": {"description": "Pasada no encontrada"}},
            },
        },
        # --- Penalties ---
        "/runs/{run_id}/penalties": {
            "get": {
                "tags": ["Penalizaciones"],
                "summary": "Listar penalizaciones de una pasada",
                "parameters": [{"name": "run_id", "in": "path", "type": "integer", "required": True}],
                "responses": {
                    "200": {
                        "description": "Lista de penalizaciones",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Penalty"}},
                            },
                        },
                    },
                    "404": {"description": "Pasada no encontrada"},
                },
            },
            "post": {
                "tags": ["Penalizaciones"],
                "summary": "Agregar penalizacion a una pasada",
                "description": "Agrega tiempo de penalizacion que se suma al total_time_ms para calcular final_time_ms",
                "parameters": [
                    {"name": "run_id", "in": "path", "type": "integer", "required": True},
                    {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/PenaltyInput"}},
                ],
                "responses": {
                    "201": {
                        "description": "Penalizacion agregada. Retorna la pasada actualizada",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"$ref": "#/definitions/Run"},
                            },
                        },
                    },
                    "400": {"description": "Datos invalidos"},
                    "404": {"description": "Pasada no encontrada"},
                },
            },
        },
        "/runs/{run_id}/penalties/{penalty_id}": {
            "delete": {
                "tags": ["Penalizaciones"],
                "summary": "Quitar penalizacion",
                "parameters": [
                    {"name": "run_id", "in": "path", "type": "integer", "required": True},
                    {"name": "penalty_id", "in": "path", "type": "integer", "required": True},
                ],
                "responses": {
                    "200": {
                        "description": "Penalizacion eliminada. Retorna la pasada actualizada",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"$ref": "#/definitions/Run"},
                            },
                        },
                    },
                    "404": {"description": "Penalizacion no encontrada"},
                },
            }
        },
        # --- Rankings ---
        "/rankings/best-times": {
            "get": {
                "tags": ["Rankings"],
                "summary": "Mejores tiempos por piloto",
                "description": "Retorna el mejor final_time_ms (con penalizaciones) de cada piloto, ordenado ascendente",
                "parameters": [
                    {"name": "condition", "in": "query", "type": "string", "enum": ["dry", "wet", "humid"], "description": "Filtrar por condicion del tramo"},
                    {"name": "category", "in": "query", "type": "string", "description": "Filtrar por categoria del auto"},
                ],
                "responses": {
                    "200": {
                        "description": "Ranking de mejores tiempos",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "position": {"type": "integer"},
                                            "pilot_id": {"type": "integer"},
                                            "pilot_name": {"type": "string"},
                                            "nickname": {"type": "string"},
                                            "car_name": {"type": "string"},
                                            "best_time_ms": {"type": "integer"},
                                            "total_time_ms": {"type": "integer"},
                                            "penalty_total_ms": {"type": "integer"},
                                            "run_date": {"type": "string"},
                                            "track_condition": {"type": "string"},
                                            "car_category": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    }
                },
            }
        },
        "/rankings/history/{pilot_id}": {
            "get": {
                "tags": ["Rankings"],
                "summary": "Historial de tiempos de un piloto",
                "description": "Todas las pasadas validas de un piloto, ordenadas por fecha",
                "parameters": [{"name": "pilot_id", "in": "path", "type": "integer", "required": True}],
                "responses": {
                    "200": {
                        "description": "Historial de pasadas del piloto",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "run_id": {"type": "integer"},
                                            "run_date": {"type": "string"},
                                            "total_time_ms": {"type": "integer"},
                                            "final_time_ms": {"type": "integer"},
                                            "penalty_total_ms": {"type": "integer"},
                                            "car_name": {"type": "string"},
                                            "track_condition": {"type": "string"},
                                            "car_category": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    }
                },
            }
        },
        "/rankings/records": {
            "get": {
                "tags": ["Rankings"],
                "summary": "Records del tramo",
                "description": "Record general, por categoria y por condicion del tramo",
                "responses": {
                    "200": {
                        "description": "Records del tramo",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "overall": {"type": "object"},
                                        "by_category": {"type": "array", "items": {"type": "object"}},
                                        "by_condition": {"type": "array", "items": {"type": "object"}},
                                    },
                                },
                            },
                        },
                    }
                },
            }
        },
        "/rankings/summary": {
            "get": {
                "tags": ["Rankings"],
                "summary": "Resumen para dashboard",
                "description": "Total de pilotos, autos, pasadas, record actual y ultimas 5 pasadas",
                "responses": {
                    "200": {
                        "description": "Estadisticas resumen",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "total_pilots": {"type": "integer"},
                                        "total_cars": {"type": "integer"},
                                        "total_runs": {"type": "integer"},
                                        "record": {"type": "object"},
                                        "latest_runs": {"type": "array", "items": {"type": "object"}},
                                    },
                                },
                            },
                        },
                    }
                },
            }
        },
    },
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs",
}
