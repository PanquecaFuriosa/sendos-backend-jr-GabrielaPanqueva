# Career Paths API - Prueba Técnica Backend Jr - Gabriela Panqueva

Sistema de evaluación 360° con generación inteligente de senderos de carrera usando IA.

## Documentación

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Arquitectura técnica completa del sistema
- **[DECISIONS.md](./DECISIONS.md)** - Decisiones de diseño y sus justificaciones

## Inicio Rápido

### Prerrequisitos
- Python 3.11+
- Docker y Docker Compose

### Instalación

```bash
# 1. Crear ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env

# 4. Levantar PostgreSQL con Docker
docker compose up -d postgres

# 5. Esperar que la DB esté lista (5 segundos)
sleep 5

# 6. Ejecutar migraciones
alembic upgrade head

# 7. (Opcional) Cargar datos de prueba
python init_db.py

# 8. Iniciar la API
uvicorn app.main:app --reload --port 8000
```

**Servicios disponibles en:**
- Documentación API: http://localhost:8000/docs
- Documentación alternativa: http://localhost:8000/redoc
- Servicio mock de IA: http://localhost:8001/docs (levantado con docker-compose)

**Nota:** El servicio mock de IA se levanta automáticamente con `docker-compose up -d` junto con PostgreSQL.

## Testing

### Ejecutar Todos los Tests

```bash
# En otra terminal (con ambiente virtual activo)
# Prerequisito: docker-compose up -d debe estar corriendo (PostgreSQL + AI Mock)
pytest tests/ -v
```

### Opciones Adicionales

```bash
# Con cobertura
pytest --cov=app --cov-report=html tests/ -v

# Modo verbose (salida detallada)
pytest -vv tests/

# Modo verbose (salida detallada)
pytest -vv tests/

# Sin reporte de cobertura (más rápido)
pytest --no-cov tests/

# Ejecutar archivo específico
pytest tests/test_api.py -v

# Ver reporte HTML de cobertura
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
start htmlcov/index.html     # Windows
```

### Usando Docker

```bash
# Ejecutar todos los tests en contenedor
docker compose exec api pytest

# Con cobertura
docker compose exec api pytest --cov=app --cov-report=html

# Tests específicos
docker compose exec api pytest tests/test_api.py -v
```

**Configuración de Tests (pytest.ini):**
- Auto-descubrimiento desde directorio `tests/`
- Cobertura de código habilitada para módulo `app/`
- Reportes: terminal + HTML en `htmlcov/`
- Modo async automático con pytest-asyncio

## Gestión de Base de Datos

### Migraciones (Alembic)

El proyecto usa **Alembic** para control de versiones de la base de datos.

```bash
# Aplicar migraciones (requerido antes del primer inicio)
alembic upgrade head

# Crear nueva migración (después de modificar modelos)
alembic revision --autogenerate -m "Descripción del cambio"

# Ver historial de migraciones
alembic history

# Revertir última migración
alembic downgrade -1

# Docker: las migraciones se ejecutan automáticamente
docker compose up -d
```

### Inicialización de Datos de Ejemplo

Después de ejecutar las migraciones, puedes cargar datos de ejemplo:

```bash
# Manual
python init_db.py

# Con Docker
docker compose exec api python init_db.py
```

**Los datos de ejemplo incluyen:**
- 5 usuarios de ejemplo
- 2 ciclos de evaluación (Q1 2026, Q2 2026)
- 7 competencias estándar (Liderazgo, Comunicación, etc.)
- Múltiples evaluaciones 360° con detalles

## Estructura del Proyecto

```
career-paths-api/
├── app/
│   ├── main.py                    # Punto de entrada de la aplicación FastAPI
│   ├── config.py                  # Configuración de la aplicación
│   ├── database.py                # Conexión y sesión de base de datos
│   ├── models/                    # Modelos ORM de SQLAlchemy
│   │   ├── user.py                   # Modelo de usuario
│   │   ├── evaluation_cycle.py       # Ciclos de evaluación (Q1 2026, etc.)
│   │   ├── competency.py             # Catálogo de competencias
│   │   ├── evaluation.py             # Evaluaciones 360°
│   │   ├── evaluation_detail.py      # Detalles de evaluación por competencia
│   │   ├── assessment.py             # Evaluación de habilidades generada por IA
│   │   ├── career_path.py            # Senderos de carrera generados
│   │   ├── career_path_step.py       # Pasos del sendero de carrera
│   │   └── development_action.py     # Acciones de desarrollo por paso
│   ├── schemas/                   # Esquemas Pydantic (request/response)
│   │   ├── evaluation_cycle.py
│   │   ├── competency.py
│   │   ├── evaluation.py
│   │   ├── assessment.py
│   │   ├── career_path.py
│   │   └── user.py
│   ├── routers/                   # Manejadores de rutas API
│   │   ├── evaluations.py            # Endpoints de evaluación 360°
│   │   ├── assessments.py            # Endpoints de evaluación de habilidades
│   │   └── career_paths.py           # Endpoints de senderos de carrera
│   └── services/
│       └── ai_integration.py         # Integración con servicio de IA con lógica de reintentos
├── alembic/                       # Sistema de migraciones de base de datos
│   ├── versions/                     # Archivos de migración (control de versiones)
│   │   └── 001_initial_migration.py
│   └── env.py                        # Configuración de Alembic
├── tests/
│   ├── conftest.py                # Fixtures y configuración de Pytest
│   ├── test_api.py                # Tests de endpoints API
│   └── test_main.py               # Tests de aplicación principal
├── alembic.ini                    # Configuración de Alembic
├── pytest.ini                     # Configuración de Pytest
├── ai_mock_service.py            # Servicio mock de IA para desarrollo
├── init_db.py                    # Script de inicialización de datos de ejemplo
├── docker-compose.yml            # Orquestación multi-contenedor
├── Dockerfile                    # Definición de contenedor API
├── Dockerfile.ai-mock            # Contenedor de servicio mock de IA
├── requirements.txt              # Dependencias de Python
├── ARCHITECTURE.md               # Documento de arquitectura técnica
├── DECISIONS.md                  # Registro de decisiones de diseño
└── README.md                     # Este archivo
```

