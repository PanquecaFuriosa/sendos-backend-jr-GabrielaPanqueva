"""
Aplicación principal de FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.routers import evaluations, assessments, career_paths

settings = get_settings()

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema de evaluación 360° con generación inteligente de senderos de carrera usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    evaluations.router,
    prefix=f"{settings.API_V1_PREFIX}/evaluations",
    tags=["evaluations"]
)
app.include_router(
    assessments.router,
    prefix=f"{settings.API_V1_PREFIX}/assessments",
    tags=["assessments"]
)
app.include_router(
    career_paths.router,
    prefix=f"{settings.API_V1_PREFIX}/career-paths",
    tags=["career-paths"]
)


@app.get("/")
async def root():
    """Endpoint raíz con información básica de la API."""
    return {
        "message": "Career Paths API - Sendos",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint para verificar que la API está funcionando."""
    return {"status": "healthy"}
