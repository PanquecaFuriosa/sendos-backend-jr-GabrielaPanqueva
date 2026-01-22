"""
Schemas for Assessment (Skills Assessment).
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class SkillsAssessmentResponse(BaseModel):
    """Schema for skills assessment response according to architecture."""
    assessment_id: UUID
    user_id: UUID
    cycle_id: UUID
    ai_profile: Optional[Dict[str, Any]] = None
    # Expected structure of ai_profile:
    # {
    #   "strengths": [{skill, proficiency_level, score, evidence}],
    #   "growth_areas": [{skill, current_level, target_level, gap_score, priority}],
    #   "hidden_talents": [{skill, evidence, potential_score}],
    #   "readiness_for_roles": [{role, readiness_percentage, missing_competencies}]
    # }
    processing_status: str
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_assessment(cls, assessment):
        """Create from Assessment model."""
        return cls(
            assessment_id=assessment.id,
            user_id=assessment.user_id,
            cycle_id=assessment.cycle_id,
            ai_profile=assessment.ai_profile,
            processing_status=assessment.processing_status.value,
            timestamp=assessment.created_at
        )
