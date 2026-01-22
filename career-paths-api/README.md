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
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar y configurar variables de entorno
cp .env.example .env

# 4. Levantar PostgreSQL con Docker
docker-compose up -d

# 5. Esperar que la DB esté lista
sleep 5

# 6. Ejecutar migraciones
alembic upgrade head

# 7. (Opcional) Cargar datos de prueba
python init_db.py

# 8. Correr la aplicación
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en http://localhost:8000/docs

### Ejecutar tests

```bash
pytest tests/ -v
```

## Migraciones de Base de Datos

El proyecto usa **Alembic** para gestionar migraciones de base de datos.

### Primera vez (requerido)
```bash
# Con Docker (se ejecutan automáticamente al hacer docker-compose up)
docker-compose up -d

# Manual - EJECUTAR ANTES de uvicorn
alembic upgrade head
```

### Crear nueva migración (cuando cambies modelos)
```bash
alembic revision --autogenerate -m "Descripción del cambio"
```

### Ver historial de migraciones
```bash
alembic history
```

### Revertir última migración
```bash
alembic downgrade -1
```

## Inicialización de Datos de Ejemplo

Después de ejecutar las migraciones, puedes cargar datos de ejemplo:

```bash
# Con Docker
docker-compose exec api python init_db.py

# Manual (después de alembic upgrade head)
python init_db.py
```

Esto crea:
- 5 usuarios de ejemplo
- 2 ciclos de evaluación
- 7 competencias estándar
- Múltiples evaluaciones 360° con detalles

## Estructura del Proyecto

```
career-paths-api/
├── app/
│   ├── main.py                 # Aplicación FastAPI principal
│   ├── config.py               # Configuración
│   ├── database.py             # Conexión a DB
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── evaluation_cycle.py
│   │   ├── competency.py
│   │   ├── evaluation.py
│   │   ├── evaluation_detail.py
│   │   ├── assessment.py
│   │   ├── career_path.py
│   │   ├── career_path_step.py
│   │   └── development_action.py
│   ├── schemas/                # Esquemas Pydantic
│   │   ├── evaluation_cycle.py
│   │   ├── competency.py
│   │   ├── evaluation.py
│   │   ├── assessment.py
│   │   └── career_path.py
│   ├── routers/                # Endpoints API
│   │   ├── evaluations.py
│   │   ├── assessments.py
│   │   └── career_paths.py
│   └── services/
│       └── ai_integration.py
├── alembic/                    # Migraciones de base de datos
│   ├── versions/               # Archivos de migración
│   │   └── 001_initial_migration.py
│   └── env.py                  # Configuración de Alembic
├── tests/
│   └── test_api.py
├── alembic.ini                 # Configuración de Alembic
├── ai_mock_service.py
├── init_db.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Endpoints Principales

### Evaluaciones 360°

**POST /api/v1/evaluations**
Crear evaluación con estructura evaluator/evaluatee

```json
{
  "evaluator_id": "uuid",
  "evaluatee_id": "uuid",
  "cycle_id": "uuid",
  "relationship": "SELF|MANAGER|PEER|DIRECT_REPORT",
  "answers": [
    {
      "competency_id": "uuid",
      "score": 8,
      "comments": "Excelente liderazgo en proyecto X"
    }
  ]
}
```

Validaciones:
- `score` debe estar entre 1 y 10
- `relationship` debe ser uno de: SELF, MANAGER, PEER, DIRECT_REPORT
- Para SELF: `evaluator_id` debe ser igual a `evaluatee_id`
- Constraint único: (evaluator_id, evaluatee_id, cycle_id)

Respuesta 201 Created:
```json
{
  "id": "uuid",
  "evaluator_id": "uuid",
  "evaluatee_id": "uuid",
  "cycle_id": "uuid",
  "relationship": "PEER",
  "status": "COMPLETED",
  "submitted_at": "2026-01-21T...",
  "details": [
    {
      "competency_name": "Liderazgo",
      "score": 8,
      "comments": "..."
    }
  ]
}
```

**POST /api/v1/evaluations/{evaluation_id}/process**
Procesar evaluación manualmente con IA (normalmente es automático)

### Evaluación de Habilidades con IA

**GET /api/v1/skills-assessments/{user_id}**
Obtener assessment más reciente del usuario

**Respuesta 200:**
```json
{
  "user_id": "uuid",
  "cycle_id": "uuid",
  "processing_status": "COMPLETED",
  "ai_profile": {
    "strengths": ["Liderazgo", "Comunicación"],
    "growth_areas": ["Pensamiento Estratégico"],
    "hidden_talents": ["Innovación"],
    "readiness_for_roles": [
      {
        "role_name": "Gerente Regional",
        "readiness_percentage": 75,
        "reasoning": "Fortalezas en liderazgo..."
      }
    ]
  },
  "created_at": "2026-01-21T..."
}
```

Respuesta 404: Usuario no encontrado o sin assessments

### Senderos de Carrera

**GET /api/v1/career-paths/{user_id}**
Obtener senderos generados para un usuario

**Respuesta 200:**
```json
{
  "career_path_id": "uuid",
  "user_id": "uuid",
  "generated_paths": [
    {
      "path_id": "uuid",
      "path_name": "Ruta de Liderazgo Ejecutivo",
      "recommended": true,
      "total_duration_months": 18,
      "feasibility_score": 0.75,
      "status": "GENERATED"
    }
  ],
  "timestamp": "2026-01-21T..."
}
```

Respuesta 202 Accepted: Generación iniciada en background
Respuesta 404 Not Found: Usuario no encontrado o sin assessment completado

**GET /api/v1/career-paths/{path_id}/steps**
Obtener pasos detallados de un sendero

**Respuesta 200:**
```json
{
  "path_id": "uuid",
  "path_name": "Ruta de Liderazgo Ejecutivo",
  "steps": [
    {
      "step_number": 1,
      "target_role": "Team Leader",
      "duration_months": 6,
      "required_competencies": ["Liderazgo", "Comunicación"]
    }
  ]
}
```

**POST /api/v1/career-paths/{path_id}/accept**
Aceptar un sendero de carrera

**Respuesta 200:**
```json
{
  "path_id": "uuid",
  "user_id": "uuid",
  "status": "IN_PROGRESS",
  "started_at": "2026-01-21T..."
}
```

Respuesta 409 Conflict: El sendero ya está en progreso

## Flujo Completo

1. **Crear ciclo de evaluación** (via admin o DB)
2. **Crear evaluaciones 360°:**
   - Auto-evaluación (SELF)
   - Evaluación de manager (MANAGER)
   - Evaluación de peer(s) (PEER)
3. **Detección automática:** Al completar SELF + MANAGER + PEER, se dispara procesamiento de IA
4. **Assessment generado:** IA analiza evaluaciones y crea perfil de habilidades
5. **Career paths:** Al consultar `/career-paths/{user_id}`, se generan senderos personalizados
6. **Aceptar path:** Usuario selecciona sendero con `/accept`

## Testing

```bash
# Ejecutar todos los tests
docker-compose exec api pytest

