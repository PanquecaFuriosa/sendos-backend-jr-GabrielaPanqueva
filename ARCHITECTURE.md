graph TD
    %% Definición de estilos
    classDef client fill:#e1e1e1,stroke:#333,stroke-width:2px;
    classDef gateway fill:#fff9c4,stroke:#333,stroke-width:2px;
    classDef domain fill:#bbdefb,stroke:#333,stroke-width:2px;
    classDef shared fill:#ffccbc,stroke:#333,stroke-width:2px;
    classDef db fill:#f5f5f5,stroke:#333,stroke-width:2px;
    classDef ext fill:#424242,stroke:#fff,stroke-width:2px,color:white;

    %% Nodos Principales
    Client([Cliente / Frontend]) ::: client
    
    subgraph "Infraestructura Backend (Sendos)"
        Gateway[API Gateway] ::: gateway
        
        %% MÓDULO PRINCIPAL
        subgraph "Modulo 1: Evaluaciones y Career"
            Controller[Controllers / API Router] ::: domain
            Service[Services Layer] ::: domain
            Model[Models / Repositories] ::: domain
            BgTask[Background Worker] ::: domain
        end

        %% MÓDULO COMPARTIDO
        subgraph "Modulo Transversal (Shared)"
            NotifyService[Notification Service] ::: shared
        end
    end

    DB[(Base de Datos PostgreSQL)] ::: db
    
    subgraph "Sistemas Externos"
        BlackBoxAI[Sistema IA Sendos] ::: ext
        Provider[Proveedor Email/Push] ::: ext
    end

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
