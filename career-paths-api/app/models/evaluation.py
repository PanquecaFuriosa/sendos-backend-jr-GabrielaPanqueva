"""
Modelo de Evaluación 360°.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class EvaluatorRelationship(str, enum.Enum):
    """Tipo de relación entre evaluador y evaluado."""
    SELF = "SELF"
    MANAGER = "MANAGER"
    PEER = "PEER"
    DIRECT_REPORT = "DIRECT_REPORT"


class EvaluationStatus(str, enum.Enum):
    """Estados de una evaluación."""
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Evaluation(Base):
    """
    Modelo de Evaluación 360°.
    Representa una evaluación realizada por un evaluador hacia un evaluado.
    """
    __tablename__ = "evaluations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Evaluator and evaluatee (N:M relationship with User)
    evaluator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    evaluatee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Evaluation cycle
    cycle_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_cycles.id"), nullable=False, index=True)
    
    # Relationship type
    evaluator_relationship = Column(SQLEnum(EvaluatorRelationship), nullable=False)
    
    # Feedback general
    general_feedback = Column(Text, nullable=True)
    
    # Status
    status = Column(SQLEnum(EvaluationStatus), default=EvaluationStatus.SUBMITTED, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Uniqueness constraint: an evaluator can only evaluate a person once per cycle
    __table_args__ = (
        UniqueConstraint('evaluator_id', 'evaluatee_id', 'cycle_id', name='uq_evaluator_evaluatee_cycle'),
        Index('ix_evaluations_evaluatee_cycle', 'evaluatee_id', 'cycle_id'),
    )
    
    # Relaciones
    evaluator = relationship("User", foreign_keys=[evaluator_id], back_populates="evaluations_given")
    evaluatee = relationship("User", foreign_keys=[evaluatee_id], back_populates="evaluations_received")
    cycle = relationship("EvaluationCycle", back_populates="evaluations")
    details = relationship("EvaluationDetail", back_populates="evaluation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Evaluation {self.evaluator_relationship} from {self.evaluator_id} to {self.evaluatee_id}>"
