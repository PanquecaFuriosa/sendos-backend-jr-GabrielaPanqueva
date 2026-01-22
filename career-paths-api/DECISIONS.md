# Decisiones de Diseño e Implementación

Esta sección explica las decisiones arquitectónicas y de diseño tomadas durante el desarrollo del sistema, justificando cada elección.

## 1. Campos JSONB para Datos Flexibles

**Decisión:** Usar campos JSONB de PostgreSQL para `ai_profile` en Assessments y estructuras complejas.

**Justificación:**
- **Flexibilidad de schema**: Permite evolución del modelo de IA sin migraciones de base de datos
- **Datos anidados**: Representación natural de estructuras complejas (strengths, growth_areas, hidden_talents)
- **Output de IA variable**: La estructura de respuesta de servicios de IA puede cambiar
- **Performance**: PostgreSQL JSONB permite indexación y queries eficientes
- **Tipo nativo**: No requiere serialización/deserialización manual

**Trade-offs aceptados:**
- Validación menos estricta a nivel de base de datos
- Queries sobre campos JSON son más complejos que SQL tradicional
- Pérdida de normalización en algunos casos

**Mitigación:** 
- Validación exhaustiva con Pydantic en capa de aplicación
- Documentación clara del schema esperado en JSONB
- Índices GIN sobre campos JSONB críticos para performance

## 2. Modelo de Datos: Weak Entities

**Decisión:** Implementar `EvaluationDetail`, `CareerPathStep` y `DevelopmentAction` como weak entities.

**Justificación:**
- **Dependencia existencial**: Estos registros no tienen significado sin su entidad padre
- **Integridad referencial**: Cascade delete automático cuando se elimina el padre
- **Modelado semántico**: Refleja correctamente la relación de composición
- **Simplificación**: No requiere gestión independiente de ciclo de vida

**Diseño:**
```
Evaluation 1----* EvaluationDetail
CareerPath 1----* CareerPathStep
CareerPathStep 1----* DevelopmentAction
```

**Ventajas:**
- Garantiza consistencia de datos
- Simplifica queries (siempre se accede vía padre)
- Evita registros huérfanos

## 3. Separación Evaluator/Evaluatee

**Decisión:** Modelo con dos foreign keys a User: `evaluator_id` y `evaluatee_id`.

**Justificación:**
- **Flexibilidad**: Soporta todas las relaciones 360° (SELF, MANAGER, PEER, DIRECT_REPORT)
- **Trazabilidad**: Identifica claramente quién evaluó a quién
- **Queries eficientes**: Fácil obtener evaluaciones dadas o recibidas
- **Normalización**: Evita duplicación de datos de usuario

**Alternativa descartada:**
- Tabla intermedia User-Evaluation-User: Más compleja sin beneficio adicional

**Constraint único:**
```sql
UniqueConstraint(evaluator_id, evaluatee_id, cycle_id)
```
Garantiza que un evaluador solo evalúa una vez a una persona por ciclo.

## 4. Ciclos de Evaluación Independientes

**Decisión:** Tabla `EvaluationCycles` separada para gestionar períodos de evaluación.

**Justificación:**
- **Organización temporal**: Agrupa evaluaciones por período (Q1 2026, Q2 2026)
- **Estado del ciclo**: Permite controlar cuándo un ciclo está activo o cerrado
- **Análisis histórico**: Facilita comparación de evolución entre ciclos
- **Reglas de negocio**: Puede prevenir evaluaciones en ciclos cerrados

**Diseño:**
- Campos: `name`, `start_date`, `end_date`, `status` (ACTIVE, CLOSED, ARCHIVED)
- Relación 1:N con Evaluations y Assessments

## 5. Catálogo de Competencias Normalizado

**Decisión:** Tabla `Competencies` separada con foreign keys desde `EvaluationDetail`.

**Justificación:**
- **Consistencia**: Todos usan los mismos nombres de competencias
- **Gestión centralizada**: Fácil agregar/modificar competencias
- **Internacionalización**: Permite traducción de competencias
- **Reportes**: Facilita análisis agregado por competencia

**Alternativa descartada:**
- Strings libres en cada evaluación: Inconsistencias, typos, no normalizable

**Estructura:**
```sql
Competencies
  - id (UUID)
  - name (String, unique)
  - description (Text)
  - category (String) -- e.g., "Technical", "Leadership"
```

## 6. Procesamiento Asíncrono con Background Tasks

**Decisión:** Usar FastAPI BackgroundTasks para procesamiento de IA.

**Justificación:**
- **Simplicidad**: No requiere infraestructura adicional (Celery, RabbitMQ, Redis)
- **Apropiado para MVP**: Procesamiento tarda segundos, no horas
- **Respuesta inmediata**: Cliente recibe confirmación sin esperar procesamiento
- **Built-in**: Parte de FastAPI, sin dependencias externas

**Limitaciones conocidas:**
- No persistente: tareas se pierden si el proceso muere
- No escalable horizontalmente: limitado a workers del proceso FastAPI
- Sin retry automático: debe ser implementado manualmente

**Plan de evolución:**
- Fase 1 (MVP): Background Tasks ✅
- Fase 2 (Producción): Migrar a Celery + Redis
- Fase 3 (Escala): Queue distribuido (AWS SQS, RabbitMQ)

## 7. Sin Autenticación en MVP

**Decisión:** No implementar autenticación en esta versión.

**Justificación:**
- **Scope de prueba técnica**: Enfocada en funcionalidad core
- **Tiempo de desarrollo**: Priorizar features de negocio
- **Simplicidad en testing**: Sin complejidad de tokens/sesiones
- **Demostración**: Facilita evaluación de la API

