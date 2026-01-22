"""
Configuración y fixtures para tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from uuid import uuid4

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.evaluation_cycle import EvaluationCycle, CycleStatus
from app.models.competency import Competency

# Base de datos de test en PostgreSQL (misma instancia, diferente DB)
SQLALCHEMY_DATABASE_URL = "postgresql://sendos:sendos123@localhost:5432/sendos_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db function to use test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def db_session():
    """Fixture for database session."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """Fixture para cliente de test."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# Fixtures de datos para tests
# ============================================================================

@pytest.fixture()
def sample_users(db_session: Session):
    """Fixture que crea usuarios de prueba."""
    users = [
        User(
            id=uuid4(),
            full_name="Juan Pérez",
            email="juan.perez@example.com",
            current_position="Desarrollador Senior",
            department="Tecnología"
        ),
        User(
            id=uuid4(),
            full_name="María González",
            email="maria.gonzalez@example.com",
            current_position="Gerente de Desarrollo",
            department="Tecnología"
        ),
        User(
            id=uuid4(),
            full_name="Carlos Rodríguez",
            email="carlos.rodriguez@example.com",
            current_position="Tech Lead",
            department="Tecnología"
        )
    ]
    
    for user in users:
        db_session.add(user)
    db_session.commit()
    
    for user in users:
        db_session.refresh(user)
    
    return users


@pytest.fixture()
def sample_cycle(db_session: Session):
    """Fixture que crea un ciclo de evaluación activo."""
    cycle = EvaluationCycle(
        id=uuid4(),
        name="Q1 2026",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now() + timedelta(days=30),
        status=CycleStatus.ACTIVE
    )
    
    db_session.add(cycle)
    db_session.commit()
    db_session.refresh(cycle)
    
    return cycle


@pytest.fixture()
def sample_competencies(db_session: Session):
    """Fixture que crea competencias de prueba."""
    competencies = [
        Competency(id=uuid4(), name="Liderazgo", description="Capacidad de liderazgo"),
        Competency(id=uuid4(), name="Comunicación", description="Habilidades de comunicación"),
        Competency(id=uuid4(), name="Trabajo en Equipo", description="Colaboración efectiva"),
        Competency(id=uuid4(), name="Resolución de Problemas", description="Pensamiento crítico"),
        Competency(id=uuid4(), name="Adaptabilidad", description="Flexibilidad ante cambios")
    ]
    
    for competency in competencies:
        db_session.add(competency)
    db_session.commit()
    
    for competency in competencies:
        db_session.refresh(competency)
    
    return competencies