# Con coverage
docker-compose exec api pytest --cov=app --cov-report=html

# Tests específicos
docker-compose exec api pytest tests/test_api.py -v

# Ver reporte de coverage (HTML)
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS/Linux
```

## Ejemplos de Uso

### Crear evaluación 360°
```bash
curl -X POST "http://localhost:8000/api/v1/evaluations" \
  -H "Content-Type: application/json" \
  -d '{
    "evaluatee_id": "uuid-user-1",
    "evaluator_id": "uuid-user-2",
    "cycle_id": "uuid-cycle-1",
    "evaluator_relationship": "PEER",
    "answers": [
      {"competency_id": "uuid-comp-1", "score": 8, "comments": "Excelente"}
    ]
  }'
```

### Obtener assessment de habilidades
```bash
curl "http://localhost:8000/api/v1/skills-assessments/uuid-user-1"
```

### Obtener senderos de carrera
```bash
curl "http://localhost:8000/api/v1/career-paths/uuid-user-1"
```

## Arquitectura Técnica

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests de la API
pytest tests/test_api.py -v

# Ver output detallado
pytest -v -s
```

## Variables de Entorno

Ver `.env.example` para todas las configuraciones disponibles.

Principales variables:
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `AI_SERVICE_BASE_URL`: URL del servicio de IA (http://localhost:8001 en desarrollo)
- `SECRET_KEY`: Clave secreta para JWT (si se implementa autenticación)
- `DEBUG`: Modo debug (True/False)

## Documentación Adicional

- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Documento de arquitectura que guía esta implementación
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Resumen de la implementación
- Documentación interactiva: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- Mock AI Service: http://localhost:8001/docs

## Arquitectura Implementada

Esta implementación sigue fielmente la arquitectura definida en el documento ARCHITECTURE.md:

- Separación evaluator/evaluatee en evaluaciones
- Ciclos de evaluación (Q1 2026, Q2 2026, etc)
- Catálogo de competencias normalizado
- Evaluación 360° con detalles por competencia
- Detección automática de ciclo completo (SELF + MANAGER + PEER)
- Procesamiento de IA con retry logic (tenacity)
- Career paths como entidades relacionales (Path → Steps → Actions)
- Constraints únicos: (evaluator, evaluatee, cycle), (user, cycle) para assessments
- Validaciones: scores 1-10, relationship types, SELF evaluation rules

Para más detalles, ver [ARCHITECTURE.md](./ARCHITECTURE.md) y [DECISIONS.md](./DECISIONS.md).

## Deployment técnicos, ver [ARCHITECTURE.md](./ARCHITECTURE.md) y [DECISIONS.md](./DECISIONS

```bash
# Construir imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Ejecutar migraciones en contenedor
docker-compose exec api alembic upgrade head

# Inicializar datos
docker-compose exec api python init_db.py

# Detener servicios
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

## Desarrollo

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Inicializar datos de ejemplo
python init_db.py
```