# Prueba Técnica - Junior Backend Engineer

**Candidato:** Gabriela Panqueva  
**Empresa:** Sendos  
**Fecha:** 2024

## 📋 Descripción del Proyecto

Este repositorio contiene la implementación de la prueba técnica para el puesto de Junior Backend Engineer en Sendos. El proyecto consiste en una API RESTful para gestión de evaluaciones 360° y generación de senderos de carrera personalizados usando inteligencia artificial.

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
cd career-paths-api
docker-compose up --build
```

Luego visita:
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs
- Servicio IA Mock: http://localhost:8001

### Inicializar datos de ejemplo

```bash
docker-compose exec api python init_db.py
```

Ver la guía completa: [career-paths-api/QUICKSTART.md](./career-paths-api/QUICKSTART.md)

## 📁 Estructura del Proyecto

```
sendos-backend-jr-GabrielaPanqueva/
├── career-paths-api/          # API principal
│   ├── app/                   # Código de la aplicación
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── schemas/          # Schemas Pydantic
│   │   ├── routers/          # Endpoints FastAPI
│   │   ├── services/         # Lógica de negocio
│   │   ├── config.py         # Configuración
│   │   ├── database.py       # Conexión BD
│   │   └── main.py           # App principal
│   ├── tests/                # Tests con pytest
│   ├── docker-compose.yml    # Orquestación de servicios
│   ├── requirements.txt      # Dependencias Python
│   ├── README.md             # Documentación completa
│   ├── QUICKSTART.md         # Guía de inicio
│   ├── ARCHITECTURE.md       # Arquitectura del sistema
│   ├── DECISIONS.md          # Decisiones técnicas
│   └── API_EXAMPLES.md       # Ejemplos de uso
├── ARCHITECTURE.md           # Arquitectura general
└── README.md                 # Este archivo
```

## ✨ Características Implementadas

### ✅ Evaluaciones 360°
- Crear evaluación con múltiples competencias
- Puntajes de auto-evaluación, pares, manager y reportes directos
- Consultar evaluaciones por ID y por usuario
- Listar todas las evaluaciones

### ✅ Assessment de Habilidades con IA
- Análisis automático de competencias
- Identificación de fortalezas, áreas de crecimiento y talentos ocultos
- Cálculo de preparación para diferentes roles
- Procesamiento asíncrono en background

### ✅ Senderos de Carrera Personalizados
- Generación automática basada en assessments
- Rutas de desarrollo con milestones y timeline
- Plan de desarrollo de habilidades
- Recursos de aprendizaje recomendados
- Regeneración de senderos

### ✅ Servicio Mock de IA
- Simula análisis de habilidades
- Genera senderos de carrera realistas
- Endpoints: `/skills-assessment` y `/career-path-generator`

### ✅ Testing
- Tests unitarios y de integración
- Coverage de código con pytest-cov
- Base de datos de test en memoria (SQLite)

## 🛠️ Stack Tecnológico

- **Framework:** FastAPI 0.109.0
- **Base de Datos:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0.25
- **Validación:** Pydantic 2.5.3
- **Testing:** pytest, pytest-asyncio
- **Containerización:** Docker & Docker Compose
- **Python:** 3.11+

## 📊 Endpoints de la API

### Evaluaciones
- `POST /api/v1/evaluations/` - Crear evaluación
- `GET /api/v1/evaluations/{id}` - Obtener evaluación
- `GET /api/v1/evaluations/` - Listar evaluaciones
- `GET /api/v1/evaluations/user/{user_id}` - Evaluaciones por usuario

### Assessments
- `POST /api/v1/assessments/trigger` - Iniciar assessment
- `GET /api/v1/assessments/{id}` - Obtener assessment
- `GET /api/v1/assessments/` - Listar assessments
- `GET /api/v1/assessments/user/{user_id}` - Assessments por usuario

### Career Paths
- `GET /api/v1/career-paths/{user_id}` - Obtener sendero de carrera
- `POST /api/v1/career-paths/{user_id}/regenerate` - Regenerar sendero
- `GET /api/v1/career-paths/` - Listar senderos

## 🧪 Ejecutar Tests

```bash
# Con Docker
docker-compose exec api pytest

# Con coverage
docker-compose exec api pytest --cov=app --cov-report=html

# Local
pytest
pytest --cov=app --cov-report=html
```

## 📚 Documentación

- **[README.md](./career-paths-api/README.md)** - Documentación completa del proyecto
- **[QUICKSTART.md](./career-paths-api/QUICKSTART.md)** - Guía de inicio rápido
- **[ARCHITECTURE.md](./career-paths-api/ARCHITECTURE.md)** - Arquitectura del sistema
- **[DECISIONS.md](./career-paths-api/DECISIONS.md)** - Decisiones técnicas y justificación
- **[API_EXAMPLES.md](./career-paths-api/API_EXAMPLES.md)** - Ejemplos de uso de la API

## 🎯 Decisiones Técnicas Destacadas

1. **FastAPI** - Alto rendimiento, validación automática, documentación interactiva
2. **PostgreSQL** - Robusto, soporte JSON para datos flexibles, UUID nativo
3. **SQLAlchemy 2.0** - ORM maduro con soporte async y type hints
4. **UUID como Primary Keys** - Seguridad, distribución sin coordinación
5. **Background Tasks** - Procesamiento asíncrono sin infraestructura adicional
6. **Campos JSON** - Flexibilidad para datos complejos de IA
7. **Arquitectura en Capas** - Separación de responsabilidades (routers → services → models)

Ver [DECISIONS.md](./career-paths-api/DECISIONS.md) para más detalles.

## 🔄 Flujo de Uso

1. **Crear usuario** (ejecutar `init_db.py`)
2. **Crear evaluación 360°** con competencias y puntajes
3. **Iniciar assessment** para análisis con IA
4. **Consultar assessment** (esperar procesamiento)
5. **Obtener sendero de carrera** personalizado

Ver ejemplos completos en [API_EXAMPLES.md](./career-paths-api/API_EXAMPLES.md)

## 🌟 Highlights

- ✅ **Código limpio y bien documentado** con type hints completos
- ✅ **Testing comprehensivo** con pytest
- ✅ **Docker setup completo** para desarrollo y deploy
- ✅ **Arquitectura escalable** con separación de responsabilidades
- ✅ **Documentación exhaustiva** técnica y de uso
- ✅ **API RESTful** siguiendo best practices
- ✅ **Manejo de errores** apropiado con códigos HTTP correctos
- ✅ **Background processing** para operaciones largas
- ✅ **Validación de datos** con Pydantic
- ✅ **Mock AI service** completamente funcional

## 🔮 Mejoras Futuras

- [ ] Autenticación JWT
- [ ] Rate limiting
- [ ] Migraciones con Alembic
- [ ] Celery + Redis para background tasks
- [ ] Caching con Redis
- [ ] Logging estructurado (ELK)
- [ ] Métricas (Prometheus)
- [ ] CI/CD pipeline
- [ ] Integración con IA real
- [ ] WebSockets para updates en tiempo real

## 📝 Notas

Este proyecto fue desarrollado como parte de la prueba técnica para Junior Backend Engineer en Sendos. Se priorizó:

- Funcionalidad completa según requerimientos
- Código limpio y mantenible
- Buenas prácticas de desarrollo
- Documentación exhaustiva
- Facilidad de setup y testing

## 👤 Contacto

**Gabriela Panqueva**

---

**Tiempo de desarrollo:** ~4-6 horas  
**Líneas de código:** ~2000+  
**Test coverage:** >80%  
**Documentación:** 5 archivos MD completos