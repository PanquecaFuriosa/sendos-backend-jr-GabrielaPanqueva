"""
User Model.
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    """
    User Model in the system.
    Represents an organization collaborator.
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    current_position = Column(String, nullable=True)
    department = Column(String, nullable=True)
    years_experience = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evaluations_given = relationship("Evaluation", foreign_keys="Evaluation.evaluator_id", back_populates="evaluator")
    evaluations_received = relationship("Evaluation", foreign_keys="Evaluation.employee_id", back_populates="employee")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    career_paths = relationship("CareerPath", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
