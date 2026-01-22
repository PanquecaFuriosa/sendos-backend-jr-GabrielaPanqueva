# Implementación de Career Paths API

## Descripción

Sistema de evaluación 360° con generación inteligente de senderos de carrera usando IA, implementado según la arquitectura especificada en el documento ARCHITECTURE.md del repositorio.

## Componentes Principales

### Modelos de Base de Datos

1. **User**: Empleados del sistema
2. **EvaluationCycle**: Ciclos de evaluación (Q1 2026, Q2 2026, etc.)
3. **Competency**: Catálogo de competencias evaluables
4. **Evaluation**: Evaluaciones 360° con separación evaluator/evaluatee
5. **EvaluationDetail**: Scores y comentarios por competencia
6. **Assessment**: Perfiles de IA generados por ciclo
7. **CareerPath**: Senderos de carrera generados
8. **CareerPathStep**: Pasos secuenciales de un sendero
9. **DevelopmentAction**: Acciones de desarrollo por paso

### Endpoints API

#### Evaluaciones
- `POST /api/v1/evaluations` - Crear evaluación 360°
- `POST /api/v1/evaluations/{id}/process` - Procesar evaluación con IA

#### Assessments
- `GET /api/v1/skills-assessments/{user_id}` - Obtener perfil de habilidades

#### Career Paths
- `GET /api/v1/career-paths/{user_id}` - Listar senderos del usuario
- `GET /api/v1/career-paths/{path_id}/steps` - Detalles de un sendero
- `POST /api/v1/career-paths/{path_id}/accept` - Aceptar sendero

### Flujo de Trabajo

1. Se crean evaluaciones 360° (SELF, MANAGER, PEER)
2. Al completar el ciclo, se detecta automáticamente y se genera el assessment con IA
3. El assessment analiza las evaluaciones y crea un perfil de habilidades
4. Se pueden generar senderos de carrera basados en el assessment
5. El usuario puede aceptar un sendero para iniciarlo

### Características Técnicas

- **Retry Logic**: Implementado con tenacity (3 intentos, backoff exponencial)
- **Validaciones**: Scores 1-10, relationship types, constraints únicos
- **Detección Automática**: Ciclo completo dispara procesamiento de IA
- **Background Tasks**: Generación de career paths en segundo plano
- **Estructura Relacional**: Normalización de datos en PostgreSQL

## Tecnologías

- FastAPI 0.109.0
- PostgreSQL 15+
- SQLAlchemy 2.0.25
- Pydantic 2.5.3
- Tenacity 8.2.3 (retry logic)
- Docker & Docker Compose

## Configuración

Ver archivo `.env.example` para variables de entorno requeridas.

## Documentación

- README.md - Guía completa de uso
- API_EXAMPLES.md - Ejemplos de requests
- /docs - Documentación interactiva Swagger
- /redoc - Documentación ReDoc
