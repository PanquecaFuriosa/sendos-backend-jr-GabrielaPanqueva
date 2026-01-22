# Decisiones Técnicas - Career Paths API

Este documento explica las principales decisiones técnicas tomadas durante el desarrollo del proyecto y la justificación detrás de cada una.

## 1. Framework Web: FastAPI

**Decisión:** Usar FastAPI como framework web principal.

**Razones:**
- ✅ **Alto rendimiento**: Comparable a Node.js y Go
- ✅ **Validación automática**: Pydantic integrado para validación de datos
- ✅ **Documentación interactiva**: Swagger UI y ReDoc automáticos
- ✅ **Type hints nativos**: Mejor experiencia de desarrollo y menos bugs
- ✅ **Async/await**: Soporte nativo para operaciones asíncronas
- ✅ **Estándares modernos**: OpenAPI, JSON Schema

**Alternativas consideradas:**
- Django REST Framework: Más pesado, mayor curva de aprendizaje
- Flask: Menos features out-of-the-box, sin validación automática

## 2. Base de Datos: PostgreSQL

**Decisión:** Usar PostgreSQL como base de datos principal.

**Razones:**
- ✅ **Robustez**: ACID compliant, confiable para producción
- ✅ **Soporte JSON**: Campos JSONB para datos flexibles (competencias, senderos)
- ✅ **UUID nativo**: Mejor para sistemas distribuidos
- ✅ **Extensibilidad**: Múltiples extensiones disponibles
- ✅ **Comunidad**: Amplia adopción en empresas

**Alternativas consideradas:**
- MySQL: Menos features avanzados para JSON
- MongoDB: No relacional, menos apropiado para datos estructurados

## 3. ORM: SQLAlchemy 2.0

**Decisión:** Usar SQLAlchemy como ORM.

**Razones:**
- ✅ **Maduro y probado**: Estable en producción
- ✅ **Flexibilidad**: Permite queries complejas cuando sea necesario
- ✅ **Type safety**: Soporte para type hints en v2.0
- ✅ **Migraciones**: Integración con Alembic
- ✅ **Async support**: Compatible con FastAPI async

**Alternativas consideradas:**
- Django ORM: Acoplado a Django
- Tortoise ORM: Menos maduro, comunidad más pequeña

## 4. Validación: Pydantic v2

**Decisión:** Usar Pydantic para validación de datos y settings.

**Razones:**
- ✅ **Integración nativa**: FastAPI lo usa internamente
- ✅ **Rendimiento**: v2 está basado en Rust (muy rápido)
- ✅ **Type safety**: Validación en tiempo de ejecución
- ✅ **Serialización**: JSON encoding/decoding automático
- ✅ **Settings management**: BaseSettings para configuración

**Alternativas consideradas:**
- Marshmallow: Más verboso, menos integrado
- Cerberus: No tiene type hints

## 5. Containerización: Docker

**Decisión:** Usar Docker y Docker Compose para desarrollo y despliegue.

**Razones:**
- ✅ **Reproducibilidad**: Mismo entorno en dev y prod
- ✅ **Aislamiento**: Dependencias encapsuladas
- ✅ **Facilidad**: Un comando para levantar todo
- ✅ **Estándar de industria**: Ampliamente adoptado
- ✅ **Multi-servicio**: db, api, ai-mock en un solo compose

**Alternativas consideradas:**
- Virtualenv solo: No aísla servicios externos (PostgreSQL)
- Kubernetes directo: Overkill para desarrollo local

## 6. Identificadores: UUID en lugar de Auto-increment

**Decisión:** Usar UUID (v4) como primary keys.

**Razones:**
- ✅ **Seguridad**: No predecibles, evita enumeración
- ✅ **Distribución**: Generación sin coordinación entre servicios
- ✅ **Merges**: Sin conflictos al combinar datos de múltiples fuentes
- ✅ **RESTful**: IDs no revelan cantidad de recursos

**Desventajas aceptadas:**
- ❌ URLs más largas
- ❌ Índices ligeramente menos eficientes (mitigado con UUIDv7 en futuro)

## 7. Campos JSON para Datos Flexibles

**Decisión:** Usar campos JSON para `evaluation_data`, `recommended_paths`, etc.

**Razones:**
- ✅ **Flexibilidad**: Schema puede evolucionar sin migraciones
- ✅ **Complejidad**: Datos anidados naturalmente representados
- ✅ **AI output**: Estructura de respuesta de IA puede variar
- ✅ **PostgreSQL JSONB**: Soporte nativo con índices y queries

**Desventajas aceptadas:**
- ❌ Validación menos estricta en BD (mitigado con Pydantic)
- ❌ Queries complejas sobre JSON menos eficientes