## API y Endpoints

La API REST está completamente documentada en:

- **Swagger UI (interactiva):** http://localhost:8000/docs  
  Probar los endpoints directamente desde el navegador

- **[ARCHITECTURE.md](./ARCHITECTURE.md)**  
  Especificación técnica completa de todos los endpoints, request/response schemas y validaciones

### Endpoints Principales

- `POST /api/v1/evaluations` - Crear evaluación 360°
- `GET /api/v1/skills-assessments/{user_id}` - Obtener perfil de habilidades
- `GET /api/v1/career-paths/{user_id}` - Obtener senderos de carrera
- `POST /api/v1/career-paths/{path_id}/accept` - Aceptar un sendero

## Flujo Completo

1. **Crear ciclo de evaluación** (vía admin o base de datos)
2. **Crear evaluaciones 360°:**
   - Auto-evaluación (SELF)
   - Evaluación del manager (MANAGER)
   - Evaluación(es) de pares (PEER)
3. **Detección automática:** Cuando SELF + MANAGER + PEER están completas, se activa el procesamiento de IA
4. **Evaluación generada:** La IA analiza las evaluaciones y crea el perfil de habilidades
5. **Senderos de carrera:** Al consultar `/career-paths/{user_id}`, se generan senderos personalizados
6. **Aceptar sendero:** El usuario selecciona un sendero de carrera con `/accept`

**Probar la API:** Visita http://localhost:8000/docs para interactuar con todos los endpoints

## Configuración

### Variables de Entorno

Ver `.env.example` para todas las configuraciones disponibles.

**Variables principales:**
- `DATABASE_URL`: Cadena de conexión a PostgreSQL
- `AI_SERVICE_BASE_URL`: URL del servicio de IA (http://localhost:8001 en desarrollo)
- `SECRET_KEY`: Clave secreta para JWT (si se implementa autenticación)
- `DEBUG`: Modo debug (True/False)

## Arquitectura

Esta implementación sigue la arquitectura definida en ARCHITECTURE.md:

**Decisiones arquitectónicas clave:**
- Separación evaluador/evaluado en evaluaciones
- Ciclos de evaluación (Q1 2026, Q2 2026, etc.)
- Catálogo de competencias normalizado
- Evaluación 360° con detalles por competencia
- Detección automática de ciclo completo (SELF + MANAGER + PEER)
- Procesamiento de IA con lógica de reintentos (librería tenacity)
- Senderos de carrera como entidades relacionales (Path → Steps → Actions)
- Restricciones únicas: (evaluator, evaluatee, cycle), (user, cycle) para evaluaciones
- Validaciones: puntajes 1-10, tipos de relación, reglas de evaluación SELF

**Para documentación técnica detallada:**
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura completa del sistema
- [DECISIONS.md](./DECISIONS.md) - Decisiones de diseño y justificaciones

### Stack Tecnológico

- **FastAPI 0.109.0** - Framework web moderno de Python
- **SQLAlchemy 2.0.25** - ORM para operaciones de base de datos
- **Alembic 1.13.1** - Herramienta de migración de base de datos
- **PostgreSQL 15** - Base de datos relacional
- **Pydantic v2** - Validación de datos con type hints
- **Pytest 7.4.4** - Framework de testing
- **Tenacity 8.2.3** - Lógica de reintentos para llamadas al servicio de IA
- **Uvicorn 0.25.0** - Servidor ASGI

### Documentación Interactiva

- **Swagger UI:** http://localhost:8000/docs - Para pruebas interactivas de API
- **Servicio Mock de IA:** http://localhost:8001/docs - Endpoints del servicio mock de IA