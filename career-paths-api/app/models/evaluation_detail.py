"""
Modelo de Detalle de Evaluación.
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class EvaluationDetail(Base):
    """
    Modelo de Detalle de Evaluación.
    Almacena el puntaje y comentarios para cada competencia en una evaluación.
    """
    __tablename__ = "evaluation_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relación con evaluación (weak entity)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Competencia evaluada
    competency_id = Column(UUID(as_uuid=True), ForeignKey("competencies.id"), nullable=False, index=True)
    
    # Puntaje (1-10)
    score = Column(Integer, nullable=False)
    
    # Comentarios opcionales
    comments = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Constraint: score debe estar entre 1 y 10
    __table_args__ = (
        CheckConstraint('score >= 1 AND score <= 10', name='check_score_range'),
    )
    
    # Relaciones
    evaluation = relationship("Evaluation", back_populates="details")
    competency = relationship("Competency", back_populates="evaluation_details")
    
    def __repr__(self):
        return f"<EvaluationDetail {self.competency_id}: {self.score}/10>"