## 8. Background Tasks para Procesamiento Asíncrono

**Decisión:** Usar FastAPI BackgroundTasks para assessment y career path generation.

**Razones:**
- ✅ **Simplicidad**: No requiere infraestructura adicional (Celery, RabbitMQ)
- ✅ **Suficiente para MVP**: Procesamiento en segundos, no horas
- ✅ **Respuesta inmediata**: Cliente no espera procesamiento largo
- ✅ **Built-in**: Parte de FastAPI, sin dependencias extra

**Limitaciones conocidas:**
- ❌ No persistente: Tareas se pierden si el proceso muere
- ❌ No escalable: Limitado a un worker

**Plan futuro:**
- Migrar a Celery + Redis cuando sea necesario escalar

## 9. AI Service Mock

**Decisión:** Implementar servicio mock de IA en lugar de integración real.

**Razones:**
- ✅ **Desarrollo autónomo**: No depende de servicio externo
- ✅ **Testing**: Resultados predecibles
- ✅ **Demo**: Funciona sin API keys o configuración compleja
- ✅ **Reemplazable**: Fácil cambiar a servicio real más tarde

**Implementación:**
- Servicio FastAPI separado en puerto 8001
- Lógica simple basada en promedios de scores
- Datos mock realistas y completos

## 10. Testing con SQLite

**Decisión:** Usar SQLite en memoria para tests en lugar de PostgreSQL.

**Razones:**
- ✅ **Velocidad**: Tests mucho más rápidos
- ✅ **Simplicidad**: No requiere BD levantada
- ✅ **CI/CD**: Fácil de configurar en pipelines
- ✅ **Aislamiento**: Cada test tiene BD limpia

**Limitaciones:**
- ❌ Dialectos diferentes: Algunas features de PostgreSQL no disponibles
- ❌ UUID handling: Diferente comportamiento

**Mitigación:**
- Tests de integración usan PostgreSQL real

## 11. Sin Autenticación (MVP)

**Decisión:** No implementar autenticación en esta versión.

**Razones:**
- ✅ **Scope**: Prueba técnica enfocada en funcionalidad core
- ✅ **Tiempo**: Priorizar features de negocio
- ✅ **Simplicidad**: Menos complejidad en testing

**Próximos pasos:**
- Implementar JWT authentication
- Roles y permisos (RBAC)
- OAuth2 para integración con SSO

## 12. CORS Permisivo (Desarrollo)

**Decisión:** Permitir todos los orígenes en CORS.

**Razones:**
- ✅ **Desarrollo**: Facilita testing desde diferentes clientes
- ✅ **MVP**: No hay frontend específico definido

**Importante:**
- ⚠️ **Cambiar en producción**: Especificar orígenes permitidos
- ⚠️ **Seguridad**: CORS restrictivo es crítico en prod

## 13. Estructura de Código Modular

**Decisión:** Separar código en módulos (models, routers, schemas, services).

**Razones:**
- ✅ **Mantenibilidad**: Fácil encontrar y modificar código
- ✅ **Testability**: Módulos independientes más fáciles de testear
- ✅ **Escalabilidad**: Nuevos features no ensucian código existente
- ✅ **Colaboración**: Múltiples desarrolladores sin conflictos

**Estructura:**
```
app/
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
├── routers/      # FastAPI endpoints
├── services/     # Business logic
├── config.py     # Settings
├── database.py   # DB connection
└── main.py       # App initialization
```

## 14. Versionado de API

**Decisión:** Incluir `/api/v1` en rutas.

**Razones:**
- ✅ **Breaking changes**: Permite v2 sin romper clientes
- ✅ **Best practice**: Estándar de industria
- ✅ **Futuro**: Facilita evolución de la API

## 15. Soft Delete vs Hard Delete

**Decisión:** Hard delete (sin soft delete implementado).

**Razones:**
- ✅ **Simplicidad**: Menos lógica en queries
- ✅ **MVP**: No hay requerimiento de auditoría

**Futuro:**
- Agregar `deleted_at` y `is_deleted` cuando sea necesario
- Implementar auditoría completa de cambios

## Conclusión

Estas decisiones priorizan:
1. **Rapidez de desarrollo** (MVP funcional)
2. **Simplicidad** (menos dependencias y complejidad)
3. **Estándares de industria** (patterns probados)
4. **Facilidad de testing** (automatización)
5. **Escalabilidad futura** (arquitectura preparada)

Muchas decisiones son apropiadas para un MVP pero necesitarán evolución para producción (autenticación, queue system, monitoring, etc.).
