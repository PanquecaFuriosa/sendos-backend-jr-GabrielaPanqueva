"""
Schemas for EvaluationCycle.
"""
from pydantic import BaseModel, ConfigDict, validator
from datetime import datetime
from uuid import UUID
from typing import Optional


class EvaluationCycleBase(BaseModel):
    """Base schema for EvaluationCycle."""
    name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "ACTIVE"
    
    @validator('end_date')
    def validate_dates(cls, end_date, values):
        """Validate that end_date is after start_date."""
        if end_date and 'start_date' in values:
            if end_date <= values['start_date']:
                raise ValueError('end_date must be after start_date')
        return end_date


class EvaluationCycleCreate(EvaluationCycleBase):
    """Schema for creating a cycle."""
    pass


class EvaluationCycleResponse(EvaluationCycleBase):
    """Schema for cycle response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
