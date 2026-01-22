"""
Servicio de integración con IA para análisis de habilidades y generación de senderos de carrera.
Incluye retry logic con tenacity y manejo robusto de errores.
"""
import httpx
import asyncio
import random
from typing import Dict, Any, List
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from app.config import get_settings

settings = get_settings()


class AIIntegrationService:
    """
    Servicio para integrar con el servicio de IA (mock o real).
    """
    
    def __init__(self):
        self.base_url = settings.AI_SERVICE_BASE_URL
        self.timeout = httpx.Timeout(30.0, connect=5.0)
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def analyze_skills(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Llama al servicio de IA para analizar habilidades basadas en la evaluación 360°.
        Incluye retry automático (máximo 3 intentos con backoff exponencial).
        
        Args:
            evaluation_data: Datos de la evaluación en formato dict
                Expected structure:
                {
                    "user_id": str,
                    "cycle_id": str,
                    "evaluations": [
                        {
                            "evaluator_id": str,
                            "relationship": str (SELF, MANAGER, PEER, DIRECT_REPORT),
                            "competencies": [
                                {
                                    "competency_name": str,
                                    "score": int,
                                    "comments": str
                                }
                            ]
                        }
                    ]
                }
            
        Returns:
            Dict con el perfil de habilidades y preparación para roles
                {
                    "strengths": [str],
                    "growth_areas": [str],
                    "hidden_talents": [str],
                    "readiness_for_roles": [
                        {
                            "role_name": str,
                            "readiness_percentage": int,
                            "reasoning": str
                        }
                    ]
                }
        """
        # Simular latencia (2-5 segundos)
        await asyncio.sleep(random.uniform(2.0, 5.0))
        
        # Simular 10% de fallos aleatorios para probar resilience
        if random.random() < 0.1:
            raise httpx.HTTPError("Simulated AI service failure")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/skills-assessment",
                    json=evaluation_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error calling AI service (will retry): {e}")
                raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def generate_career_paths(
        self, 
        user_profile: Dict[str, Any],
        ai_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Llama al servicio de IA para generar senderos de carrera personalizados.
        Incluye retry automático (máximo 3 intentos con backoff exponencial).
        
        Args:
            user_profile: Perfil del usuario (posición actual, experiencia, etc.)
            ai_profile: Perfil de IA del assessment completado
            
        Returns:
            Dict con senderos de carrera generados
                {
                    "generated_paths": [
                        {
                            "path_name": str,
                            "recommended": bool,
                            "total_duration_months": int,
                            "feasibility_score": float,
                            "steps": [
                                {
                                    "step_number": int,
                                    "title": str,
                                    "target_role": str,
                                    "duration_months": int,
                                    "required_competencies": [str],
                                    "development_actions": [
                                        {
                                            "type": str (training, project, mentoring),
                                            "description": str
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
        """
        # Simular latencia (2-5 segundos)
        await asyncio.sleep(random.uniform(2.0, 5.0))
        
        # Simular 10% de fallos aleatorios
        if random.random() < 0.1:
            raise httpx.HTTPError("Simulated AI service failure")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "user_profile": user_profile,
                    "ai_profile": ai_profile
                }
                response = await client.post(
                    f"{self.base_url}/career-path-generator",
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error generating career paths (will retry): {e}")
                raise


# Instancia singleton del servicio
ai_service = AIIntegrationService()
