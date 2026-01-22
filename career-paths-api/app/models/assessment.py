"""
Modelo de Assessment (Evaluación de Habilidades con IA).
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class ProcessingStatus(str, enum.Enum):
    """Estados de procesamiento del assessment."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Assessment(Base):
    """
    Modelo de Assessment - Análisis de habilidades generado por IA.
    Almacena los resultados del análisis de competencias usando IA.
    Un usuario solo puede tener un assessment por ciclo.
    """
    __tablename__ = "assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    cycle_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_cycles.id"), nullable=False, index=True)
    
    # AI profile (JSONB for better performance in PostgreSQL)
    ai_profile = Column(JSONB, nullable=True)
    # Structure according to architecture spec:
    # {
    #   "strengths": [{skill, proficiency_level, score, evidence}],
    #   "growth_areas": [{skill, current_level, target_level, gap_score, priority}],
    #   "hidden_talents": [{skill, evidence, potential_score}],
    #   "readiness_for_roles": [{role, readiness_percentage, missing_competencies}]
    # }
    
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint: un usuario solo puede tener un assessment por ciclo
    __table_args__ = (
        UniqueConstraint('user_id', 'cycle_id', name='uq_user_cycle_assessment'),
    )
    
    # Relaciones
    user = relationship("User", back_populates="assessments")
    cycle = relationship("EvaluationCycle", back_populates="assessments")
    
    def __repr__(self):
        return f"<Assessment {self.id} - Status: {self.processing_status.value}>"
