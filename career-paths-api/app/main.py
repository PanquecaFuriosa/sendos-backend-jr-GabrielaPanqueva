"""
FastAPI main application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.routers import evaluations, assessments, career_paths

settings = get_settings()

# Create database tables
# NOTE: Tables are now created via Alembic migrations
# Run: alembic upgrade head
# Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema de evaluación 360° con generación inteligente de senderos de carrera usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    evaluations.router,
    prefix=f"{settings.API_V1_PREFIX}/evaluations",
    tags=["evaluations"]
)
app.include_router(
    assessments.router,
    prefix=f"{settings.API_V1_PREFIX}/skills-assessments",
    tags=["skills-assessments"]
)
app.include_router(
    career_paths.router,
    prefix=f"{settings.API_V1_PREFIX}/career-paths",
    tags=["career-paths"]
)


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Career Paths API - Sendos",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy"}
