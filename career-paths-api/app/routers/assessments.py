"""
Router para operaciones de skills assessments (análisis de habilidades con IA).
Endpoint: /skills-assessments según arquitectura
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
    prefix="/skills-assessments",
    tags=["skills-assessments"]
)


async def trigger_ai_processing(user_id: UUID, cycle_id: UUID, db: Session):
    """
    Función helper para disparar el procesamiento de IA.
    Recopila todas las evaluaciones del ciclo y llama al servicio de IA.
    """
    try:
        # Verificar si ya existe un assessment para este usuario/ciclo
        existing_assessment = db.query(Assessment).filter(
            and_(
                Assessment.user_id == user_id,
                Assessment.cycle_id == cycle_id
            )
        ).first()
        
        if existing_assessment and existing_assessment.processing_status == ProcessingStatus.COMPLETED:
            # Ya se procesó, no hacer nada
            return
        
        if not existing_assessment:
            # Crear nuevo assessment
            assessment = Assessment(
                user_id=user_id,
                cycle_id=cycle_id,
                processing_status=ProcessingStatus.PENDING
            )
            db.add(assessment)
            db.flush()
        else:
            assessment = existing_assessment
        
        # Actualizar estado a PROCESSING
        assessment.processing_status = ProcessingStatus.PROCESSING
        assessment.processing_started_at = datetime.utcnow()
        db.commit()
        
        # Recopilar todas las evaluaciones del ciclo para este usuario
        evaluations = db.query(Evaluation).filter(
            and_(
                Evaluation.evaluatee_id == user_id,
                Evaluation.cycle_id == cycle_id
            )
        ).all()
        
        if not evaluations:
            raise Exception("No evaluations found for this user/cycle")
        
        # Preparar datos para la IA (formato simplificado)
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
        
        # Llamar al servicio de IA
        ai_result = await ai_service.analyze_skills(evaluation_data)
        
        # Actualizar el assessment con los resultados
        assessment.ai_profile = ai_result
        assessment.processing_status = ProcessingStatus.COMPLETED
        assessment.processing_completed_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        # En caso de error, actualizar el assessment
        if 'assessment' in locals():
            assessment.processing_status = ProcessingStatus.FAILED
            assessment.error_message = str(e)
            assessment.processing_completed_at = datetime.utcnow()
            db.commit()


@router.get("/{user_id}", 
            response_model=SkillsAssessmentResponse,
            summary="Get skills assessment for a user",
            responses={
                404: {"description": "Employee not found or no assessments processed yet"}
            })
async def get_skills_assessment(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene el assessment de habilidades más reciente de un usuario.
    
    - **user_id**: ID del usuario
    
    Retorna el perfil de habilidades generado por IA con:
    - strengths: Fortalezas identificadas
    - growth_areas: Áreas de mejora
    - hidden_talents: Talentos ocultos
    - readiness_for_roles: Preparación para diferentes roles
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {user_id} not found."
        )
    
    # Obtener el assessment más reciente completado
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
