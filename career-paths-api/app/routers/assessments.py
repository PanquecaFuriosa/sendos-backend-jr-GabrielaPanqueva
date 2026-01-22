"""
Router for skills assessments operations (AI skills analysis).
Endpoint: /skills-assessments according to architecture
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.assessment import Assessment, ProcessingStatus
from app.models.user import User
from app.models.evaluation import Evaluation, EvaluatorRelationship
from app.models.evaluation_cycle import EvaluationCycle
from app.schemas.assessment import SkillsAssessmentResponse
from app.services.ai_integration import ai_service

router = APIRouter(
    tags=["skills-assessments"]
)


async def trigger_ai_processing(user_id: UUID, cycle_id: UUID, db: Session):
    """
    Helper function to trigger AI processing.
    Collects all cycle evaluations and calls the AI service.
    """
    try:
        # Check if an assessment already exists for this user/cycle
        existing_assessment = db.query(Assessment).filter(
            and_(
                Assessment.user_id == user_id,
                Assessment.cycle_id == cycle_id
            )
        ).first()
        
        if existing_assessment and existing_assessment.processing_status == ProcessingStatus.COMPLETED:
            # Already processed, do nothing
            return
        
        if not existing_assessment:
            # Create new assessment
            assessment = Assessment(
                user_id=user_id,
                cycle_id=cycle_id,
                processing_status=ProcessingStatus.PENDING
            )
            db.add(assessment)
            db.flush()
        else:
            assessment = existing_assessment
        
        # Update status to PROCESSING
        assessment.processing_status = ProcessingStatus.PROCESSING
        assessment.processing_started_at = datetime.utcnow()
        db.commit()
        
        # Collect all cycle evaluations for this user
        evaluations = db.query(Evaluation).filter(
            and_(
                Evaluation.employee_id == user_id,
                Evaluation.cycle_id == cycle_id
            )
        ).all()
        
        if not evaluations:
            raise Exception("No evaluations found for this user/cycle")
        
        # Prepare data for AI (simplified format)
        evaluation_data = {
            "user_id": str(user_id),
            "cycle_id": str(cycle_id),
            "evaluations": []
        }
        
        for eval in evaluations:
            eval_dict = {
                "relationship": eval.evaluator_relationship.value,
                "competencies": []
            }
            for detail in eval.details:
                eval_dict["competencies"].append({
                    "name": detail.competency.name if detail.competency else "Unknown",
                    "score": detail.score,
                    "comments": detail.comments
                })
            evaluation_data["evaluations"].append(eval_dict)
        
        # Call AI service
        ai_result = await ai_service.analyze_skills(evaluation_data)
        
        # Update assessment with results
        assessment.ai_profile = ai_result
        assessment.processing_status = ProcessingStatus.COMPLETED
        assessment.processing_completed_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        # In case of error, update the assessment
        if 'assessment' in locals():
            assessment.processing_status = ProcessingStatus.FAILED
            assessment.error_message = str(e)
            assessment.processing_completed_at = datetime.utcnow()
            db.commit()


@router.get("/{user_id}", 
            response_model=SkillsAssessmentResponse,
            summary="Get skills assessment for a user",
            responses={
                403: {"description": "You do not have permission to view these skill assessments."},
                404: {"description": "Employee not found or no assessments processed yet"}
            })
async def get_skills_assessment(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Gets the most recent skills assessment for a user.
    
    - **user_id**: User ID
    
    Returns the AI-generated skills profile with:
    - strengths: Identified strengths
    - growth_areas: Areas for improvement
    - hidden_talents: Hidden talents
    - readiness_for_roles: Readiness for different roles
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {user_id} not found."
        )
    
    # Get the most recent completed assessment
    assessment = db.query(Assessment).filter(
        and_(
            Assessment.user_id == user_id,
            Assessment.processing_status == ProcessingStatus.COMPLETED
        )
    ).order_by(Assessment.created_at.desc()).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No skills assessments have been processed for this employee yet."
        )
    
    return SkillsAssessmentResponse.from_assessment(assessment)
