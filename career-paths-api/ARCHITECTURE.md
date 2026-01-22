# Diseño de Arquitectura del Sistema

## 1.1 Diagrama de componentes
```mermaid
graph TD  
    classDef client fill:#e1e1e1,stroke:#333,stroke-width:2px,color:#000;
    classDef gateway fill:#fff9c4,stroke:#333,stroke-width:2px,color:#000;
    classDef domain fill:#bbdefb,stroke:#333,stroke-width:2px,color:#000;
    classDef shared fill:#ffccbc,stroke:#333,stroke-width:2px,color:#000;
    classDef db fill:#f5f5f5,stroke:#333,stroke-width:2px,color:#000;
    classDef ext fill:#bdbdbd,stroke:#333,stroke-width:2px,color:#000;

    %% --- NODOS Y ESTRUCTURA ---
    Client([Cliente / Frontend])
    
    subgraph SendosBackend ["Infraestructura Backend (Sendos)"]
        Gateway[API Gateway]
        
        %% MÓDULO PRINCIPAL
       subgraph ModuloCore ["Módulo Evaluaciones 360°"]
            Controller[Controllers - Validación HTTP y Rutas]
            Service[Services - Lógica de Negocio Pura]
            Model[Models - Persistencia y Datos]
            BgTask[Background Worker - Procesamiento Asíncrono]
        end

        %% MÓDULO COMPARTIDO
        subgraph ModuloShared ["Modulo Transversal (Shared)"]
            NotifyService[Notification Service]
        end
    end

    DB[(Base de Datos PostgreSQL)]
    
    subgraph External ["Sistemas Externos"]
        BlackBoxAI[Sistema IA Sendos]
        Provider[Proveedor Email/Push]
    end

    %% --- RELACIONES ---
    %% Flujos Síncronos
    Client --> Gateway
    Gateway --> Controller
    Controller --> Service
    Service --> Model
    Model <--> DB

    %% Flujo Asíncrono de IA
    Service -- "1. Encolar Tarea (Async)" --> BgTask
    BgTask <--> BlackBoxAI
    BgTask -. "2. Actualizar Resultado" .-> Model
    
    %% Flujo de Notificación
    BgTask -- "3. Solicitar Notificación" --> NotifyService
    NotifyService -- "4. Enviar" --> Provider

    %% --- ASIGNACIÓN DE ESTILOS ---
    class Client client;
    class Gateway gateway;
    class Controller,Service,Model,BgTask domain;
    class NotifyService shared;
    class DB db;
    class BlackBoxAI,Provider ext;
```

## 1.2 Especificación de Endpoints

