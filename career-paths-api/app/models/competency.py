"""
Competency Model.
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Competency(Base):
    """
    Competency Model.
    Catalog of assessable competencies (e.g., Leadership, Communication).
    """
    __tablename__ = "competencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evaluation_details = relationship("EvaluationDetail", back_populates="competency", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Competency {self.name}>"
