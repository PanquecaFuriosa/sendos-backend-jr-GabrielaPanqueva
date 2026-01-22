"""
Modelo de Career Path (Sendero de Carrera).
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class CareerPathStatus(str, enum.Enum):
    """Estados de un sendero de carrera."""
    GENERATED = "GENERATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class CareerPath(Base):
    """
    Career Path model - AI-generated career path.
    Represents a complete professional development route.
    """
    __tablename__ = "career_paths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Path information
    path_name = Column(String, nullable=False)  # "Ruta de Liderazgo Regional"
    recommended = Column(Boolean, default=False)  # If it's the recommended path
    total_duration_months = Column(Float, nullable=False)
    feasibility_score = Column(Float, nullable=True)  # 0.0 - 1.0
    
    # Status
    status = Column(SQLEnum(CareerPathStatus), default=CareerPathStatus.GENERATED, nullable=False)
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)  # Cuando el usuario lo acepta
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="career_paths")
    steps = relationship("CareerPathStep", back_populates="career_path", cascade="all, delete-orphan", order_by="CareerPathStep.step_order")
    
    def __repr__(self):
        return f"<CareerPath {self.path_name} - {self.status.value}>"
