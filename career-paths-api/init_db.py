"""
Script to initialize the database with sample data.
Includes: Users, EvaluationCycles, Competencies, Evaluations with details.

Note: Database tables are created via Alembic migrations.
Run 'alembic upgrade head' before executing this script.
"""
from app.database import SessionLocal
from app.models.user import User
from app.models.evaluation_cycle import EvaluationCycle, CycleStatus
from app.models.competency import Competency
from app.models.evaluation import Evaluation, EvaluatorRelationship, EvaluationStatus
from app.models.evaluation_detail import EvaluationDetail
from datetime import datetime, timedelta
import uuid


def init_db():
    """Initialize the database with complete sample data."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"La base de datos ya tiene {existing_users} usuarios. No se crearon más.")
            return
        
        print("Inicializando base de datos...")
        
        # 1. Create sample users
        users_data = [
            {
                "email": "maria.garcia@sendos.com",
                "full_name": "María García",
                "current_position": "Analista Senior",
                "department": "Operaciones",
                "years_experience": "5"
            },
            {
                "email": "carlos.lopez@sendos.com",
                "full_name": "Carlos López",
                "current_position": "Gerente de Área",
                "department": "Ventas",
                "years_experience": "8"
            },
            {
                "email": "ana.martinez@sendos.com",
                "full_name": "Ana Martínez",
                "current_position": "Coordinadora",
                "department": "Marketing",
                "years_experience": "3"
            },
            {
                "email": "pedro.sanchez@sendos.com",
                "full_name": "Pedro Sánchez",
                "current_position": "Director Regional",
                "department": "Operaciones",
                "years_experience": "12"
            },
            {
                "email": "laura.fernandez@sendos.com",
                "full_name": "Laura Fernández",
                "current_position": "Analista",
                "department": "Operaciones",
                "years_experience": "2"
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
            users.append(user)
        
        db.flush()
        print(f"Usuarios creados: {len(users)}")
        
        # 2. Create evaluation cycle
        cycle = EvaluationCycle(
            name="Q1 2026",
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 3, 31),
            status=CycleStatus.ACTIVE
        )
        db.add(cycle)
        db.flush()
        print(f"Ciclo de evaluación creado: {cycle.name}")
        
        # 3. Create competencies catalog
        competencies_data = [
            {"name": "Liderazgo", "description": "Capacidad de dirigir y motivar equipos"},
            {"name": "Comunicación", "description": "Habilidad para transmitir ideas claramente"},
            {"name": "Trabajo en Equipo", "description": "Colaboración efectiva con otros"},
            {"name": "Resolución de Problemas", "description": "Capacidad analítica y solución creativa"},
            {"name": "Adaptabilidad", "description": "Flexibilidad ante cambios"},
            {"name": "Pensamiento Estratégico", "description": "Visión a largo plazo y planificación"},
            {"name": "Innovación", "description": "Creatividad y propuesta de mejoras"},
            {"name": "Orientación a Resultados", "description": "Enfoque en logro de objetivos"},
            {"name": "Desarrollo de Personas", "description": "Mentoría y formación de equipos"},
            {"name": "Gestión de Proyectos", "description": "Planificación y ejecución de iniciativas"}
        ]
        
        competencies = []
        for comp_data in competencies_data:
            comp = Competency(**comp_data)
            db.add(comp)
            competencies.append(comp)
        
        db.flush()
        print(f"Catálogo de {len(competencies)} competencias creado")
        
        # 4. Create sample evaluations for María García
        # Assuming: María (0), Carlos (1), Ana (2), Pedro (3), Laura (4)
        
        # María's self-evaluation
        eval_self = Evaluation(
            evaluator_id=users[0].id,
            evaluatee_id=users[0].id,
            cycle_id=cycle.id,
            evaluator_relationship=EvaluatorRelationship.SELF,
            status=EvaluationStatus.SUBMITTED
        )
        db.add(eval_self)
        db.flush()
        
        # Self-evaluation details (moderate scores)
        self_scores = [7, 6, 8, 7, 7, 5, 6, 8, 5, 6]
        for i, comp in enumerate(competencies):
            detail = EvaluationDetail(
                evaluation_id=eval_self.id,
                competency_id=comp.id,
                score=self_scores[i],
                comments=f"Auto-evaluación en {comp.name}"
            )
            db.add(detail)
        
        # Carlos's (Manager) evaluation of María
        eval_manager = Evaluation(
            evaluator_id=users[1].id,
            evaluatee_id=users[0].id,
            cycle_id=cycle.id,
            evaluator_relationship=EvaluatorRelationship.MANAGER,
            status=EvaluationStatus.SUBMITTED
        )
        db.add(eval_manager)
        db.flush()
        
        # Manager's details (sees more strengths)
        manager_scores = [8, 8, 9, 8, 7, 6, 7, 9, 6, 8]
        for i, comp in enumerate(competencies):
            detail = EvaluationDetail(
                evaluation_id=eval_manager.id,
                competency_id=comp.id,
                score=manager_scores[i],
                comments=f"Evaluación de manager: {comp.name} - buen desempeño"
            )
            db.add(detail)
        
        # Ana's (Peer) evaluation of María
        eval_peer = Evaluation(
            evaluator_id=users[2].id,
            evaluatee_id=users[0].id,
            cycle_id=cycle.id,
            evaluator_relationship=EvaluatorRelationship.PEER,
            status=EvaluationStatus.SUBMITTED
        )
        db.add(eval_peer)
        db.flush()
        
        # Peer details (balanced scores)
        peer_scores = [8, 9, 9, 7, 8, 6, 7, 8, 7, 7]
        for i, comp in enumerate(competencies):
            detail = EvaluationDetail(
                evaluation_id=eval_peer.id,
                competency_id=comp.id,
                score=peer_scores[i],
                comments=f"Evaluación de compañero: excelente en {comp.name}"
            )
            db.add(detail)
        
        db.commit()
        print(f"Evaluaciones 360° creadas para {users[0].full_name}")
        print("   - Auto-evaluación (SELF)")
        print("   - Evaluación de manager (MANAGER)")
        print("   - Evaluación de peer (PEER)")
        
        # Show summary
        print("\nResumen de datos creados:")
        print(f"   Usuarios: {len(users)}")
        print(f"   Ciclos: 1 ({cycle.name})")
        print(f"   Competencias: {len(competencies)}")
        print(f"   Evaluaciones: 3 (SELF + MANAGER + PEER)")
        print(f"   Detalles: {len(competencies) * 3}")
        
        print("\nUsuarios creados:")
        for user in users:
            print(f"   - {user.full_name} ({user.email})")
            print(f"     ID: {user.id}")
            print(f"     Posición: {user.current_position} - {user.department}")
        
        print(f"\nCiclo activo: {cycle.name} (ID: {cycle.id})")
        print(f"   Período: {cycle.start_date.date()} a {cycle.end_date.date()}")
        
        print("\nSiguiente paso:")
        print("   El ciclo está COMPLETO (SELF + MANAGER + PEER) para María García.")
        print("   Al crear la evaluación, se detectará automáticamente y se")
        print("   generará el assessment de IA. Luego se pueden generar career paths.")
        
        print("\nBase de datos inicializada correctamente!")
            
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
