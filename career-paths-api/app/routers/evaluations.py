"""
Router para operaciones de evaluaciones 360°.
Según arquitectura definida en ARCHITECTURE.md
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.evaluation import Evaluation, EvaluationStatus, EvaluatorRelationship
from app.models.evaluation_detail import EvaluationDetail
from app.models.evaluation_cycle import EvaluationCycle
from app.models.user import User
from app.models.competency import Competency
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse, EvaluationFullResponse, EvaluationDetailResponse

router = APIRouter(
    tags=["evaluations"]
)


async def check_cycle_completion_and_trigger_ai(evaluatee_id: UUID, cycle_id: UUID, db: Session):
    """
    Verifica si se completaron todas las evaluaciones del ciclo para un usuario.
    Si está completo, dispara el procesamiento de IA.
    """
    from app.routers.assessments import trigger_ai_processing
    
    # Contar evaluaciones requeridas y completadas
    required_types = [
        EvaluatorRelationship.SELF,
        EvaluatorRelationship.MANAGER,
        EvaluatorRelationship.PEER
    ]
    
    completed_types = set()
    evaluations = db.query(Evaluation).filter(
        and_(
            Evaluation.evaluatee_id == evaluatee_id,
            Evaluation.cycle_id == cycle_id
        )
    ).all()
    
    for eval in evaluations:
        completed_types.add(eval.evaluator_relationship)
    
    # Check if it has at least: SELF + MANAGER + 1 PEER
    has_self = EvaluatorRelationship.SELF in completed_types
    has_manager = EvaluatorRelationship.MANAGER in completed_types
    has_peer = EvaluatorRelationship.PEER in completed_types
    
    if has_self and has_manager and has_peer:
        # Ciclo completo, disparar procesamiento
        await trigger_ai_processing(evaluatee_id, cycle_id, db)


@router.post("/", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED,
             summary="Submit a new 360 evaluation",
             responses={
                 404: {"description": "Cycle or User not found"},
                 409: {"description": "Evaluation duplicate constraint violation"},
                 422: {"description": "Validation error"}
             })
async def create_evaluation(
    evaluation: EvaluationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva evaluación 360°.
    
    - **evaluator_id**: ID del usuario que evalúa
    - **evaluatee_id**: ID del usuario evaluado
    - **cycle_id**: ID del ciclo de evaluación
    - **evaluator_relationship**: Tipo de relación (SELF, MANAGER, PEER, DIRECT_REPORT)
    - **answers**: Lista de respuestas por competencia con scores (1-10)
    - **general_feedback**: Comentario general (opcional)
    
    Si se completa el ciclo (SELF + MANAGER + PEER), dispara procesamiento de IA automáticamente.
    """
    # Verify the cycle exists
    cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == evaluation.cycle_id).first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation cycle with ID {evaluation.cycle_id} not found."
        )
    
    # Verify evaluator and evaluatee exist
    evaluator = db.query(User).filter(User.id == evaluation.evaluator_id).first()
    if not evaluator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The specified evaluator ({evaluation.evaluator_id}) does not exist."
        )
    
    evaluatee = db.query(User).filter(User.id == evaluation.evaluatee_id).first()
    if not evaluatee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The specified employee ({evaluation.evaluatee_id}) does not exist."
        )
    
    # Verify all competencies exist
    for answer in evaluation.answers:
        competency = db.query(Competency).filter(Competency.id == answer.competency_id).first()
        if not competency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competency with ID {answer.competency_id} not found."
            )
    
    try:
        # Create the evaluation
        db_evaluation = Evaluation(
            evaluator_id=evaluation.evaluator_id,
            evaluatee_id=evaluation.evaluatee_id,
            cycle_id=evaluation.cycle_id,
            evaluator_relationship=EvaluatorRelationship(evaluation.evaluator_relationship),
            general_feedback=evaluation.general_feedback,
            status=EvaluationStatus.SUBMITTED
        )
        
        db.add(db_evaluation)
        db.flush()  # Para obtener el ID
        
        # Create evaluation details
        for answer in evaluation.answers:
            detail = EvaluationDetail(
                evaluation_id=db_evaluation.id,
                competency_id=answer.competency_id,
                score=answer.score,
                comments=answer.comments
            )
            db.add(detail)
        
        db.commit()
        db.refresh(db_evaluation)
        
        # Check if cycle is complete and trigger AI in background
        background_tasks.add_task(
            check_cycle_completion_and_trigger_ai,
            evaluation.evaluatee_id,
            evaluation.cycle_id,
            db
        )
        
        return db_evaluation
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate evaluation. A record already exists for this employee-evaluator pair in the current cycle."
        )


@router.get("/{evaluation_id}", response_model=EvaluationFullResponse)
async def get_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene una evaluación por su ID con todos sus detalles.
    
    - **evaluation_id**: ID de la evaluación a consultar
    """
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID {evaluation_id} not found."
        )
    
    # Cargar detalles con nombres de competencias
    details_response = []
    for detail in evaluation.details:
        details_response.append(EvaluationDetailResponse(
            competency_id=detail.competency_id,
            competency_name=detail.competency.name if detail.competency else None,
            score=detail.score,
            comments=detail.comments
        ))
    
    # Build response
    response = EvaluationFullResponse(
        id=evaluation.id,
        evaluator_id=evaluation.evaluator_id,
        evaluatee_id=evaluation.evaluatee_id,
        cycle_id=evaluation.cycle_id,
        evaluator_relationship=evaluation.evaluator_relationship.value,
        general_feedback=evaluation.general_feedback,
        status=evaluation.status.value,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at,
        details=details_response
    )
    
    return response


@router.get("/", response_model=List[EvaluationResponse])
async def list_evaluations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lists all evaluations.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    evaluations = db.query(Evaluation).offset(skip).limit(limit).all()
    return evaluations


@router.post("/{evaluation_id}/process", 
             response_model=dict,
             status_code=status.HTTP_202_ACCEPTED,
             summary="Trigger AI processing for an evaluation",
             responses={
                 404: {"description": "Evaluation not found"},
                 409: {"description": "The evaluation is already being processed"}
             })
async def process_evaluation(
    evaluation_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Dispara el procesamiento de IA manualmente para una evaluación.
    Normalmente esto se hace automáticamente cuando se completa el ciclo.
    
    - **evaluation_id**: ID de la evaluación a procesar
    """
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID {evaluation_id} not found."
        )
    
    if evaluation.status == EvaluationStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The evaluation is already being processed."
        )
    
    # Actualizar estado
    evaluation.status = EvaluationStatus.PROCESSING
    db.commit()
    
    # Disparar procesamiento en background
    from app.routers.assessments import trigger_ai_processing
    background_tasks.add_task(
        trigger_ai_processing,
        evaluation.evaluatee_id,
        evaluation.cycle_id,
        db
    )
    
    return {
        "message": "Processing started",
        "task_id": str(evaluation.id),
        "status": "PROCESSING"
    }
