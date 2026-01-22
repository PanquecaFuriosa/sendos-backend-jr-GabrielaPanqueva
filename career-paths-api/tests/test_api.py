"""
Tests for the Career Paths API.
Covers: Evaluations, Assessments, Career Paths.
"""
import pytest
from uuid import uuid4, UUID
from datetime import datetime


class TestEvaluations:
    """Tests for the /evaluations endpoint."""
    
    def test_create_evaluation_missing_cycle(self, client):
        """Cannot create evaluation with non-existent cycle."""
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
        """SELF evaluation must have evaluator_id == evaluatee_id."""
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
        """Score must be between 1 and 10."""
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
        """Relationship must be one of the enum values."""
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
    """Tests for the /skills-assessments endpoint."""
    
    def test_get_assessment_nonexistent_user(self, client):
        """Cannot get assessment for non-existent user."""
        fake_user_id = str(uuid4())
        response = client.get(f"/api/v1/skills-assessments/{fake_user_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_process_evaluation_nonexistent(self, client):
        """Cannot process non-existent evaluation."""
        fake_eval_id = str(uuid4())
        response = client.post(f"/api/v1/evaluations/{fake_eval_id}/process")
        assert response.status_code == 404


class TestCareerPaths:
    """Tests for the /career-paths endpoints."""
    
    def test_get_career_paths_nonexistent_user(self, client):
        """Non-existent user should return 404."""
        fake_user_id = str(uuid4())
        response = client.get(f"/api/v1/career-paths/{fake_user_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_career_path_steps_nonexistent(self, client):
        """Non-existent path should return 404."""
        fake_path_id = str(uuid4())
        response = client.get(f"/api/v1/career-paths/{fake_path_id}/steps")
        assert response.status_code == 404
    
    def test_accept_career_path_nonexistent(self, client):
        """Cannot accept non-existent path."""
        fake_path_id = str(uuid4())
        response = client.post(f"/api/v1/career-paths/{fake_path_id}/accept")
        assert response.status_code == 404


class TestIntegration:
    """Integration tests for complete flow (require DB)."""
    
    @pytest.mark.skip(reason="Requiere DB inicializada con datos")
    def test_full_workflow(self, client, db_session):
        """
        Test complete workflow:
        1. Create cycle
        2. Create evaluations (SELF + MANAGER + PEER)
        3. Verify assessment is automatically generated
        4. Get career paths
        5. Accept a path
        """
        # This test would require DB fixtures with real data
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
