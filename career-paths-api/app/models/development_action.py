"""
Modelo de Acción de Desarrollo.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class DevelopmentAction(Base):
    """
    Modelo de Acción de Desarrollo (weak entity).
    Representa una acción específica de desarrollo dentro de un paso.
    """
    __tablename__ = "development_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relación con step (weak entity)
    step_id = Column(UUID(as_uuid=True), ForeignKey("career_path_steps.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Información de la acción
    type = Column(String, nullable=False)  # "training", "project", "mentoring", etc.
    description = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    step = relationship("CareerPathStep", back_populates="development_actions")
    
    def __repr__(self):
        return f"<DevelopmentAction {self.type}: {self.description[:30]}>"
