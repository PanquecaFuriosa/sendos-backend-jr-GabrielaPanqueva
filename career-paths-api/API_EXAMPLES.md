# Ejemplos de Requests - Career Paths API

Esta API implementa la arquitectura especificada en ARCHITECTURE.md.

Este archivo contiene ejemplos de requests HTTP para probar todos los endpoints de la API.

## Prerequisitos

1. Tener la API corriendo: `docker-compose up` o `uvicorn app.main:app --reload`
2. Tener el servicio mock de IA corriendo: `python ai_mock_service.py`
3. Base de datos inicializada: `python init_db.py`

Después de `init_db.py` tendrás:
- 5 usuarios creados
- 1 ciclo activo "Q1 2026"
- 10 competencias en el catálogo
- 3 evaluaciones completas para María García (SELF + MANAGER + PEER)

## Variables

Obtén estos valores del output de `init_db.py`:

```bash
BASE_URL=http://localhost:8000
API_PREFIX=/api/v1

# IDs de ejemplo (copiar del output de init_db.py)
MARIA_ID=<UUID de María García>
CARLOS_ID=<UUID de Carlos López>
CYCLE_ID=<UUID del ciclo Q1 2026>
COMP_LIDERAZGO_ID=<UUID de competencia Liderazgo>
COMP_COMUNICACION_ID=<UUID de competencia Comunicación>
```

---

## 1. Health Check

### GET /health

```bash
curl -X GET "${BASE_URL}/health"
```

**Respuesta esperada:**
```json
{
  "status": "healthy"
}
```

---

## Evaluaciones 360°

### POST /api/v1/evaluations - Crear Evaluación

Estructura:
- `evaluator_id` y `evaluatee_id` (separados)
- `cycle_id` obligatorio
- `relationship`: SELF | MANAGER | PEER | DIRECT_REPORT
- `answers` array con competency_id, score (1-10), comments
      "competencies": [
        {
          "name": "Liderazgo",
          "self_score": 8,
          "peer_scores": [7, 8, 9],
          "manager_score": 7,
          "direct_report_scores": [8, 8]
        },
        {
          "name": "Comunicación",
          "self_score": 9,
          "peer_scores": [8, 9, 9],
          "manager_score": 8,
          "direct_report_scores": [9]
        },
        {
          "name": "Trabajo en Equipo",
          "self_score": 7,
          "peer_scores": [8, 7, 8],
          "manager_score": 8,
          "direct_report_scores": [7, 8]
        },
        {
          "name": "Pensamiento Estratégico",
          "self_score": 6,
          "peer_scores": [5, 6, 7],
          "manager_score": 6,
          "direct_report_scores": []
        },
        {
          "name": "Gestión del Tiempo",
          "self_score": 8,
          "peer_scores": [7, 8, 8],
          "manager_score": 7,
          "direct_report_scores": [8]
        }
      ]
    },
    "current_position": "Analista Senior",
    "years_experience": "5"
  }'