### 1.2.1 Crear evaluación 360°
#### POST /api/v1/evaluations
Request: 
```json
{
  "employee_id": "uuid-user-1", 
  "evaluator_id": "uuid-user-2",
  "cycle_id": "uuid-cycle-2026-q1",
  "evaluator_relationship": "PEER",  
  "answers": [
    {
      "competency": "Liderazgo",
      "score": 8,
      "comments": "Demuestra gran capacidad..."
    },
    {
      "competency": "Comunicación",
      "score": 7,
      "comments": "Buena oratoria, falta escucha activa."
    }
  ],
  "general_feedback": "En general, es un excelente compañero de equipo."
}
```
Response 201: 
```json
{
  "id": "uuid-new-eval-1",
  "employee_id": "uuid-user-1",
  "status": "SUBMITTED",
  "created_at": "2026-01-20T10:30:00Z"
}
```
Response 400: 
```json
{
  "detail": "Invalid relationship. For 'SELF' type evaluations, the employee ID and the evaluator ID must match."
}
```
Response 404: 
```json
{
  "detail": "The specified employee (uuid-user-999) does not exist."
}
```
Response 409: 
```json
{
  "detail": "Duplicate evaluation. A record already exists for this employee-evaluator pair in the current cycle."
}
```
Response 422: 
```json
{
  "detail": [
    {
      "loc": ["body", "answers", 0, "score"],
      "msg": "ensure this value is less than or equal to 10",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### 1.2.2 Obtener evaluación
#### GET /api/v1/evaluations/{evaluation_id}
Response 200:
```json
{
  "employee_id": "uuid-user-1", 
  "evaluator_id": "uuid-user-2",
  "cycle_id": "uuid-cycle-2026-q1",
  "evaluator_relationship": "PEER",  
  "answers": [
    {
      "competency": "Liderazgo",
      "score": 8,
      "comments": "Demuestra gran capacidad..."
    },
    {
      "competency_id": "Comunicación",
      "score": 7,
      "comments": "Buena oratoria, falta escucha activa."
    }
  ],
  "general_feedback": "En general, es un excelente compañero de equipo."
  "status": "COMPLETED"
  "updated_at": "2026-01-20T10:35:00Z"
}
```
Response 403: 
```json
{
  "detail": "You do not have permission to view this career plan."
}
```
Response 404: 
```json
{
  "detail": "Evaluation with ID {uuid} not found."
}
```
Response 422: 
```json
{
  "detail": [
    {
      "loc": ["path", "evaluation_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```
### 1.2.3 Procesar con IA
#### POST /api/v1/evaluations/{evaluation_id}/process
Request: 
```json
{}
```
Response 202:
```json
{
  "message": "Processing started",
  "task_id": "uuid-task-99",
  "status": "PROCESSING"
}
```
Response 403: 
```json
{
  "detail": "You do not have permission to modify this evaluation."
}
```
Response 404: 
```json
{
  "detail": "Evaluation with ID {uuid} not found."
}
```
Response 409: 
```json
{
  "detail": "The evaluation is already being processed."
}
```
Response 422: 
```json
{
  "detail": [
    {
      "loc": ["path", "evaluation_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

### 1.2.4 Obtener assessment de habilidades
#### GET /api/v1/skills-assessments/{user_id}
Response 200:
```json
{
  "assessment_id": "uuid-assessment-001",
  "user_id": "uuid-user-1",
  "skills_profile": {
    "strengths": [
      {
        "skill": "Comunicación",
        "proficiency_level": "Avanzado",
        "score": 7.8,
        "evidence": "Consistentemente evaluado positivamente por pares y equipo"
      },
      {
        "skill": "Trabajo en Equipo",
        "proficiency_level": "Avanzado",
        "score": 8.2,
        "evidence": "Excelente colaboración interdepartamental"
      }
    ],
    "growth_areas": [
      {
        "skill": "Liderazgo",
        "current_level": "Intermedio",
        "target_level": "Avanzado",
        "gap_score": 1.2,
        "priority": "Alta"
      },
      {
        "skill": "Pensamiento Estratégico",
        "current_level": "Básico",
        "target_level": "Intermedio",
        "gap_score": 2.1,
        "priority": "Media"
      }
    ],
    "hidden_talents": [
      {
        "skill": "Gestión de Conflictos",
        "evidence": "Identificado a través de análisis de feedback cualitativo",
        "potential_score": 8.5
      }
    ]
  },
  "readiness_for_roles": [
    {
      "role": "Gerente Regional",
      "readiness_percentage": 65,
      "missing_competencies": ["Pensamiento Estratégico", "Gestión de P&L"]
    },
    {
      "role": "Gerente de Capacitación",
      "readiness_percentage": 78,
      "missing_competencies": ["Diseño Instruccional"]
    }
  ],
  "timestamp": "2025-01-15T10:30:00Z"
}
```
Response 403: 
```json
{
  "detail": "You do not have permission to view these skill assessments."
}
```
Response 404: 
```json
{
  "detail": "Employee with ID {uuid} not found."
}
```
Response 404: 
```json
{
  "detail": "No skills assessments have been processed for this employee yet."
}
```
Response 422: 
```json
{
  "detail": [
    {
      "loc": ["path", "user_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

### 1.2.5 Obtener senderos generados
#### GET /api/v1/career-paths/{user_id}
Response 200:
```json
{
  "career_path_id": "uuid-cp-gen-001",
  "user_id": "uuid-user-1",
  "generated_paths": [
    {
      "path_id": "uuid-path-01",
      "path_name": "Ruta de Liderazgo Regional",
      "recommended": true,
      "total_duration_months": 24,
      "feasibility_score": 0.85
    },
    {
      "path_id": "uuid-path-02",
      "path_name": "Ruta de Especialización en Operaciones",
      "recommended": false,
      "total_duration_months": 18,
      "feasibility_score": 0.72
    }
  ],
  "timestamp": "2025-01-15T10:35:00Z"
}
```
Response 403: 
```json
{
  "detail": "You do not have permission to view these paths."
}
```
Response 404: 
```json
{
  "detail": "Employee with ID {uuid} not found."
}
```
Response 404: 
```json
{
  "detail": "No paths have been created for this employee yet."
}
```
Response 422: 
```json
{
  "detail": [
    {
      "loc": ["path", "user_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

### 1.2.6 Obtener pasos detallados de un sendero
#### GET /api/v1/career-paths/{path_id}/steps
Response 200:
```json
{
  "path_id": "uuid-path-01",
  "path_name": "Ruta de Liderazgo Regional",
  "steps": [
    {
      "step_number": 1,
      "target_role": "Gerente de Sucursal Senior",
      "duration_months": 12,
      "required_competencies": [
        {
          "name": "Pensamiento Estratégico",
          "current_level": 5,
          "required_level": 7,
          "development_actions": [
            "Curso: Estrategia de Negocios Avanzada",
            "Proyecto: Plan estratégico para sucursal",
            "Mentoria con Gerente Regional"
          ]
        }
      ]
    },
    {
      "step_number": 2,
      "target_role": "Gerente Regional",
      "duration_months": 12,
      "required_competencies": [
        {
          "name": "Gestión de P&L",
          "current_level": 4,
          "required_level": 8,
          "development_actions": [
            "Certificación: Finanzas para Managers",
            "Shadowing: Director Financiero"
          ]
        }
      ]
    }
  ]
}
```
Response 403: 
```json
{
  "detail": "You do not have permission to view this path."
}
```
Response 404: 
```json
{
  "detail": "Path with ID {uuid} not found."
}
```
Response 422: 
```json
{
  "detail": [
    {
      "loc": ["path", "path_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```
### 1.2.7 Marcar un sendero como aceptado por el usuario
#### POST /api/v1/career-paths/{path_id}/accept
Request: 
```json
{}
```
Response 200:
```json
{
  "path_id": "uuid-path-01",
  "user_id": "uuid-user-1",
  "status": "IN_PROGRESS",
  "started_at": "2026-01-20T12:00:00Z",
  "message": "Path accepted."
}
```
Response 403: 
```json
{
  "detail": "You do not have permission to modify this career plan."
}
```
Response 404:
```json
{ 
  "detail": "Path whit ID {uuid} not found." 
}
```
Response 409:
```json
{ 
  "detail": "This career plan is already underway.." 
}
```
Response 422:
```json
{
  "detail": [
    {
      "loc": ["path", "path_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```
### 1.2.8 (Adicional) Obtener la lista de evaluaciones del usuario
#### GET /api/v1/evaluations
Response 200:
```json
[
  {
    "id": "uuid-eval-1",
    "user_id": "uuid-user-1",
    "evaluator_id": "uuid-user-2",
    "cycle_id": "uuid-cycle-2026-q1",
    "evaluator_relationship": "peer", 
    "status": "COMPLETED",
    "created_at": "2026-01-20T10:00:00Z"
  },
  {
    "id": "uuid-eval-2",
    "user_id": "uuid-user-1",
    "evaluator_id": "uuid-user-3",
    "cycle_id": "uuid-cycle-2026-q1",
    "evaluator_relationship": "manager",
    "status": "SUBMITTED",
    "created_at": "2026-01-20T11:00:00Z"
  }
]
```
Response 401: 
```json
{
   "detail": "Authentication credentials not provided or invalid."
}
```

## 1.3 Diseño de Modelo de Datos
```mermaid
erDiagram
    %% --- BLOQUE 1: ACTORES Y TIEMPO ---
    USERS {
        uuid id PK
        string email
        string full_name
    }

    EVALUATION_CYCLES {
        uuid id PK
        string name
        timestamp start_date
        string status
    }

    COMPETENCIES {
        uuid id PK
        string name
        string description
    }

    %% --- BLOQUE 2: PROCESOS (EVALUACIONES) ---
    EVALUATIONS {
        uuid id PK
        uuid evaluator_id FK
        uuid evaluatee_id FK
        uuid cycle_id FK
        string status
    }

    EVALUATION_DETAILS {
        uuid id PK
        uuid evaluation_id FK "[WEAK] Dep: Evaluation"
        uuid competency_id FK
        int score
        timestamp created_at
    }

    %% --- BLOQUE 3: INTELIGENCIA ARTIFICIAL ---
    SKILLS_ASSESSMENTS {
        uuid id PK
        uuid user_id FK
        uuid cycle_id FK
        jsonb ai_profile
        timestamp created_at
    }

    %% --- BLOQUE 4: PLANES DE CARRERA (CADENA DÉBIL) ---
    CAREER_PATHS {
        uuid id PK
        uuid user_id FK "[WEAK] Dep: User"
        string title
        float match_score
        timestamp created_at
    }

    CAREER_PATH_STEPS {
        uuid id PK
        uuid career_path_id FK "[WEAK] Dep: Path"
        int step_order
        string title
    }

    DEVELOPMENT_ACTIONS {
        uuid id PK
        uuid step_id FK "[WEAK] Dep: Step"
        string type
        string description
    }

    %% --- RELACIONES (Ordenadas para evitar cruces) ---

    %% Usuarios y Ciclos
    USERS ||--o{ EVALUATIONS : "recibe/realiza"
    EVALUATION_CYCLES ||--o{ EVALUATIONS : "agrupa"
    
    %% Detalles de Evaluación
    EVALUATIONS ||--|{ EVALUATION_DETAILS : "tiene detalles"
    COMPETENCIES ||--o{ EVALUATION_DETAILS : "se mide en"

    %% IA
    USERS ||--o{ SKILLS_ASSESSMENTS : "tiene perfil IA"
    EVALUATION_CYCLES ||--o{ SKILLS_ASSESSMENTS : "contexto"

    %% Senderos (Cascada hacia abajo)
    USERS ||--o{ CAREER_PATHS : "proyecta"
    CAREER_PATHS ||--|{ CAREER_PATH_STEPS : "pasos"
    CAREER_PATH_STEPS ||--o{ DEVELOPMENT_ACTIONS : "acciones"
```

### Constraints y validaciones
#### 1.3.1 Unicidad de Evaluaciones
Regla: No pueden existir dos evaluaciones distintas para el mismo par (Evaluador, Evaluado) dentro del mismo Ciclo.
Sea E el conjunto de todas las Evaluaciones.
Sea e.evaluator, e.evaluatee, e.cycle los atributos de una evaluación e.

∀ e1, e2 ∈ E :
    (e1.evaluator = e2.evaluator ∧
     e1.evaluatee = e2.evaluatee ∧
     e1.cycle = e2.cycle)
    ⟹ e1 = e2

#### 1.3.2 Validez de Puntajes
Regla: Todo puntaje asignado en un detalle de evaluación debe estar dentro del rango [1, 10].
Sea D el conjunto de todos los Detalles de Evaluación (EvaluationDetails).
Sea d.score el puntaje asignado.

∀ d ∈ D : (d.score ≥ 1 ∧ d.score ≤ 10)

#### 1.3.2 Coherencia Temporal de Ciclos
Regla: Un ciclo no puede terminar antes de empezar.
Sea C el conjunto de Ciclos de Evaluación.

∀ c ∈ C : c.start_date < c.end_date

## 1.4 Flujo de Procesamiento Completo
### 1.4.1 Flujo 1: Procesamiento de Evaluación 360°
1. Un usuario completa todas sus evaluaciones 360° (self, peers, manager, direct reports)
2. El sistema detecta que el ciclo está completo
3. Se dispara el procesamiento automático con IA
4. Se genera el Skills Assessment
5. Se genera el Career Path
6. Se notifica al usuario

Este flujo describe el proceso "Core" del sistema. Dado que los servicios de IA pueden tardar entre 5 y 30 segundos en responder, este proceso se maneja de forma asíncrona utilizando BackgroundTasks de FastAPI para no bloquear al cliente

#### Diagrama de secuencia
```mermaid
sequenceDiagram
    participant User as Cliente (Frontend)
    participant API as Backend FastAPI
    participant DB as Base de Datos
    participant Worker as Tarea en 2do Plano
    participant AISkills as Servicio IA Habilidades
    participant AICareer as Servicio IA Carrera

    User->>API: POST /evaluations (Envía evaluación)
    API->>DB: Guardar Evaluación
    API->>DB: ¿Ciclo Completado? (Auto + Jefe + Pares)
    
    alt Ciclo Incompleto
        API-->>User: 201 Created (Estado: Pendiente)
    else Ciclo Completo
        API->>Worker: Encolar "Procesar Análisis IA"
        API-->>User: 201 Created (Estado: Procesando)
        
        Note over Worker: Inicia Proceso Asíncrono
        
        %% Paso 1: Evaluación de Habilidades
        Worker->>DB: Obtener todas las evaluaciones del ciclo
        Worker->>AISkills: POST /assess_skills (Datos Crudos)
        AISkills-->>Worker: JSON Perfil de Habilidades
        Worker->>DB: Insertar en tabla skills_assessments
        
        %% Paso 2: Generación de Senderos (Depende del anterior)
        Worker->>DB: Obtener Perfil Usuario + ID Assessment
        Worker->>AICareer: POST /generate_paths
        AICareer-->>Worker: JSON Senderos de Carrera
        Worker->>DB: Insertar en tablas career_paths y steps
        
        %% Paso 3: Finalización
        Worker->>DB: Actualizar Estado Ciclo = COMPLETADO
        Worker->>User: (Simulado) Enviar Notificación "Resultados Listos"
    end
```

El flujo comienza automáticamente en cuanto el sistema valida que se han completado todas las evaluaciones requeridas del empleado, incluyendo la autoevaluación, la del jefe y la de los pares. Para optimizar la experiencia de usuario, se diseñó este proceso de manera asíncrona utilizando BackgroundTasks de FastAPI; lo cual permite devolver una respuesta exitosa de inmediato mientras la lógica pesada se ejecuta en segundo plano.

Luego, el sistema toma las calificaciones numéricas "crudas" y las procesa a través de dos capas de inteligencia artificial: la primera transforma esos datos en un perfil cualitativo de fortalezas y debilidades en formato JSONB, y la segunda utiliza ese perfil junto con la jerarquía organizacional para proponer planes de carrera.

### 1.4.2 Flujo 2: Consulta de Senderos de Carrera
1. Un usuario consulta sus senderos disponibles
2. El sistema retorna los senderos con su estado actual
3. El usuario puede ver detalles de un sendero específico
```mermaid
sequenceDiagram
    participant User as Cliente (Usuario)
    participant API as Backend FastAPI
    participant DB as Base de Datos

    %% Consulta de Lista (Resumen)
    User->>API: GET /career-paths/{user_id}
    API->>DB: SELECT * FROM career_paths WHERE user_id = ...
    DB-->>API: Retorna Lista [Sendero A, Sendero B]
    API-->>User: 200 OK (JSON Resumen: Título y Score)

    %% Consulta de Detalle (Carga Diferida)
    User->>API: GET /career-paths/{path_id}/steps
    API->>DB: JOIN career_paths + steps + actions
    DB-->>API: Retorna Jerarquía Completa
    API-->>User: 200 OK (JSON Detallado con pasos y cursos)
```

## 1.5 Especificaciones para Agentes de Código
A continuación se presentan las instrucciones técnicas precisas diseñadas para ser ingresadas en asistentes de codificación (Cursor/Copilot), asegurando la generación de código robusto y alineado con la arquitectura. Además de las instrucciones, se le suministró al agente, el contexto de su rol y de lo que debe hacer para que éste fuese capaz de "meterse" en dicho rol y "entender" un poco más lo que se requiere.

### a) Modelo de datos SQLAlchemy para la tabla de Skills Assessment
Eres el Ingeniero de Software Senior de Sendos, una plataforma de gestión de recursos humanos, eres experto en bases de datos PostgreSQL y SQLAlchemy. Tu trabajo es generar el código para la entidad SkillsAssessment siguiendo la especificaciones estrictas que se enlistan a continuación:

1. Configuración Base:
   - Usa la sintaxis moderna de SQLAlchemy 2.0 (Mapped, mapped_column).
   - El modelo debe heredar de Base.
   - Nombre de tabla: skills_assessments.

2. Campos Requeridos:
   - id: UUID, Primary Key, valor por defecto uuid4.
   - user_id: UUID, ForeignKey a users.id, no nulo, indexado.
   - cycle_id: UUID, ForeignKey a evaluation_cycles.id, no nulo.
   - ai_profile: JSONB, no nulo. Aquí se guardará el análisis cualitativo (fortalezas/debilidades).
   - created_at: DateTime (UTC), por defecto func.now().

3. Relaciones:
   - user: Relación M:1 con la tabla User (back_populates="assessments").
   - cycle: Relación M:1 con la tabla EvaluationCycle.

4. Restricciones (Constraints):
   - Crea un UniqueConstraint compuesto para (user_id, cycle_id). Un usuario solo debe tener un perfil de IA por ciclo.

5. Extras:
   - Incluye un método __repr__ útil para debugging que muestre el ID y el user_id.
   - Asegúrate de importar los tipos necesarios de sqlalchemy y sqlalchemy.dialects.postgresql.

### b) Endpoint POST para crear una evaluación
Eres el Ingeniero de Software Senior de Sendos, una plataforma de gestión de recursos humanos, eres experto en FastAPI y arquitectura asíncrona. Tu tarea es generar el código para el endpoint de creación de evaluaciones, asegurando que la experiencia de usuario sea rápida aunque el procesamiento posterior sea lento. Sigue estas especificaciones:

1. Firma del Endpoint:
   - Archivo: app/api/routers/evaluations.py.
   - Decorador: @router.post("/", status_code=201).
   - Respuesta: Debe devolver el objeto creado usando el esquema EvaluationResponse.

2. Validación de Datos (Pydantic):
   - Entrada: Esquema EvaluationCreate.
   - Regla Crítica: Valida que el campo score (dentro de los detalles) sea un entero estrictamente entre 1 y 10.
   - Si la validación falla, el framework debe levantar HTTPException(422) automáticamente.
3. Lógica de Persistencia (Base de Datos):
   - Usa AsyncSession inyectada vía Depends.
   - Paso 1: Verifica si el cycle_id existe. Si no, lanza HTTPException(404).
   - Paso 2: Intenta insertar la evaluación. Envuelve esto en un bloque try/except.
   - Manejo de Error Específico: Si SQLAlchemy lanza un IntegrityError, significa que se violó el constraint de unicidad (ya existe una evaluación para este par en este ciclo). En este caso, lanza HTTPException(409, detail="Evaluation already exists").

4. Desacoplamiento (Background Tasks):
   - Inyecta BackgroundTasks en la función del controlador.
   - Lógica: Una vez confirmado el commit en la BD, llama a la función de servicio service.trigger_ai_pipeline(user_id).
   - Instrucción de Claridad: Esta llamada debe pasarse obligatoriamente a background_tasks.add_task(...). Bajo ninguna circunstancia debes usar await en esta línea, ya que bloquearía la respuesta HTTP al cliente.

5. Documentación OpenAPI (Swagger):
   - Agrega un summary="Submit a new 360 evaluation".
   - En el parámetro responses del decorador, documenta explícitamente:
     * 404: "Cycle or User not found".
     * 409: "Evaluation duplicate constraint violation".

### c) Servicio de integración con el AI Career Path Generator

Eres el Ingeniero de Backend Senior de Sendos, una plataforma de gestión de recursos humanos. Eres especialista en integración de sistemas. Tu tarea es implementar `AICareerService` en `app/services/ai_service.py`. Debes crear un **Mock Robusto** que simule el comportamiento real del motor de una IA que genera rutas de crecimiento profesional como empleado.

1. Definición Asíncrona:
   - Clase: `AICareerService`.
   - Método: `async def generate_career_path(self, user_profile: Dict) -> Dict`.

2. Simulación de Latencia (Realismo):
   - La IA es un proceso pesado. Usa `await asyncio.sleep(random.uniform(2.0, 5.0))` para simular el tiempo de inferencia.

4. Resiliencia (Retry Logic):
   - Implementa resiliencia usando `tenacity`.
   - Configuración: Máximo 3 intentos con **Backoff Exponencial** (multiplier=1, min=2, max=10).
   - Simulación de Fallos: Haz que el 10% de las peticiones fallen aleatoriamente (`ConnectionError`) para validar que el mecanismo de reintento funciona.

4. Contrato de Datos (Output):
   - Estructura Requerida del Mock:
```json
{
  "career_path_id": "uuid",
  "user_id": "uuid",
  "generated_paths": [
    {
      "path_id": "uuid",
      "path_name": "Ruta de Liderazgo Regional",
      "recommended": true,
      "total_duration_months": 24,
      "feasibility_score": 0.85,
      "steps": [
        {
          "step_number": 1,
          "target_role": "Gerente de Sucursal Senior",
          "duration_months": 12,
          "required_competencies": [
            {
              "name": "Pensamiento Estratégico",
              "current_level": 5,
              "required_level": 7,
              "development_actions": [
                "Curso: Estrategia de Negocios Avanzada",
                "Proyecto: Plan estratégico para sucursal",
                "Mentoría con Gerente Regional"
              ]
            }
          ]
        },
        {
          "step_number": 2,
          "target_role": "Gerente Regional",
          "duration_months": 12,
          "required_competencies": [
            {
              "name": "Gestión de P&L",
              "current_level": 4,
              "required_level": 8,
              "development_actions": [
                "Certificación: Finanzas para Managers",
                "Shadowing: Director Financiero",
                "Proyecto: Análisis de rentabilidad regional"
              ]
            }
          ]
        }
      ]
    },
    {
      "path_id": "uuid",
      "path_name": "Ruta de Especialización en Operaciones",
      "recommended": false,
      "total_duration_months": 18,
      "feasibility_score": 0.72,
      "steps": [...]
    }
  ],
  "timestamp": "2025-01-15T10:35:00Z"
}

```

5. Manejo de Timeouts:
   - Si el proceso total excede los **10 segundos**, lanza `AITimeoutError`.

7. Observabilidad:
   - Usa `logging` para registrar: Inicio del proceso (INFO), Intentos fallidos (WARNING) y Éxito final con el ID del usuario (INFO).

## 1.6 Patrones de Diseño Aplicados

### Repository Pattern (Implícito)
Los modelos SQLAlchemy actúan como repositorios, encapsulando acceso a datos.

### Service Layer Pattern
Capa `services/` contiene lógica de negocio, separada de HTTP y persistencia.

### DTO Pattern
Pydantic schemas actúan como Data Transfer Objects entre capas.

### Dependency Injection
FastAPI `Depends()` inyecta dependencias (DB session, settings, etc.).

### Factory Pattern
Funciones helper para crear objetos de prueba en tests.

## 1.7 Consideraciones de Producción

### Pendientes para Producción

**Seguridad:**
- [ ] Implementar autenticación JWT
- [ ] Rate limiting por usuario/IP
- [ ] Validación de roles y permisos
- [ ] HTTPS obligatorio
- [ ] Secret key rotation
- [ ] SQL injection prevention (ya mitigado con ORM)
- [ ] XSS prevention en responses

**Performance:**
- [ ] Caché con Redis (assessments, career paths)
- [ ] Connection pooling optimizado
- [ ] Índices adicionales basados en queries reales
- [ ] Query optimization
- [ ] Lazy loading para relaciones grandes

**Escalabilidad:**
- [ ] Migrar background tasks a Celery
- [ ] Load balancer (Nginx/HAProxy)
- [ ] Multiple replicas de API
- [ ] Read replicas de PostgreSQL
- [ ] CDN para assets estáticos

**Observabilidad:**
- [ ] Logging estructurado (JSON)
- [ ] Distributed tracing (Jaeger/OpenTelemetry)
- [ ] Metrics (Prometheus)
- [ ] Dashboards (Grafana)
- [ ] Error tracking (Sentry)
- [ ] Alerting (PagerDuty)

**Datos:**
- [ ] Backups automáticos de PostgreSQL
- [ ] Point-in-time recovery
- [ ] Disaster recovery plan
- [ ] Data retention policies
- [ ] GDPR compliance (soft delete, exportación de datos)

**DevOps:**
- [ ] CI/CD pipeline completo
- [ ] Automated testing en PRs
- [ ] Deployment canary/blue-green
- [ ] Infrastructure as Code (Terraform)
- [ ] Secrets management (Vault, AWS Secrets Manager)

## 1.8 Conclusión de Diseño

La arquitectura implementada prioriza:

1. **Simplicidad**: Decisiones pragmáticas para MVP funcional
2. **Estándares**: Patterns probados de la industria
3. **Escalabilidad**: Diseño preparado para crecer
4. **Mantenibilidad**: Código claro y bien organizado
5. **Flexibilidad**: Fácil evolucionar y cambiar

Las decisiones tomadas son apropiadas para un MVP/prueba técnica pero requieren evolución para un sistema de producción enterprise-grade. La arquitectura modular facilita estas mejoras incrementales sin reescritura completa.
