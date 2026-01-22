"""
Schemas for Career Path.
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any, Union


class CareerPathSummaryResponse(BaseModel):
    """Schema for career paths summary (list)."""
    path_id: UUID
    path_name: str
    recommended: bool
    total_duration_months: float
    feasibility_score: Optional[float] = None
    status: str
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_career_path(cls, path):
        """Create from CareerPath model."""
        return cls(
            path_id=path.id,
            path_name=path.path_name,
            recommended=path.recommended,
            total_duration_months=path.total_duration_months,
            feasibility_score=path.feasibility_score,
            status=path.status.value,
            generated_at=path.generated_at
        )


class CareerPathsListResponse(BaseModel):
    """Schema for user's career paths list."""
    career_path_id: UUID  # Most recent record ID
    user_id: UUID
    generated_paths: List[CareerPathSummaryResponse]
    timestamp: datetime


class CompetencyDevelopment(BaseModel):
    """Schema for competency development in a step."""
    name: str
    current_level: int
    required_level: int
    development_actions: List[str]


class CareerPathStepDetail(BaseModel):
    """Schema for step detail."""
    step_number: int
    target_role: str
    duration_months: int
    # Can be either a list of strings or a list of dicts
    required_competencies: Union[List[str], List[Dict[str, Any]]]


class CareerPathStepsResponse(BaseModel):
    """Schema for detailed path steps."""
    path_id: UUID
    path_name: str
    total_duration_months: float
    feasibility_score: Optional[float] = None
    status: str
    steps: List[CareerPathStepDetail]
    
    model_config = ConfigDict(from_attributes=True)


class CareerPathAcceptResponse(BaseModel):
    """Schema for path acceptance response."""
    path_id: UUID
    user_id: UUID
    status: str
    started_at: datetime
    message: str = "Path accepted."
