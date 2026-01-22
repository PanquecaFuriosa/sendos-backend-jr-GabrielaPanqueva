"""
Evaluation Detail Model.
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class EvaluationDetail(Base):
    """
    Evaluation Detail Model.
    Stores the score and comments for each competency in an evaluation.
    """
    __tablename__ = "evaluation_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relationship with evaluation (weak entity)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Assessed competency
    competency_id = Column(UUID(as_uuid=True), ForeignKey("competencies.id"), nullable=False, index=True)
    
    # Score (1-10)
    score = Column(Integer, nullable=False)
    
    # Optional comments
    comments = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Constraint: score must be between 1 and 10
    __table_args__ = (
        CheckConstraint('score >= 1 AND score <= 10', name='check_score_range'),
    )
    
    # Relationships
    evaluation = relationship("Evaluation", back_populates="details")
    competency = relationship("Competency", back_populates="evaluation_details")
    
    def __repr__(self):
        return f"<EvaluationDetail {self.competency_id}: {self.score}/10>"