** Crítico para producción:**
Esta decisión es solo para MVP. Producción **REQUIERE**:
- JWT authentication
- Roles y permisos (RBAC)
- Rate limiting por usuario
- Audit logs

**Plan de implementación:**
```python
# Fase 1: JWT básico
- POST /auth/login → token
- Header: Authorization: Bearer <token>
- Middleware de validación

# Fase 2: Roles
- Roles: EMPLOYEE, MANAGER, HR, ADMIN
- Endpoints con @require_role("MANAGER")

# Fase 3: Permisos granulares
- Solo evaluador puede ver su evaluación
- Solo evaluatee puede ver su assessment
```

## 8. Estructura Modular de Código

**Decisión:** Separación clara en módulos: models, schemas, routers, services.

**Justificación:**
- **Separation of Concerns**: Cada módulo tiene responsabilidad única
- **Mantenibilidad**: Fácil localizar y modificar código
- **Testabilidad**: Módulos independientes facilitan unit tests
- **Escalabilidad**: Nuevos features no contaminan código existente
- **Colaboración**: Múltiples desarrolladores sin conflictos de merge

**Arquitectura en capas:**
```
┌─────────────────────────────────┐
│  Routers (HTTP Layer)           │ ← FastAPI endpoints
│  - Validación HTTP               │
│  - Parsing request/response      │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Services (Business Logic)      │ ← Lógica de negocio
│  - Reglas de negocio             │
│  - Orquestación                  │
│  - Llamadas a servicios externos │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Models (Data Layer)            │ ← SQLAlchemy models
│  - Persistencia                  │
│  - Queries a base de datos       │
└─────────────────────────────────┘

         Esquemas (Pydantic)
         ├── Request schemas
         └── Response schemas
```

**Ventajas demostradas:**
- Fácil agregar nuevos endpoints sin modificar modelos
- Business logic testeable sin levantar servidor HTTP
- Reuso de lógica entre diferentes endpoints

## 9. Hard Delete vs Soft Delete

**Decisión:** Implementar hard delete (eliminación física).

**Justificación:**
- **Simplicidad**: Queries más simples, sin filtros `WHERE deleted_at IS NULL`
- **Performance**: Índices más eficientes sin registros "eliminados"
- **MVP scope**: No hay requerimiento de auditoría completa
- **GDPR**: Derecho al olvido requiere eliminación física

**Trade-offs:**
- No hay histórico de cambios
- No se puede "deshacer" eliminación
- Dificulta debugging de problemas históricos

**Plan futuro (si se requiere auditoría):**
```python
# Agregar a todos los modelos
deleted_at = Column(DateTime, nullable=True)
deleted_by = Column(UUID, ForeignKey("users.id"), nullable=True)

# Query manager
def active_only(query):
    return query.filter(Model.deleted_at == None)

# Soft delete
def soft_delete(obj, user_id):
    obj.deleted_at = datetime.utcnow()
    obj.deleted_by = user_id
```

## 10. Testing con SQLite en Memoria

**Decisión:** Usar SQLite in-memory para unit tests, PostgreSQL para integration tests.

**Justificación:**
- **Velocidad**: SQLite en memoria es ~10x más rápido
- **Simplicidad**: No requiere servicio de BD corriendo
- **CI/CD**: Fácil configurar en GitHub Actions
- **Aislamiento**: Cada test tiene BD limpia automáticamente

**Limitaciones SQLite:**
- UUID manejo diferente
- No soporta algunas features de PostgreSQL (JSONB queries avanzados)
- Dialectos SQL ligeramente diferentes

**Estrategia de testing:**
```
Unit tests (70%) → SQLite in-memory
  - Tests de modelos individuales
  - Tests de validación Pydantic
  - Tests de lógica de negocio

Integration tests (30%) → PostgreSQL
  - Tests de endpoints completos
  - Tests de queries complejas JSONB
  - Tests de constraints únicos
```
---

## BONUS IMPLEMENTADOS

### 1. Alembic - Migraciones de Base de Datos ⭐ (+5 puntos)

**Implementación:**
- Alembic configurado con auto-detección de modelos
- Migración inicial (001_initial_migration.py) con las 9 tablas
- Integración con Docker: migraciones automáticas al iniciar
- Comandos documentados en README.md

**Beneficios:**
- Versionamiento del esquema de BD
- Rollback seguro de cambios
- Trabajo en equipo sin conflictos de schema
- Deployment controlado y auditable

**Archivos clave:**
- `alembic/env.py`: Configuración con import de modelos
- `alembic/versions/001_initial_migration.py`: Migración inicial
- `docker-compose.yml`: Ejecuta `alembic upgrade head` antes de iniciar app

### 2. Tenacity - Retry Logic para Integraciones IA ⭐

**Implementación:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
)
async def call_ai_service(data):
    # Llamadas al servicio IA con reintentos automáticos
```

**Beneficios:**
- Resiliencia ante fallos temporales de red
- Experiencia de usuario mejorada (menos errores 500)
- Backoff exponencial evita saturar servicios externos

### 3. BackgroundTasks - Procesamiento Asíncrono

**Implementación:**
```python
@router.post("/api/v1/career-paths")
async def generate_career_path(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_career_path_generation, assessment_id)
    return {"status": "processing"}
```

**Beneficios:**
- Respuestas rápidas al usuario (no bloqueantes)
- Procesamiento pesado en segundo plano
- Mejor experiencia en generación de rutas (puede tardar varios segundos)