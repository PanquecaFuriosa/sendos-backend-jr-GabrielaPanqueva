"""
Modelo de Paso del Sendero de Carrera.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class CareerPathStep(Base):
    """
    Modelo de Paso del Sendero de Carrera (weak entity).
    Representa un paso individual en un sendero de carrera.
    """
    __tablename__ = "career_path_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relación con career path (weak entity)
    career_path_id = Column(UUID(as_uuid=True), ForeignKey("career_paths.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Información del paso
    step_order = Column(Integer, nullable=False)  # 1, 2, 3...
    title = Column(String, nullable=False)
    target_role = Column(String, nullable=False)
    duration_months = Column(Integer, nullable=False)
    
    # Competencias requeridas (JSONB)
    required_competencies = Column(JSONB, nullable=True)
    # [
    #   {
    #     "name": "Pensamiento Estratégico",
    #     "current_level": 5,
    #     "required_level": 7,
    #     "development_actions": [...]
    #   }
    # ]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    career_path = relationship("CareerPath", back_populates="steps")
    development_actions = relationship("DevelopmentAction", back_populates="step", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CareerPathStep {self.step_order}: {self.target_role}>"
