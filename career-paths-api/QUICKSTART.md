# Guía de Inicio Rápido - Career Paths API

Esta guía te ayudará a poner en marcha el proyecto de manera rápida y sencilla.

## Opción 1: Usando Docker (Recomendado) 🐳

### Pre-requisitos
- Docker Desktop instalado
- Docker Compose instalado

### Pasos

1. **Navegar al directorio del proyecto:**
   ```bash
   cd career-paths-api
   ```

2. **Levantar todos los servicios:**
   ```bash
   docker-compose up --build
   ```

   Esto levantará:
   - PostgreSQL en puerto 5432
   - API en puerto 8000
   - Servicio mock de IA en puerto 8001

3. **Verificar que todo funciona:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Acceder a la documentación:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

5. **(Opcional) Inicializar datos de ejemplo:**

   Ejecutar en otro terminal mientras los contenedores están corriendo:
   ```bash
   docker-compose exec api python init_db.py
   ```

   Esto creará 3 usuarios de ejemplo.

6. **Probar el flujo completo:**

   Ver ejemplos de requests en [API_EXAMPLES.md](./API_EXAMPLES.md)

---

## Opción 2: Instalación Manual (Desarrollo local) 🛠️

### Pre-requisitos
- Python 3.11 o superior
- PostgreSQL 15 o superior instalado y corriendo

### Pasos

1. **Crear y activar entorno virtual:**
   ```bash
   cd career-paths-api
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar base de datos:**
   
   Crear base de datos en PostgreSQL:
   ```sql
   CREATE DATABASE career_paths_db;
   CREATE USER sendos WITH PASSWORD 'sendos123';
   GRANT ALL PRIVILEGES ON DATABASE career_paths_db TO sendos;
   ```

4. **Configurar variables de entorno:**
   
   Copiar `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Editar `.env` y ajustar la URL de la base de datos si es necesario.

5. **Inicializar base de datos:**
   ```bash
   python init_db.py
   ```

6. **Levantar el servicio mock de IA (en un terminal):**
   ```bash
   python ai_mock_service.py
   ```

7. **Levantar la API (en otro terminal):**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Verificar que funciona:**
   ```bash
   curl http://localhost:8000/health
   ```

9. **Acceder a la documentación:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## Ejecución de Tests 🧪

### Con Docker:
```bash
docker-compose exec api pytest
```

### Con coverage:
```bash
docker-compose exec api pytest --cov=app --cov-report=html
```

### Manual:
```bash
pytest
pytest --cov=app --cov-report=html
```

Ver reporte de coverage:
```bash
# Windows
start htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Mac
open htmlcov/index.html
```

---

## Flujo de Uso Completo 🔄

### 1. Obtener IDs de usuarios
```bash
# Ver usuarios creados en los logs después de init_db.py
# O consultar directamente:
docker-compose exec db psql -U sendos -d career_paths_db -c "SELECT id, full_name, email FROM users;"
```

### 2. Crear evaluación 360°

```bash
curl -X POST "http://localhost:8000/api/v1/evaluations/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID_AQUI",
    "evaluation_data": {
      "competencies": [
        {
          "name": "Liderazgo",
          "self_score": 8,
          "peer_scores": [7, 8, 9],
          "manager_score": 7,
          "direct_report_scores": [8, 8]
        }
      ]
    },
    "current_position": "Analista Senior",
    "years_experience": "5"
  }'
```

Guarda el `id` de la evaluación retornada.

### 3. Iniciar assessment

```bash
curl -X POST "http://localhost:8000/api/v1/assessments/trigger" \
  -H "Content-Type: application/json" \
  -d '{"evaluation_id": "EVALUATION_ID_AQUI"}'
```

### 4. Verificar assessment (esperar 2-3 segundos)

```bash
curl http://localhost:8000/api/v1/assessments/ASSESSMENT_ID_AQUI
```

### 5. Obtener sendero de carrera

```bash
curl http://localhost:8000/api/v1/career-paths/USER_ID_AQUI
```

Si retorna 202, esperar y volver a llamar.

---

## Comandos Útiles 🔧

### Docker

```bash
# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api

# Parar servicios
docker-compose down

# Parar y eliminar volúmenes (reinicio completo)
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache

# Entrar a un contenedor
docker-compose exec api bash
docker-compose exec db psql -U sendos -d career_paths_db
```

### Base de Datos

```bash
# Conectar a PostgreSQL (dentro del contenedor)
docker-compose exec db psql -U sendos -d career_paths_db

# Ver tablas
\dt

# Ver datos de usuarios
SELECT * FROM users;

# Ver evaluaciones
SELECT id, user_id, status, created_at FROM evaluations;

# Ver assessments
SELECT id, user_id, processing_status, created_at FROM assessments;
```

---

## Solución de Problemas 🔍

### Puerto 8000 ya está en uso
```bash
# Cambiar el puerto en docker-compose.yml
ports:
  - "8080:8000"  # Usar 8080 en lugar de 8000
```

### Base de datos no conecta
```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps

# Ver logs de la base de datos
docker-compose logs db

# Reiniciar solo la BD
docker-compose restart db
```

### Tests fallan
```bash
# Asegurarse de que no hay procesos usando la BD de test
rm test.db

# Ejecutar tests con más detalles
pytest -v -s
```

### AI Service no responde
```bash
# Verificar que está corriendo
curl http://localhost:8001/

# Ver logs
docker-compose logs ai-mock

# Reiniciar servicio
docker-compose restart ai-mock
```

---

## Próximos Pasos 📚

1. Lee [ARCHITECTURE.md](./ARCHITECTURE.md) para entender la arquitectura
2. Lee [DECISIONS.md](./DECISIONS.md) para entender las decisiones técnicas
3. Revisa [API_EXAMPLES.md](./API_EXAMPLES.md) para más ejemplos de uso
4. Explora la documentación interactiva en http://localhost:8000/docs

---

## Recursos Adicionales 🌐

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

¡Feliz desarrollo! 🚀