```

**Respuesta esperada (201):**
```json
{
  "id": "uuid-de-evaluacion",
  "user_id": "uuid-del-usuario",
  "evaluation_data": { ... },
  "status": "completed",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### GET /api/v1/evaluations/{evaluation_id} - Obtener Evaluación

```bash
curl -X GET "${BASE_URL}${API_PREFIX}/evaluations/EVALUATION_ID_AQUI"
```

### GET /api/v1/evaluations/ - Listar Evaluaciones

```bash
curl -X GET "${BASE_URL}${API_PREFIX}/evaluations/"
```

Con paginación:
```bash
curl -X GET "${BASE_URL}${API_PREFIX}/evaluations/?skip=0&limit=10"
```

### GET /api/v1/evaluations/user/{user_id} - Evaluaciones de Usuario

```bash
curl -X GET "${BASE_URL}${API_PREFIX}/evaluations/user/USER_ID_AQUI"
```

---

## 3. Assessments (Análisis de Habilidades)

### POST /api/v1/assessments/trigger - Iniciar Assessment

```bash
curl -X POST "${BASE_URL}${API_PREFIX}/assessments/trigger" \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_id": "EVALUATION_ID_AQUI"
  }'
```

**Respuesta esperada (201):**
```json
{
  "id": "uuid-del-assessment",
  "user_id": "uuid-del-usuario",
  "evaluation_id": "uuid-de-evaluacion",
  "processing_status": "pending",
  "skills_profile": null,
  "readiness_for_roles": null,
  "created_at": "2024-01-15T10:35:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

### GET /api/v1/assessments/{assessment_id} - Obtener Assessment

```bash
curl -X GET "${BASE_URL}${API_PREFIX}/assessments/ASSESSMENT_ID_AQUI"
```

**Respuesta cuando está completado:**
```json
{
  "id": "uuid-del-assessment",
  "user_id": "uuid-del-usuario",
  "evaluation_id": "uuid-de-evaluacion",
  "processing_status": "completed",
  "skills_profile": {
    "strengths": ["Comunicación", "Trabajo en Equipo"],
    "growth_areas": ["Pensamiento Estratégico"],
    "hidden_talents": ["Liderazgo", "Gestión del Tiempo"]
  },
  "readiness_for_roles": [
    {
      "role": "Gerente Regional",
      "readiness_percentage": 65,
      "missing_competencies": ["Pensamiento Estratégico"]
    }
  ],
  "processing_started_at": "2024-01-15T10:35:01",
  "processing_completed_at": "2024-01-15T10:35:03",
  "created_at": "2024-01-15T10:35:00",
  "updated_at": "2024-01-15T10:35:03"
}
```

### GET /api/v1/assessments/ - Listar Assessments

```bash
curl -X GET "${BASE_URL}${API_PREFIX}/assessments/"
```

### GET /api/v1/assessments/user/{user_id} - Assessments de Usuario

```bash
curl -X GET "${BASE_URL}${API_PREFIX}/assessments/user/USER_ID_AQUI"
```

---

## 4. Career Paths (Senderos de Carrera)

### GET /api/v1/career-paths/{user_id} - Obtener Sendero de Carrera

```bash
curl -X GET "${BASE_URL}${API_PREFIX}/career-paths/USER_ID_AQUI"
```

**Primera llamada (202 - Generando):**
```json
{
  "detail": "Career path generation started. Please check again in a few moments."
}
```

**Llamada posterior (200 - Completado):**
```json
{
  "id": "uuid-del-career-path",
  "user_id": "uuid-del-usuario",
  "recommended_paths": [
    {
      "target_role": "Gerente Regional",
      "timeline_months": 12,
      "milestones": [ ... ],
      "development_actions": [ ... ],
      "success_probability": 0.75
    }
  ],
  "skill_development_plan": [ ... ],
  "learning_resources": [ ... ],
  "status": "active",
  "version": 1,
  "generated_at": "2024-01-15T10:40:00",
  "expires_at": "2024-07-15T10:40:00"
}
```

### POST /api/v1/career-paths/{user_id}/regenerate - Regenerar Sendero

```bash
curl -X POST "${BASE_URL}${API_PREFIX}/career-paths/USER_ID_AQUI/regenerate"
```

**Respuesta (202):**
```json
{
  "message": "Career path regeneration started",
  "user_id": "uuid-del-usuario"
}
```

### GET /api/v1/career-paths/ - Listar Career Paths

```bash
curl -X GET "${BASE_URL}${API_PREFIX}/career-paths/"
```

Con filtro de estado:
```bash
curl -X GET "${BASE_URL}${API_PREFIX}/career-paths/?status_filter=active"
```

---

## 5. Flujo Completo de Ejemplo

### Paso 1: Crear usuario (ejecutar init_db.py primero)

```bash
python init_db.py
```

Anotar el USER_ID de uno de los usuarios creados.

### Paso 2: Crear evaluación 360°

```bash
curl -X POST "http://localhost:8000/api/v1/evaluations/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "TU_USER_ID",
    "evaluation_data": {
      "competencies": [
        {
          "name": "Liderazgo",
          "self_score": 8,
          "peer_scores": [7, 8, 9],
          "manager_score": 7,
          "direct_report_scores": [8, 8]
        },
        {
          "name": "Comunicación",
          "self_score": 9,
          "peer_scores": [8, 9, 9],
          "manager_score": 8,
          "direct_report_scores": [9]
        },
        {
          "name": "Pensamiento Estratégico",
          "self_score": 5,
          "peer_scores": [5, 6, 4],
          "manager_score": 5,
          "direct_report_scores": []
        }
      ]
    },
    "current_position": "Analista Senior",
    "years_experience": "5"
  }'
```

Anotar el EVALUATION_ID.

### Paso 3: Iniciar assessment

```bash
curl -X POST "http://localhost:8000/api/v1/assessments/trigger" \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_id": "TU_EVALUATION_ID"
  }'
```

Anotar el ASSESSMENT_ID.

### Paso 4: Verificar assessment (esperar unos segundos)

```bash
curl -X GET "http://localhost:8000/api/v1/assessments/TU_ASSESSMENT_ID"
```

Verificar que `processing_status` sea "completed".

### Paso 5: Obtener sendero de carrera

```bash
curl -X GET "http://localhost:8000/api/v1/career-paths/TU_USER_ID"
```

Si retorna 202, esperar unos segundos y volver a llamar.

---

## 6. Testing con Postman

Importa la siguiente colección en Postman:

```json
{
  "info": {
    "name": "Career Paths API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "api_prefix",
      "value": "/api/v1"
    }
  ]
}
```

---

## 7. Documentación Interactiva

Una vez levantada la API, visita:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Desde ahí puedes probar todos los endpoints interactivamente.
