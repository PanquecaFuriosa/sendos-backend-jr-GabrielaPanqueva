"""
Tests para la Career Paths API.
Cubre: Evaluations, Assessments, Career Paths.
"""
import pytest
from uuid import uuid4, UUID
from datetime import datetime


class TestEvaluations:
    """Tests para el endpoint /evaluations."""
    
    def test_create_evaluation_missing_cycle(self, client):
        """No se puede crear evaluación con ciclo inexistente."""
        payload = {
            "evaluator_id": str(uuid4()),
            "evaluatee_id": str(uuid4()),
            "cycle_id": str(uuid4()),
            "relationship": "PEER",
            "answers": [
                {
                    "competency_id": str(uuid4()),
                    "score": 8,
                    "comments": "Excelente desempeño"
                }
            ]
        }
        
        response = client.post("/api/v1/evaluations", json=payload)
        assert response.status_code == 404
        assert "cycle" in response.json()["detail"].lower()
    
    def test_create_self_evaluation_mismatched_ids(self, client):
        """SELF evaluation debe tener evaluator_id == evaluatee_id."""
        payload = {
            "evaluator_id": str(uuid4()),
            "evaluatee_id": str(uuid4()),  # Diferente ID
            "cycle_id": str(uuid4()),
            "relationship": "SELF",
            "answers": [
                {
                    "competency_id": str(uuid4()),
                    "score": 7,
                    "comments": "Auto-evaluación"
                }
            ]
        }
        
        response = client.post("/api/v1/evaluations", json=payload)
        assert response.status_code == 400
        assert "SELF" in response.json()["detail"]
    
    def test_create_evaluation_invalid_score(self, client):
        """Score debe estar entre 1 y 10."""
        payload = {
            "evaluator_id": str(uuid4()),
            "evaluatee_id": str(uuid4()),
            "cycle_id": str(uuid4()),
            "relationship": "PEER",
            "answers": [
                {
                    "competency_id": str(uuid4()),
                    "score": 11,  # Inválido
                    "comments": "Test"
                }
            ]
        }
        
        response = client.post("/api/v1/evaluations", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_create_evaluation_invalid_relationship(self, client):
        """Relationship debe ser uno de los valores del enum."""
        payload = {
            "evaluator_id": str(uuid4()),
            "evaluatee_id": str(uuid4()),
            "cycle_id": str(uuid4()),
            "relationship": "FRIEND",  # Inválido
            "answers": []
        }
        
        response = client.post("/api/v1/evaluations", json=payload)
        assert response.status_code == 422


class TestAssessments:
    """Tests para el endpoint /skills-assessments."""
    
    def test_get_assessment_nonexistent_user(self, client):
        """No se puede obtener assessment de usuario inexistente."""
        fake_user_id = str(uuid4())
        response = client.get(f"/api/v1/skills-assessments/{fake_user_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_process_evaluation_nonexistent(self, client):
        """No se puede procesar evaluación inexistente."""
        fake_eval_id = str(uuid4())
        response = client.post(f"/api/v1/evaluations/{fake_eval_id}/process")
        assert response.status_code == 404


class TestCareerPaths:
    """Tests para los endpoints /career-paths."""
    
    def test_get_career_paths_nonexistent_user(self, client):
        """Usuario inexistente debe retornar 404."""
        fake_user_id = str(uuid4())
        response = client.get(f"/api/v1/career-paths/{fake_user_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_career_path_steps_nonexistent(self, client):
        """Path inexistente debe retornar 404."""
        fake_path_id = str(uuid4())
        response = client.get(f"/api/v1/career-paths/{fake_path_id}/steps")
        assert response.status_code == 404
    
    def test_accept_career_path_nonexistent(self, client):
        """No se puede aceptar path inexistente."""
        fake_path_id = str(uuid4())
        response = client.post(f"/api/v1/career-paths/{fake_path_id}/accept")
        assert response.status_code == 404


class TestIntegration:
    """Tests de integración del flujo completo (requieren DB)."""
    
    @pytest.mark.skip(reason="Requiere DB inicializada con datos")
    def test_full_workflow(self, client, db_session):
        """
        Test del flujo completo:
        1. Crear ciclo
        2. Crear evaluaciones (SELF + MANAGER + PEER)
        3. Verificar que se genera assessment automáticamente
        4. Obtener career paths
        5. Aceptar un path
        """
        # Este test requeriría fixtures de DB con datos reales
        pass
    
    @pytest.mark.skip(reason="Requiere DB inicializada")
    def test_duplicate_evaluation(self, client, db_session):
        """
        Test de constraint: No se puede crear evaluación duplicada
        (mismo evaluator, evaluatee, cycle).
        """
        # Debería retornar 409 Conflict
        pass
    
    @pytest.mark.skip(reason="Requiere DB inicializada")
    def test_cycle_completion_triggers_ai(self, client, db_session):
        """
        Test: Al completar ciclo (SELF + MANAGER + PEER),
        se debe crear assessment automáticamente.
        """
        pass
