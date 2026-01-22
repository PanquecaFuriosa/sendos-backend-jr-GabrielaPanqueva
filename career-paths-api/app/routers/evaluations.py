"""
Router for 360° evaluation operations.
According to architecture defined in ARCHITECTURE.md
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


async def check_cycle_completion_and_trigger_ai(employee_id: UUID, cycle_id: UUID, db: Session):
    """
    Checks if all cycle evaluations are completed for a user.
    If complete, triggers AI processing.
    """
    from app.routers.assessments import trigger_ai_processing
    
    # Count required and completed evaluations
    required_types = [
        EvaluatorRelationship.SELF,
        EvaluatorRelationship.MANAGER,
        EvaluatorRelationship.PEER
    ]
    
    completed_types = set()
    evaluations = db.query(Evaluation).filter(
        and_(
            Evaluation.employee_id == employee_id,
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
                 400: {"description": "Invalid relationship for SELF evaluation"},
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
    Creates a new 360° evaluation.
    
    - **evaluator_id**: ID of the user performing the evaluation
    - **employee_id**: ID of the user being evaluated
    - **cycle_id**: ID of the evaluation cycle
    - **evaluator_relationship**: Relationship type (SELF, MANAGER, PEER, DIRECT_REPORT)
    - **answers**: List of answers per competency with scores (1-10)
    - **general_feedback**: General comments (optional)
    
    If the cycle is completed (SELF + MANAGER + PEER), triggers AI processing automatically.
    """
    # Verify the cycle exists
    cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == evaluation.cycle_id).first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation cycle with ID {evaluation.cycle_id} not found."
        )
    
    # Verify evaluator exists
    evaluator = db.query(User).filter(User.id == evaluation.evaluator_id).first()
    if not evaluator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The specified evaluator ({evaluation.evaluator_id}) does not exist."
        )
    
    # Verify employee exists
    employee = db.query(User).filter(User.id == evaluation.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The specified employee ({evaluation.employee_id}) does not exist."
        )
    
    # Validate SELF evaluation: evaluator and employee must be the same person
    if evaluation.evaluator_relationship == "SELF":
        if evaluation.evaluator_id != evaluation.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid relationship. For 'SELF' type evaluations, the employee ID and the evaluator ID must match."
            )
    
    # Verify all competencies exist and build a mapping name -> id
    competency_mapping = {}
    for answer in evaluation.answers:
        competency = db.query(Competency).filter(Competency.name == answer.competency).first()
        if not competency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competency '{answer.competency}' not found."
            )
        competency_mapping[answer.competency] = competency.id
    
    try:
        # Create the evaluation
        db_evaluation = Evaluation(
            evaluator_id=evaluation.evaluator_id,
            employee_id=evaluation.employee_id,
            cycle_id=evaluation.cycle_id,
            evaluator_relationship=EvaluatorRelationship(evaluation.evaluator_relationship),
            general_feedback=evaluation.general_feedback,
            status=EvaluationStatus.SUBMITTED
        )
        
        db.add(db_evaluation)
        db.flush()  # Para obtener el ID
        
        # Create evaluation details - map competency name to ID
        for answer in evaluation.answers:
            detail = EvaluationDetail(
                evaluation_id=db_evaluation.id,
                competency_id=competency_mapping[answer.competency],  # Use mapped ID
                score=answer.score,
                comments=answer.comments
            )
            db.add(detail)
        
        db.commit()
        db.refresh(db_evaluation)
        
        # Check if cycle is complete and trigger AI in background
        background_tasks.add_task(
            check_cycle_completion_and_trigger_ai,
            evaluation.employee_id,
            evaluation.cycle_id,
            db
        )
        
        # Return response according to architecture spec
        return EvaluationResponse(
            id=db_evaluation.id,
            employee_id=db_evaluation.employee_id,
            status=db_evaluation.status.value,
            created_at=db_evaluation.created_at
        )
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate evaluation. A record already exists for this employee-evaluator pair in the current cycle."
        )


@router.get("/{evaluation_id}", 
            response_model=EvaluationFullResponse,
            summary="Get evaluation by ID",
            responses={
                403: {"description": "You do not have permission to view this career plan."},
                404: {"description": "Evaluation not found"},
                422: {"description": "Invalid UUID"}
            })
async def get_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Gets an evaluation by its ID with all its details.
    
    - **evaluation_id**: ID of the evaluation to query
    """
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID {evaluation_id} not found."
        )
    
    # Build answers list according to architecture spec
    answers_response = []
    for detail in evaluation.details:
        answers_response.append(EvaluationDetailResponse(
            competency=detail.competency.name if detail.competency else "Unknown",
            score=detail.score,
            comments=detail.comments
        ))
    
    # Build response according to architecture spec
    response = EvaluationFullResponse(
        id=evaluation.id,
        employee_id=evaluation.employee_id,
        evaluator_id=evaluation.evaluator_id,
        cycle_id=evaluation.cycle_id,
        evaluator_relationship=evaluation.evaluator_relationship.value,
        answers=answers_response,
        general_feedback=evaluation.general_feedback,
        status=evaluation.status.value,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at
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
             status_code=status.HTTP_202_ACCEPTED,
             summary="Trigger AI processing for an evaluation",
             responses={
                 202: {"description": "Processing started"},
                 403: {"description": "You do not have permission to modify this evaluation."},
                 404: {"description": "Evaluation not found"},
                 409: {"description": "The evaluation is already being processed"},
                 422: {"description": "Invalid UUID"}
             })
async def process_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Triggers AI processing manually for an evaluation.
    Normally this is done automatically when the cycle is completed.
    
    - **evaluation_id**: ID of the evaluation to process
    
    Returns 202 Accepted according to architecture specification.
    """
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID {evaluation_id} not found."
        )
    
    # Check if already processing
    from app.models.assessment import Assessment, ProcessingStatus
    existing_assessment = db.query(Assessment).filter(
        and_(
            Assessment.user_id == evaluation.employee_id,
            Assessment.cycle_id == evaluation.cycle_id,
            Assessment.processing_status == ProcessingStatus.PROCESSING
        )
    ).first()
    
    if existing_assessment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The evaluation is already being processed."
        )
    
    # Process directly (without background task to avoid session issues)
    from app.routers.assessments import trigger_ai_processing
    
    try:
        await trigger_ai_processing(
            evaluation.employee_id,
            evaluation.cycle_id,
            db
        )
        
        # Return 202 response according to architecture spec
        return {
            "message": "Processing started",
            "task_id": str(evaluation.id),  # Using evaluation_id as task_id
            "status": "PROCESSING"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing evaluation: {str(e)}"
        )
