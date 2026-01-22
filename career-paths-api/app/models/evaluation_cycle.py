"""
Evaluation Cycle Model.
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class CycleStatus(str, enum.Enum):
    """Possible evaluation cycle statuses."""
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


class EvaluationCycle(Base):
    """
    Evaluation Cycle Model.
    Groups evaluations by period (e.g., Q1 2026).
    """
    __tablename__ = "evaluation_cycles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # e.g., "2026-Q1"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(CycleStatus), default=CycleStatus.ACTIVE, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evaluations = relationship("Evaluation", back_populates="cycle", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="cycle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EvaluationCycle {self.name} - {self.status}>"
