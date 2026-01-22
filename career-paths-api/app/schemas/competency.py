"""
Schemas para Competency.
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class CompetencyBase(BaseModel):
    """Base schema para Competency."""
    name: str
    description: Optional[str] = None


class CompetencyCreate(CompetencyBase):
    """Schema to create a competency."""
    pass


class CompetencyResponse(CompetencyBase):
    """Schema para la respuesta de competencia."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
