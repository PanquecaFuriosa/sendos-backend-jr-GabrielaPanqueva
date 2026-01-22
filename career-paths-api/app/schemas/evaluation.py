"""
Schemas para Evaluation (360° Evaluation).
"""
from pydantic import BaseModel, Field, ConfigDict, validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class EvaluationAnswerCreate(BaseModel):
    """Schema para una respuesta en la evaluación."""
    competency_id: UUID
    score: int = Field(..., ge=1, le=10, description="Score must be between 1 and 10")
    comments: Optional[str] = None


class EvaluationCreate(BaseModel):
    """Schema para crear una nueva evaluación."""
    evaluator_id: UUID
    evaluatee_id: UUID
    cycle_id: UUID
    evaluator_relationship: str = Field(..., description="SELF, MANAGER, PEER, or DIRECT_REPORT")
    answers: List[EvaluationAnswerCreate]
    general_feedback: Optional[str] = None
    
    @validator('evaluator_relationship')
    def validate_relationship(cls, v):
        """Validar que el tipo de relación sea válido."""
        valid_types = ["SELF", "MANAGER", "PEER", "DIRECT_REPORT"]
        if v not in valid_types:
            raise ValueError(f'evaluator_relationship must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('answers')
    def validate_answers(cls, v):
        """Validar que haya al menos una respuesta."""
        if not v or len(v) == 0:
            raise ValueError('At least one answer is required')
        return v
    
    @validator('evaluatee_id')
    def validate_self_evaluation(cls, evaluatee_id, values):
        """Para evaluaciones SELF, evaluator_id y evaluatee_id deben coincidir."""
        if 'evaluator_id' in values and 'evaluator_relationship' in values:
            if values['evaluator_relationship'] == 'SELF':
                if evaluatee_id != values['evaluator_id']:
                    raise ValueError("For 'SELF' type evaluations, the employee ID and the evaluator ID must match.")
        return evaluatee_id


class EvaluationResponse(BaseModel):
    """Schema para la respuesta de evaluación."""
    id: UUID
    evaluator_id: UUID
    evaluatee_id: UUID
    cycle_id: UUID
    evaluator_relationship: str
    general_feedback: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EvaluationDetailResponse(BaseModel):
    """Schema para detalle de evaluación con competencia."""
    competency_id: UUID
    competency_name: Optional[str] = None
    score: int
    comments: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class EvaluationFullResponse(EvaluationResponse):
    """Schema completo con detalles."""
    details: List[EvaluationDetailResponse] = []
