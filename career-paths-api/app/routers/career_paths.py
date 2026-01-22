"""
Router para operaciones de senderos de carrera (career paths).
Endpoints: /career-paths según arquitectura
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.career_path import CareerPath, CareerPathStatus
from app.models.career_path_step import CareerPathStep
from app.models.development_action import DevelopmentAction
from app.models.user import User
from app.models.assessment import Assessment, ProcessingStatus
from app.schemas.career_path import (
    CareerPathsListResponse,
    CareerPathSummaryResponse,
    CareerPathStepsResponse,
    CareerPathStepDetail,
    CareerPathAcceptResponse
)
from app.services.ai_integration import ai_service

router = APIRouter(
    tags=["career-paths"]
)


async def generate_career_paths_task(user_id: UUID, db: Session):
    """
    Genera senderos de carrera en segundo plano usando el servicio de IA.
    """
    try:
        # Obtener el usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        
        # Obtener el assessment más reciente completado
        latest_assessment = db.query(Assessment).filter(
            and_(
                Assessment.user_id == user_id,
                Assessment.processing_status == ProcessingStatus.COMPLETED
            )
        ).order_by(Assessment.created_at.desc()).first()
        
        if not latest_assessment or not latest_assessment.ai_profile:
            raise Exception("No completed assessment found for user")
        
        # Preparar el perfil del usuario
        user_profile = {
            "user_id": str(user_id),
            "email": user.email,
            "full_name": user.full_name,
            "current_position": user.current_position,
            "department": user.department,
            "years_experience": user.years_experience
        }
        
        # Llamar al servicio de IA para generar senderos
        career_data = await ai_service.generate_career_paths(
            user_profile=user_profile,
            ai_profile=latest_assessment.ai_profile
        )
        
        # Archivar senderos anteriores
        db.query(CareerPath).filter(
            and_(
                CareerPath.user_id == user_id,
                CareerPath.status == CareerPathStatus.GENERATED
            )
        ).update({"status": CareerPathStatus.ARCHIVED})
        
        # Crear los nuevos senderos
        paths_data = career_data.get("generated_paths", [])
        for path_data in paths_data:
            career_path = CareerPath(
                user_id=user_id,
                path_name=path_data.get("path_name"),
                recommended=path_data.get("recommended", False),
                total_duration_months=path_data.get("total_duration_months", 12),
                feasibility_score=path_data.get("feasibility_score"),
                status=CareerPathStatus.GENERATED
            )
            db.add(career_path)
            db.flush()
            
            # Crear los pasos del sendero
            steps_data = path_data.get("steps", [])
            for step_data in steps_data:
                step = CareerPathStep(
                    career_path_id=career_path.id,
                    step_order=step_data.get("step_number"),
                    title=step_data.get("title", ""),
                    target_role=step_data.get("target_role"),
                    duration_months=step_data.get("duration_months"),
                    required_competencies=step_data.get("required_competencies")
                )
                db.add(step)
                db.flush()
                
                # Crear acciones de desarrollo
                actions_data = step_data.get("development_actions", [])
                for action_data in actions_data:
                    if isinstance(action_data, dict):
                        action = DevelopmentAction(
                            step_id=step.id,
                            type=action_data.get("type", "training"),
                            description=action_data.get("description", "")
                        )
                        db.add(action)
                    elif isinstance(action_data, str):
                        # Si es string, crear acción genérica
                        action = DevelopmentAction(
                            step_id=step.id,
                            type="training",
                            description=action_data
                        )
                        db.add(action)
        
        db.commit()
        
    except Exception as e:
        print(f"Error generating career paths: {e}")
        db.rollback()


@router.get("/{user_id}",
            response_model=CareerPathsListResponse,
            summary="Get career paths for a user",
            responses={
                404: {"description": "User not found or no paths created yet"},
                202: {"description": "Career path generation started"}
            })
async def get_career_paths(
    user_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Obtiene los senderos de carrera de un usuario.
    Si no existen, los genera automáticamente en segundo plano.
    
    - **user_id**: ID del usuario
    
    Retorna lista de senderos generados con información resumida.
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {user_id} not found."
        )
    
    # Buscar senderos generados del usuario
    career_paths = db.query(CareerPath).filter(
        and_(
            CareerPath.user_id == user_id,
            CareerPath.status != CareerPathStatus.ARCHIVED
        )
    ).order_by(CareerPath.generated_at.desc()).all()
    
    if not career_paths:
        # No existen, verificar si hay assessment completado
        latest_assessment = db.query(Assessment).filter(
            and_(
                Assessment.user_id == user_id,
                Assessment.processing_status == ProcessingStatus.COMPLETED
            )
        ).first()
        
        if not latest_assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No completed assessment found for user {user_id}. Please complete evaluations first."
            )
        
        # Generar senderos en segundo plano
        background_tasks.add_task(generate_career_paths_task, user_id, db)
        
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Career path generation started. Please check again in a few moments."
        )
    
    # Construir respuesta
    paths_summaries = [CareerPathSummaryResponse.from_career_path(path) for path in career_paths]
    
    return CareerPathsListResponse(
        career_path_id=career_paths[0].id if career_paths else None,
        user_id=user_id,
        generated_paths=paths_summaries,
        timestamp=career_paths[0].generated_at if career_paths else datetime.utcnow()
    )


@router.get("/{path_id}/steps",
            response_model=CareerPathStepsResponse,
            summary="Get detailed steps for a career path",
            responses={
                404: {"description": "Path not found"}
            })
async def get_career_path_steps(
    path_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene los pasos detallados de un sendero específico.
    
    - **path_id**: ID del sendero
    
    Retorna los pasos con competencias requeridas y acciones de desarrollo.
    """
    career_path = db.query(CareerPath).filter(CareerPath.id == path_id).first()
    
    if not career_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Path with ID {path_id} not found."
        )
    
    # Construir respuesta con pasos
    steps_response = []
    for step in career_path.steps:
        step_detail = CareerPathStepDetail(
            step_number=step.step_order,
            target_role=step.target_role,
            duration_months=step.duration_months,
            required_competencies=step.required_competencies or []
        )
        steps_response.append(step_detail)
    
    return CareerPathStepsResponse(
        path_id=career_path.id,
        path_name=career_path.path_name,
        steps=steps_response
    )


@router.post("/{path_id}/accept",
             response_model=CareerPathAcceptResponse,
             summary="Accept a career path",
             responses={
                 404: {"description": "Path not found"},
                 409: {"description": "This career plan is already underway"}
             })
async def accept_career_path(
    path_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Marca un sendero de carrera como aceptado por el usuario.
    Cambia el estado a IN_PROGRESS.
    
    - **path_id**: ID del sendero a aceptar
    """
    career_path = db.query(CareerPath).filter(CareerPath.id == path_id).first()
    
    if not career_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Path with ID {path_id} not found."
        )
    
    if career_path.status == CareerPathStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This career plan is already underway."
        )
    
    # Actualizar estado
    career_path.status = CareerPathStatus.IN_PROGRESS
    career_path.started_at = datetime.utcnow()
    db.commit()
    
    return CareerPathAcceptResponse(
        path_id=career_path.id,
        user_id=career_path.user_id,
        status=career_path.status.value,
        started_at=career_path.started_at
    )
