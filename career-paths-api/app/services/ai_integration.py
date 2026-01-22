"""
AI integration service for skills analysis and career path generation.
Includes retry logic with tenacity and robust error handling.
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
    Service to integrate with the AI service (mock or real).
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
        Calls the AI service to analyze skills based on 360° evaluation.
        Includes automatic retry (max 3 attempts with exponential backoff).
        
        Args:
            evaluation_data: Evaluation data in dict format
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
            Dict with skills profile and role readiness
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
        # Simulate latency (2-5 seconds)
        await asyncio.sleep(random.uniform(2.0, 5.0))
        
        # Simulate 10% random failures to test resilience
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
        Calls the AI service to generate personalized career paths.
        Includes automatic retry (max 3 attempts with exponential backoff).
        
        Args:
            user_profile: User profile (current position, experience, etc.)
            ai_profile: AI profile from completed assessment
            
        Returns:
            Dict with generated career paths
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
        # Simulate latency (2-5 seconds)
        await asyncio.sleep(random.uniform(2.0, 5.0))
        
        # Simulate 10% random failures
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


# Singleton instance of the service
ai_service = AIIntegrationService()
