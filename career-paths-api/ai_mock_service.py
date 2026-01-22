"""
Mock AI service to simulate skills analysis and career path generation.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import random

app = FastAPI(title="AI Mock Service")


class SkillsAssessmentRequest(BaseModel):
    """Request structure: user_id, cycle_id, evaluations array"""
    user_id: str
    cycle_id: str
    evaluations: List[Dict[str, Any]]


class CareerPathRequest(BaseModel):
    """Request: user_profile + ai_profile"""
    user_profile: Dict[str, Any]
    ai_profile: Dict[str, Any]


@app.get("/")
async def root():
    return {"service": "AI Mock Service", "status": "running", "version": "2.0"}


@app.post("/skills-assessment")
async def assess_skills(request: SkillsAssessmentRequest):
    """
    Simulates skills analysis using AI.
    Processes 360° evaluations with evaluator/evaluatee/relationship structure.
    
    Request structure:
    {
        "user_id": "uuid",
        "cycle_id": "uuid",
        "evaluations": [
            {
                "evaluator_id": "uuid",
                "relationship": "SELF|MANAGER|PEER|DIRECT_REPORT",
                "competencies": [
                    {"competency_name": "Leadership", "score": 8, "comments": "..."}
                ]
            }
        ]
    }
    """
    evaluations = request.evaluations
    
    # Group competencies by evaluator type
    competency_scores = {}
    
    for evaluation in evaluations:
        relationship = evaluation.get("relationship", "PEER")
        competencies = evaluation.get("competencies", [])
        
        for comp in competencies:
            name = comp.get("competency_name", "")
            score = comp.get("score", 5)
            
            if name not in competency_scores:
                competency_scores[name] = {
                    "SELF": [],
                    "MANAGER": [],
                    "PEER": [],
                    "DIRECT_REPORT": []
                }
            
            competency_scores[name][relationship].append(score)
    
    # Analyze competencies
    strengths = []
    growth_areas = []
    hidden_talents = []
    
    for comp_name, scores_by_type in competency_scores.items():
        all_scores = []
        for score_list in scores_by_type.values():
            all_scores.extend(score_list)
        
        if not all_scores:
            continue
        
        avg_score = sum(all_scores) / len(all_scores)
        
        # Detect hidden talents: low SELF but high others
        self_scores = scores_by_type.get("SELF", [])
        other_scores = (scores_by_type.get("MANAGER", []) + 
                       scores_by_type.get("PEER", []) + 
                       scores_by_type.get("DIRECT_REPORT", []))
        
        if self_scores and other_scores:
            self_avg = sum(self_scores) / len(self_scores)
            others_avg = sum(other_scores) / len(other_scores)
            
            if self_avg < 6 and others_avg >= 7:
                hidden_talents.append(comp_name)
                continue
        
        if avg_score >= 8:
            strengths.append(comp_name)
        elif avg_score <= 5:
            growth_areas.append(comp_name)
    
    # Generate role readiness based on strengths
    readiness_for_roles = [
        {
            "role_name": "Gerente Regional",
            "readiness_percentage": min(90, 50 + len(strengths) * 8),
            "reasoning": f"Fortalezas identificadas: {', '.join(strengths[:3]) if strengths else 'Ninguna'}. Áreas a desarrollar: {', '.join(growth_areas[:2]) if growth_areas else 'Ninguna'}."
        },
        {
            "role_name": "Director de Operaciones",
            "readiness_percentage": min(75, 40 + len(strengths) * 6),
            "reasoning": f"Requiere desarrollo en: {', '.join(growth_areas[:3]) if growth_areas else 'competencias estratégicas'}. Fortalezas alineadas: {len(strengths)}/{len(competency_scores)}."
        },
        {
            "role_name": "Coordinador de Equipo",
            "readiness_percentage": min(95, 70 + len(strengths) * 5),
            "reasoning": f"Alta preparación. Fortalezas clave: {', '.join(strengths[:2]) if strengths else 'liderazgo básico'}."
        }
    ]
    
    return {
        "strengths": strengths,
        "growth_areas": growth_areas,
        "hidden_talents": hidden_talents,
        "readiness_for_roles": readiness_for_roles
    }


@app.post("/career-path-generator")
async def generate_career_path(request: CareerPathRequest):
    """
    Simulates personalized career path generation using AI.
    Returns structure compatible with CareerPath, CareerPathStep and DevelopmentAction.
    
    Response structure:
    {
        "generated_paths": [
            {
                "path_name": "...",
                "recommended": bool,
                "total_duration_months": int,
                "feasibility_score": float,
                "steps": [
                    {
                        "step_number": int,
                        "title": "...",
                        "target_role": "...",
                        "duration_months": int,
                        "required_competencies": [...],
                        "development_actions": [
                            {"type": "training|project|mentoring", "description": "..."}
                        ]
                    }
                ]
            }
        ]
    }
    """
    user_profile = request.user_profile
    ai_profile = request.ai_profile
    
    current_position = user_profile.get("current_position", "Analista")
    strengths = ai_profile.get("strengths", [])
    growth_areas = ai_profile.get("growth_areas", [])
    
    # Generate 2-3 personalized paths
    generated_paths = []
    
    # Path 1: Leadership Route (recommended if has strengths)
    path1 = {
        "path_name": "Ruta de Liderazgo Ejecutivo",
        "recommended": len(strengths) >= 3,
        "total_duration_months": 18,
        "feasibility_score": 0.75 if len(strengths) >= 3 else 0.60,
        "steps": [
            {
                "step_number": 1,
                "title": "Fundamentos de Liderazgo",
                "target_role": "Team Leader",
                "duration_months": 6,
                "required_competencies": ["Liderazgo", "Comunicación", "Trabajo en Equipo"],
                "development_actions": [
                    {"type": "training", "description": "Curso de Liderazgo Estratégico Avanzado"},
                    {"type": "project", "description": "Liderar proyecto piloto de mejora de procesos"},
                    {"type": "mentoring", "description": "Mentoría con gerente experimentado"}
                ]
            },
            {
                "step_number": 2,
                "title": "Gestión Estratégica",
                "target_role": "Gerente de Área",
                "duration_months": 8,
                "required_competencies": ["Pensamiento Estratégico", "Gestión de Equipos", "Toma de Decisiones"],
                "development_actions": [
                    {"type": "training", "description": "MBA Ejecutivo o Diplomado en Gestión"},
                    {"type": "project", "description": "Liderar iniciativa de transformación digital"},
                    {"type": "mentoring", "description": "Programa de coaching ejecutivo"}
                ]
            },
            {
                "step_number": 3,
                "title": "Liderazgo Ejecutivo",
                "target_role": "Gerente Regional",
                "duration_months": 4,
                "required_competencies": ["Visión Estratégica", "Gestión Financiera", "Influencia"],
                "development_actions": [
                    {"type": "training", "description": "Programa de desarrollo ejecutivo"},
                    {"type": "project", "description": "Presentar propuesta estratégica a dirección"},
                    {"type": "mentoring", "description": "Shadowing con director ejecutivo"}
                ]
            }
        ]
    }
    generated_paths.append(path1)
    
    # Path 2: Technical Specialization Route
    path2 = {
        "path_name": "Ruta de Especialización Técnica",
        "recommended": len(growth_areas) <= 2,
        "total_duration_months": 12,
        "feasibility_score": 0.85,
        "steps": [
            {
                "step_number": 1,
                "title": "Especialista",
                "target_role": "Especialista Senior",
                "duration_months": 6,
                "required_competencies": ["Expertise Técnico", "Resolución de Problemas", "Innovación"],
                "development_actions": [
                    {"type": "training", "description": "Certificaciones profesionales avanzadas"},
                    {"type": "project", "description": "Proyecto de innovación o mejora continua"},
                    {"type": "training", "description": "Cursos de tecnologías emergentes"}
                ]
            },
            {
                "step_number": 2,
                "title": "Referente Técnico",
                "target_role": "Consultor Interno",
                "duration_months": 6,
                "required_competencies": ["Mentoría", "Comunicación Técnica", "Liderazgo de Opinión"],
                "development_actions": [
                    {"type": "project", "description": "Publicar artículos técnicos o case studies"},
                    {"type": "mentoring", "description": "Mentoría a juniors"},
                    {"type": "training", "description": "Programa de train the trainer"}
                ]
            }
        ]
    }
    generated_paths.append(path2)
    
    # Path 3: Hybrid Route (if applicable)
    if len(strengths) >= 2 and len(growth_areas) <= 3:
        path3 = {
            "path_name": "Ruta Híbrida: Gestión + Especialización",
            "recommended": False,
            "total_duration_months": 15,
            "feasibility_score": 0.68,
            "steps": [
                {
                    "step_number": 1,
                    "title": "Líder Técnico",
                    "target_role": "Tech Lead",
                    "duration_months": 8,
                    "required_competencies": ["Liderazgo Técnico", "Arquitectura", "Gestión de Proyectos"],
                    "development_actions": [
                        {"type": "training", "description": "Certificación en arquitectura de soluciones"},
                        {"type": "project", "description": "Liderar equipo técnico en proyecto complejo"},
                        {"type": "mentoring", "description": "Mentoría con arquitecto senior"}
                    ]
                },
                {
                    "step_number": 2,
                    "title": "Gerente de Tecnología",
                    "target_role": "Gerente de TI",
                    "duration_months": 7,
                    "required_competencies": ["Gestión de TI", "Estrategia Tecnológica", "Presupuesto"],
                    "development_actions": [
                        {"type": "training", "description": "MBA con enfoque en tecnología"},
                        {"type": "project", "description": "Definir roadmap tecnológico del área"},
                        {"type": "mentoring", "description": "Coaching con CTO"}
                    ]
                }
            ]
        }
        generated_paths.append(path3)
    
    return {
        "generated_paths": generated_paths
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
