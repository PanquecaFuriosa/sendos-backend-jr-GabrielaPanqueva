"""
Servicio mock de IA para simular análisis de habilidades y generación de senderos de carrera.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import random

app = FastAPI(title="AI Mock Service")


class SkillsAssessmentRequest(BaseModel):
    """Request con estructura: user_id, cycle_id, evaluations array"""
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
    Simula el análisis de habilidades usando IA.
    Procesa evaluaciones 360° con estructura evaluator/evaluatee/relationship.
    
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
    
    # Agrupar competencias por tipo de evaluador
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
    
    # Analizar competencias
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
        
        # Detectar hidden talents: SELF bajo pero otros altos
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
    
    # Generar readiness para roles basado en fortalezas
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
    Simula la generación de senderos de carrera personalizados usando IA.
    Retorna estructura compatible con CareerPath, CareerPathStep y DevelopmentAction.
    
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
    
    # Generar 2-3 senderos personalizados
    generated_paths = []
    
    # Path 1: Ruta de Liderazgo (recomendado si tiene fortalezas)
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
    
    # Path 2: Ruta de Especialización Técnica
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
    
    # Path 3: Ruta Híbrida (solo si tiene buen balance)
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


@app.get("/")
async def root():
    return {"service": "AI Mock Service", "status": "running"}


@app.post("/skills-assessment")
async def assess_skills(request: SkillsAssessmentRequest):
    """
    Simula el análisis de habilidades usando IA.
    En producción, esto llamaría a un modelo de ML real.
    """
    competencies = request.evaluation_data.get("competencies", [])
    
    strengths = []
    growth_areas = []
    hidden_talents = []
    
    for comp in competencies:
        name = comp.get("name", "")
        self_score = comp.get("self_score", 0)
        peer_scores = comp.get("peer_scores", [])
        manager_score = comp.get("manager_score", 0)
        
        # Calcular promedio
        all_scores = [self_score, manager_score] + peer_scores
        avg_score = sum(all_scores) / len(all_scores)
        
        if avg_score >= 8:
            strengths.append(name)
        elif avg_score <= 5:
            growth_areas.append(name)
        else:
            hidden_talents.append(name)
    
    # Generar readiness para roles
    readiness_for_roles = [
        {
            "role": "Gerente Regional",
            "readiness_percentage": random.randint(55, 75),
            "missing_competencies": growth_areas[:2] if growth_areas else ["Liderazgo Estratégico"]
        },
        {
            "role": "Director de Operaciones",
            "readiness_percentage": random.randint(40, 60),
            "missing_competencies": growth_areas if growth_areas else ["Visión Estratégica", "Gestión Financiera"]
        },
        {
            "role": "Coordinador de Equipo",
            "readiness_percentage": random.randint(75, 90),
            "missing_competencies": []
        }
    ]
    
    return {
        "skills_profile": {
            "strengths": strengths,
            "growth_areas": growth_areas,
            "hidden_talents": hidden_talents
        },
        "readiness_for_roles": readiness_for_roles
    }


@app.post("/career-path-generator")
async def generate_career_path(request: CareerPathRequest):
    """
    Simula la generación de senderos de carrera personalizados usando IA.
    En producción, esto usaría modelos de ML para predecir rutas óptimas.
    """
    user_profile = request.user_profile
    skills_profile = request.skills_profile
    readiness = request.readiness
    
    current_position = user_profile.get("current_position", "Analista")
    
    # Generar senderos recomendados
    recommended_paths = [
        {
            "target_role": "Gerente Regional",
            "timeline_months": 12,
            "milestones": [
                {
                    "description": "Completar certificación en Liderazgo Estratégico",
                    "target_month": 3,
                    "success_criteria": [
                        "Obtener certificación reconocida",
                        "Aplicar conceptos en proyecto real",
                        "Recibir feedback positivo de superiores"
                    ]
                },
                {
                    "description": "Liderar proyecto cross-funcional importante",
                    "target_month": 6,
                    "success_criteria": [
                        "Entregar proyecto a tiempo y dentro de presupuesto",
                        "Gestionar equipo de al menos 5 personas",
                        "Demostrar habilidades de stakeholder management"
                    ]
                },
                {
                    "description": "Programa de mentoría con Gerente Regional",
                    "target_month": 9,
                    "success_criteria": [
                        "Completar 10 sesiones de mentoría",
                        "Implementar al menos 3 mejoras sugeridas",
                        "Recibir endorsement del mentor"
                    ]
                },
                {
                    "description": "Presentar propuesta estratégica a dirección",
                    "target_month": 12,
                    "success_criteria": [
                        "Desarrollar business case completo",
                        "Presentar a comité ejecutivo",
                        "Obtener aprobación para implementación"
                    ]
                }
            ],
            "development_actions": [
                {
                    "action_type": "training",
                    "description": "Curso de Liderazgo Estratégico Avanzado",
                    "priority": "high"
                },
                {
                    "action_type": "project",
                    "description": "Liderar iniciativa de transformación digital",
                    "priority": "high"
                },
                {
                    "action_type": "mentoring",
                    "description": "Mentoría 1:1 con ejecutivo senior",
                    "priority": "medium"
                },
                {
                    "action_type": "networking",
                    "description": "Participar en conferencias de liderazgo",
                    "priority": "medium"
                }
            ],
            "success_probability": 0.75
        },
        {
            "target_role": "Especialista Senior",
            "timeline_months": 6,
            "milestones": [
                {
                    "description": "Certificación técnica avanzada",
                    "target_month": 2,
                    "success_criteria": [
                        "Obtener certificación profesional",
                        "Alcanzar score superior al 90%"
                    ]
                },
                {
                    "description": "Publicar artículo técnico o case study",
                    "target_month": 4,
                    "success_criteria": [
                        "Publicar en blog corporativo o medio externo",
                        "Recibir al menos 500 visualizaciones"
                    ]
                },
                {
                    "description": "Convertirse en referente interno",
                    "target_month": 6,
                    "success_criteria": [
                        "Ser consultado por al menos 3 equipos",
                        "Dar al menos 2 charlas internas"
                    ]
                }
            ],
            "development_actions": [
                {
                    "action_type": "training",
                    "description": "Especialización técnica avanzada",
                    "priority": "high"
                },
                {
                    "action_type": "project",
                    "description": "Proyecto de innovación o mejora",
                    "priority": "high"
                },
                {
                    "action_type": "knowledge_sharing",
                    "description": "Programa de capacitación interna",
                    "priority": "medium"
                }
            ],
            "success_probability": 0.85
        }
    ]
    
    # Plan de desarrollo de habilidades
    skill_development_plan = [
        {
            "skill": "Pensamiento Estratégico",
            "current_level": "Básico",
            "target_level": "Avanzado",
            "recommended_actions": [
                "Tomar curso de estrategia empresarial",
                "Participar en sesiones de planificación estratégica",
                "Leer casos de estudio de Harvard Business Review",
                "Practicar análisis FODA y matrices estratégicas"
            ],
            "estimated_time_months": 6
        },
        {
            "skill": "Gestión de Equipos",
            "current_level": "Intermedio",
            "target_level": "Avanzado",
            "recommended_actions": [
                "Taller de gestión de equipos de alto rendimiento",
                "Coaching individual con experto en RRHH",
                "Liderar equipo en proyecto estratégico",
                "Implementar framework de OKRs con el equipo"
            ],
            "estimated_time_months": 4
        },
        {
            "skill": "Comunicación Ejecutiva",
            "current_level": "Básico",
            "target_level": "Intermedio",
            "recommended_actions": [
                "Curso de presentaciones ejecutivas",
                "Práctica con feedback de mentores",
                "Presentar en reuniones de liderazgo",
                "Toastmasters o club de oratoria"
            ],
            "estimated_time_months": 3
        },
        {
            "skill": "Toma de Decisiones Basada en Datos",
            "current_level": "Intermedio",
            "target_level": "Avanzado",
            "recommended_actions": [
                "Curso de análisis de datos para negocios",
                "Usar herramientas de BI en proyectos reales",
                "Desarrollar dashboards de KPIs",
                "Participar en proyectos de data analytics"
            ],
            "estimated_time_months": 5
        }
    ]
    
    # Recursos de aprendizaje
    learning_resources = [
        {
            "type": "course",
            "title": "Liderazgo Estratégico para Ejecutivos",
            "provider": "Coursera - University of Illinois",
            "duration_hours": 40,
            "url": "https://www.coursera.org/specializations/strategic-leadership",
            "cost": "$49/mes",
            "relevance": "Alta - Desarrollo de habilidades de liderazgo"
        },
        {
            "type": "book",
            "title": "Good to Great: Why Some Companies Make the Leap and Others Don't",
            "author": "Jim Collins",
            "relevance": "Transformación organizacional y liderazgo",
            "estimated_reading_hours": 12
        },
        {
            "type": "book",
            "title": "The Five Dysfunctions of a Team",
            "author": "Patrick Lencioni",
            "relevance": "Gestión de equipos de alto rendimiento",
            "estimated_reading_hours": 8
        },
        {
            "type": "course",
            "title": "Data-Driven Decision Making",
            "provider": "edX - MIT",
            "duration_hours": 30,
            "url": "https://www.edx.org/course/data-driven-decision-making",
            "cost": "Gratis (certificado $99)",
            "relevance": "Media - Mejora de habilidades analíticas"
        },
        {
            "type": "mentoring",
            "title": "Programa de Mentoría Ejecutiva",
            "provider": "Interno - Sendos",
            "duration_months": 6,
            "description": "Mentoría 1:1 con ejecutivo senior",
            "relevance": "Alta - Aprendizaje directo de líderes experimentados"
        },
        {
            "type": "workshop",
            "title": "Taller de Comunicación Ejecutiva",
            "provider": "Dale Carnegie",
            "duration_hours": 16,
            "description": "Desarrollo de habilidades de presentación y comunicación",
            "relevance": "Alta - Esencial para roles de liderazgo"
        }
    ]
    
    return {
        "recommended_paths": recommended_paths,
        "skill_development_plan": skill_development_plan,
        "learning_resources": learning_resources
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
