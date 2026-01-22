"""
Schemas para Assessment (Skills Assessment).
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class SkillsAssessmentResponse(BaseModel):
    """Schema para la respuesta de skills assessment según arquitectura."""
    assessment_id: UUID
    user_id: UUID
    ai_profile: Optional[Dict[str, Any]] = None
    # Estructura esperada del ai_profile:
    # {
    #   "strengths": [{skill, proficiency_level, score, evidence}],
    #   "growth_areas": [{skill, current_level, target_level, gap_score, priority}],
    #   "hidden_talents": [{skill, evidence, potential_score}],
    #   "readiness_for_roles": [{role, readiness_percentage, missing_competencies}]
    # }
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_assessment(cls, assessment):
        """Crear desde modelo Assessment."""
        return cls(
            assessment_id=assessment.id,
            user_id=assessment.user_id,
            ai_profile=assessment.ai_profile,
            timestamp=assessment.created_at
        )
