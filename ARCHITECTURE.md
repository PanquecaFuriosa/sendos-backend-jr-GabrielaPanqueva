# Arquitectura del Sistema

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
