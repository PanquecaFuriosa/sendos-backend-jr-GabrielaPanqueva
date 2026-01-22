"""
Schemas for Evaluation (360° Evaluation).
"""
from pydantic import BaseModel, Field, ConfigDict, validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class EvaluationAnswerCreate(BaseModel):
    """Schema for an evaluation answer - External API uses name."""
    competency: str  # Architecture spec uses competency name, not ID
    score: int = Field(..., ge=1, le=10, description="Score must be between 1 and 10")
    comments: Optional[str] = None


class EvaluationCreate(BaseModel):
    """Schema to create a new evaluation."""
    evaluator_id: UUID
    employee_id: UUID  # Architecture spec uses 'employee_id' instead of 'evaluatee_id'
    cycle_id: UUID
    evaluator_relationship: str = Field(..., description="SELF, MANAGER, PEER, or DIRECT_REPORT")
    answers: List[EvaluationAnswerCreate]
    general_feedback: Optional[str] = None
    
    @validator('evaluator_relationship')
    def validate_relationship(cls, v):
        """Validate that the relationship type is valid."""
        valid_types = ["SELF", "MANAGER", "PEER", "DIRECT_REPORT"]
        if v not in valid_types:
            raise ValueError(f'evaluator_relationship must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('answers')
    def validate_answers(cls, v):
        """Validate that there is at least one answer."""
        if not v or len(v) == 0:
            raise ValueError('At least one answer is required')
        return v
    
    @validator('employee_id')
    def validate_self_evaluation(cls, employee_id, values):
        """For SELF evaluations, evaluator_id and employee_id must match."""
        if 'evaluator_id' in values and 'evaluator_relationship' in values:
            if values['evaluator_relationship'] == 'SELF':
                if employee_id != values['evaluator_id']:
                    raise ValueError("Invalid relationship. For 'SELF' type evaluations, the employee ID and the evaluator ID must match.")
        return employee_id


class EvaluationResponse(BaseModel):
    """Schema for evaluation response according to architecture."""
    id: UUID
    employee_id: UUID
    evaluator_id: UUID
    cycle_id: UUID
    evaluator_relationship: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EvaluationDetailResponse(BaseModel):
    """Schema for evaluation detail with competency."""
    competency: str  # Architecture spec uses 'competency' name directly
    score: int
    comments: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class EvaluationFullResponse(BaseModel):
    """Complete schema with details according to architecture."""
    id: UUID
    employee_id: UUID
    evaluator_id: UUID
    cycle_id: UUID
    evaluator_relationship: str
    answers: List[EvaluationDetailResponse]
    general_feedback: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    model_config = ConfigDict(from_attributes=True)
