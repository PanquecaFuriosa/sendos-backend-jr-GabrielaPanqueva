"""
Schemas para Career Path.
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any, Union


class CareerPathSummaryResponse(BaseModel):
    """Schema para resumen de career paths (lista)."""
    path_id: UUID
    path_name: str
    recommended: bool
    total_duration_months: float
    feasibility_score: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_career_path(cls, path):
        """Create from CareerPath model."""
        return cls(
            path_id=path.id,
            path_name=path.path_name,
            recommended=path.recommended,
            total_duration_months=path.total_duration_months,
            feasibility_score=path.feasibility_score
        )


class CareerPathsListResponse(BaseModel):
    """Schema para lista de career paths de un usuario."""
    career_path_id: UUID  # ID del registro más reciente
    user_id: UUID
    generated_paths: List[CareerPathSummaryResponse]
    timestamp: datetime


class CompetencyDevelopment(BaseModel):
    """Schema para desarrollo de competencia en un paso."""
    name: str
    current_level: int
    required_level: int
    development_actions: List[str]


class CareerPathStepDetail(BaseModel):
    """Schema para detalle de un paso."""
    step_number: int
    target_role: str
    duration_months: int
    # Can be either a list of strings or a list of dicts
    required_competencies: Union[List[str], List[Dict[str, Any]]]


class CareerPathStepsResponse(BaseModel):
    """Schema para pasos detallados de un sendero."""
    path_id: UUID
    path_name: str
    steps: List[CareerPathStepDetail]
    
    model_config = ConfigDict(from_attributes=True)


class CareerPathAcceptResponse(BaseModel):
    """Schema para respuesta de aceptación de sendero."""
    path_id: UUID
    user_id: UUID
    status: str
    started_at: datetime
    message: str = "Path accepted."
