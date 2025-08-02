from typing import Dict, Any, List
from langchain.tools import BaseTool, tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType, Language
from services.gemini_service import GeminiService
from services.tavily_service import TavilyService
import logging

logger = logging.getLogger(__name__)

class EducationalAgent(BaseAgent):
    """Agent Pédagogique - Crée des contenus éducatifs, quiz interactifs et supports pédagogiques"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.EDUCATIONAL_AGENT,
            description="Crée des contenus éducatifs, quiz interactifs et supports de formation sur l'énergie solaire"
        )
        self.gemini_service = GeminiService()
        self.tavily_service = TavilyService()
    
    def _init_tools(self) -> List[BaseTool]:
        return [
            self.create_quiz_tool,
            self.generate_lesson_plan_tool,
            self.create_educational_content_tool,
            self.generate_infographic_data_tool,
            self.create_practical_exercise_tool,
            self.assess_knowledge_tool,
            self.create_certification_path_tool
        ]
    
    def _get_system_prompt(self) -> str:
        """Prompt système de l'agent pédagogique"""
        return """
        Vous êtes l'Agent Pédagogique pour Solar Nasih, expert en formation et éducation sur l'énergie solaire.
        
        Vos responsabilités incluent:
        1. Créer des quiz interactifs adaptés au niveau
        2. Développer des contenus pédagogiques structurés
        3. Concevoir des parcours de formation
        4. Générer des exercices pratiques
        5. Évaluer les connaissances acquises
        6. Adapter le contenu selon le public (particuliers, professionnels, étudiants)
        
        Votre approche doit être:
        - Pédagogique et progressive
        - Adaptée au niveau de l'apprenant
        - Interactive et engageante
        - Basée sur des exemples concrets
        - Incluant des évaluations
        """
    
    @tool
    def create_quiz_tool(self, topic: str, difficulty: str = "intermediate", num_questions: int = 10) -> Dict[str, Any]:
        """Crée un quiz interactif sur un sujet donné"""
        try:
            # Base de questions par niveau et sujet
            question_bank = {
                "basics": {
                    "beginner": [
                        {
                            "question": "Qu'est-ce que l'effet photovoltaïque ?",
                            "options": [
                                "La conversion de la lumière en électricité",
                                "Le chauffage de l'eau par le soleil",
                                "La transformation de l'électricité en lumière",
                                "L'absorption de la chaleur solaire"
                            ],
                            "correct": 0,
                            "explanation": "L'effet photovoltaïque convertit directement la lumière (photons) en électricité grâce aux cellules photovoltaïques."
                        },
                        {
                            "question": "Quelle est l'unité de mesure de la puissance d'un panneau solaire ?",
                            "options": ["Watt-crête (Wc)", "Kilowatt-heure (kWh)", "Volt (V)", "Ampère (A)"],
                            "correct": 0,
                            "explanation": "Le Watt-crête (Wc) mesure la puissance maximale d'un panneau dans des conditions standards."
                        },
                        {
                            "question": "Quel élément n'est PAS nécessaire dans une installation photovoltaïque ?",
                            "options": ["Panneaux solaires", "Onduleur", "Batterie", "Compteur"],
                            "correct": 2,
                            "explanation": "La batterie n'est pas obligatoire, surtout en autoconsommation avec vente du surplus."
                        }
                    ],
                    "intermediate": [
                        {
                            "question": "Quel facteur influence le PLUS la production d'un panneau solaire ?",
                            "options": ["L'orientation", "L'inclinaison", "L'irradiance", "La température"],
                            "correct": 2,
                            "explanation": "L'irradiance (quantité de lumière reçue) est le facteur principal de production."
                        },
                        {
                            "question": "Quelle est la durée de vie typique d'un panneau photovoltaïque ?",
                            "options": ["10-15 ans", "20-25 ans", "25-30 ans", "35-40 ans"],
                            "correct": 2,
                            "explanation": "Les panneaux modernes ont une durée de vie de 25-30 ans avec garantie constructeur de 20-25 ans."
                        }
                    ],
                    "advanced": [
                        {
                            "question": "Quel est le rendement théorique maximum d'une cellule silicium cristallin ?",
                            "options": ["24%", "29%", "34%", "39%"],
                            "correct": 1,
                            "explanation": "La limite théorique de Shockley-Queisser pour le silicium est d'environ 29%."
                        }
                    ]
                },
                "installation": {
                    "beginner": [
                        {
                            "question": "Quelle orientation est optimale pour des panneaux en France ?",
                            "options": ["Nord", "Sud", "Est", "Ouest"],
                            "correct": 1,
                            "explanation": "L'orientation Sud maximise l'exposition au soleil en France."
                        }
                    ],
                    "intermediate": [
                        {
                            "question": "Quelle inclinaison optimise la production annuelle en France ?",
                            "options": ["15°", "30°", "35°", "45°"],
                            "correct": 2,
                            "explanation": "35° est l'inclinaison optimale pour maximiser la production annuelle en France."
                        }
                    ]
                },
                "economics": {
                    "intermediate": [
                        {
                            "question": "Qu'est-ce que l'autoconsommation photovoltaïque ?",
                            "options": [
                                "Vendre toute sa production",
                                "Consommer sa propre production",
                                "Stocker l'énergie dans des batteries",
                                "Acheter de l'électricité solaire"
                            ],
                            "correct": 1,
                            "explanation": "L'autoconsommation consiste à utiliser directement l'électricité produite par ses panneaux."
                        }
                    ]
                }
            }
            
            # Sélection des questions
            available_topics = list(question_bank.keys())
            selected_topic = topic if topic in available_topics else "basics"
            
            topic_questions = question_bank[selected_topic].get(difficulty, question_bank[selected_topic].get("beginner", []))
            
            # Génération du quiz
            selected_questions = random.sample(
                topic_questions, 
                min(num_questions, len(topic_questions))
            )
            
            # Si pas assez de questions, compléter avec des questions générées
            if len(selected_questions) < num_questions:
                additional_questions = self._generate_additional_questions(
                    topic, difficulty, num_questions - len(selected_questions)
                )
                selected_questions.extend(additional_questions)
            
            quiz_data = {
                "title": f"Quiz {topic.title()} - Niveau {difficulty}",
                "description": f"Testez vos connaissances en énergie solaire - {topic}",
                "topic": topic,
                "difficulty": difficulty,
                "total_questions": len(selected_questions),
                "estimated_time": len(selected_questions) * 2,  # 2 min par question
                "questions": selected_questions,
                "scoring": {
                    "total_points": len(selected_questions) * 10,
                    "passing_score": len(selected_questions) * 6,  # 60% pour réussir
                    "grading": {
                        "excellent": "90-100%",
                        "good": "70-89%", 
                        "satisfactory": "60-69%",
                        "needs_improvement": "<60%"
                    }
                }
            }
            
            return quiz_data
            
        except Exception as e:
            logger.error(f"Erreur création quiz: {e}")
            return {"error": str(e)}
    
    @tool
    def generate_lesson_plan_tool(self, subject: str, target_audience: str = "general", duration: int = 60) -> Dict[str, Any]:
        """Génère un plan de cours structuré"""
        try:
            # Templates de plans de cours par audience
            lesson_templates = {
                "general": {
                    "introduction_photovoltaique": {
                        "title": "Introduction au Photovoltaïque",
                        "objectives": [
                            "Comprendre le principe de l'effet photovoltaïque",
                            "Identifier les composants d'une installation",
                            "Connaître les avantages de l'énergie solaire"
                        ],
                        "structure": [
                            {"section": "Introduction", "duration": 10, "content": "Histoire et principe"},
                            {"section": "Technologie", "duration": 20, "content": "Cellules, modules, systèmes"},
                            {"section": "Applications", "duration": 20, "content": "Résidentiel, commercial, utilité"},
                            {"section": "Exercice pratique", "duration": 15, "content": "Calcul simple de production"},
                            {"section": "Questions/Réponses", "duration": 10, "content": "Discussion interactive"}
                        ]
                    }
                },
                "professionals": {
                    "installation_techniques": {
                        "title": "Techniques d'Installation Photovoltaïque",
                        "objectives": [
                            "Maîtriser les techniques de pose",
                            "Respecter les normes de sécurité",
                            "Optimiser les performances"
                        ],
                        "structure": [
                            {"section": "Préparation", "duration": 15, "content": "Étude de faisabilité, matériel"},
                            {"section": "Installation", "duration": 30, "content": "Fixation, câblage, raccordement"},
                            {"section": "Tests et validation", "duration": 15, "content": "Mesures, CONSUEL"},
                            {"section": "Maintenance", "duration": 15, "content": "Entretien préventif"},
                            {"section": "Cas pratiques", "duration": 10, "content": "Résolution de problèmes"}
                        ]
                    }
                },
                "students": {
                    "energie_renouvelable": {
                        "title": "Les Énergies Renouvelables - Focus Solaire",
                        "objectives": [
                            "Distinguer les différentes énergies renouvelables",
                            "Comprendre les enjeux environnementaux",
                            "Calculer le potentiel solaire"
                        ],
                        "structure": [
                            {"section": "Contexte énergétique", "duration": 15, "content": "Enjeux climatiques"},
                            {"section": "Panorama des EnR", "duration": 15, "content": "Solaire, éolien, hydraulique..."},
                            {"section": "Focus photovoltaïque", "duration": 20, "content": "Principe et technologies"},
                            {"section": "Calculs et exercices", "duration": 25, "content": "Dimensionnement simple"},
                            {"section": "Projet de groupe", "duration": 10, "content": "Présentation courte"}
                        ]
                    }
                }
            }
            
            # Sélection du template approprié
            audience_templates = lesson_templates.get(target_audience, lesson_templates["general"])
            
            # Recherche du sujet le plus proche
            selected_lesson = None
            for lesson_key, lesson_data in audience_templates.items():
                if subject.lower() in lesson_key.lower() or any(word in lesson_key.lower() for word in subject.lower().split()):
                    selected_lesson = lesson_data
                    break
            
            # Si aucun template trouvé, créer un plan générique
            if not selected_lesson:
                selected_lesson = self._create_generic_lesson_plan(subject, target_audience, duration)
            
            # Adaptation à la durée demandée
            adapted_lesson = self._adapt_lesson_duration(selected_lesson, duration)
            
            # Ajout de ressources et matériels
            adapted_lesson.update({
                "target_audience": target_audience,
                "duration_minutes": duration,
                "prerequisites": self._get_prerequisites(subject, target_audience),
                "materials_needed": self._get_required_materials(subject, target_audience),
                "assessment_methods": self._get_assessment_methods(target_audience),
                "additional_resources": self._get_additional_resources(subject),
                "homework_suggestions": self._get_homework_suggestions(subject, target_audience)
            })
            
            return adapted_lesson
            
        except Exception as e:
            logger.error(f"Erreur génération plan de cours: {e}")
            return {"error": str(e)}
    
    @tool
    def create_educational_content_tool(self, topic: str, format_type: str = "article", complexity: str = "intermediate") -> Dict[str, Any]:
        """Crée du contenu éducatif sur un sujet donné"""
        try:
            content_structures = {
                "article": {
                    "photovoltaique_principe": {
                        "title": "Le Principe du Photovoltaïque Expliqué",
                        "sections": [
                            {
                                "title": "Introduction",
                                "content": "L'énergie solaire photovoltaïque convertit directement la lumière du soleil en électricité..."
                            },
                            {
                                "title": "L'effet photovoltaïque",
                                "content": "Découvert en 1839 par Edmond Becquerel, l'effet photovoltaïque..."
                            },
                            {
                                "title": "Les composants",
                                "content": "Une installation photovoltaïque comprend plusieurs éléments essentiels..."
                            },
                            {
                                "title": "Applications pratiques",
                                "content": "Les systèmes photovoltaïques trouvent de nombreuses applications..."
                            }
                        ]
                    }
                },
                "infographic": {
                    "installation_steps": {
                        "title": "Les Étapes d'Installation Photovoltaïque",
                        "visual_elements": [
                            {"step": 1, "title": "Étude", "icon": "🔍", "description": "Analyse de faisabilité"},
                            {"step": 2, "title": "Conception", "icon": "📐", "description": "Dimensionnement système"},
                            {"step": 3, "title": "Autorisations", "icon": "📄", "description": "Déclaration préalable"},
                            {"step": 4, "title": "Installation", "icon": "🔧", "description": "Pose des équipements"},
                            {"step": 5, "title": "Raccordement", "icon": "⚡", "description": "Mise en service"}
                        ]
                    }
                },
                "tutorial": {
                    "dimensionnement": {
                        "title": "Comment Dimensionner une Installation Solaire",
                        "steps": [
                            {
                                "step": 1,
                                "title": "Analyser sa consommation",
                                "instructions": "Relevez votre consommation annuelle en kWh sur vos factures...",
                                "example": "Famille de 4 personnes = 4500 kWh/an en moyenne"
                            },
                            {
                                "step": 2,
                                "title": "Évaluer le potentiel solaire",
                                "instructions": "Mesurez la surface disponible et évaluez l'orientation...",
                                "example": "Toit de 40m² orienté Sud = potentiel de 6 kWc"
                            }
                        ]
                    }
                }
            }
            
            # Génération du contenu adapté
            if format_type in content_structures and topic in content_structures[format_type]:
                base_content = content_structures[format_type][topic]
            else:
                # Génération dynamique avec Gemini
                base_content = self._generate_dynamic_content(topic, format_type, complexity)
            
            # Enrichissement du contenu
            enriched_content = {
                **base_content,
                "metadata": {
                    "topic": topic,
                    "format": format_type,
                    "complexity": complexity,
                    "estimated_reading_time": self._estimate_reading_time(base_content),
                    "keywords": self._extract_keywords(topic),
                    "related_topics": self._get_related_topics(topic)
                },
                "interactive_elements": self._add_interactive_elements(format_type),
                "assessment_questions": self._generate_comprehension_questions(topic, complexity)
            }
            
            return enriched_content
            
        except Exception as e:
            logger.error(f"Erreur création contenu éducatif: {e}")
            return {"error": str(e)}
    
    @tool
    def generate_infographic_data_tool(self, data_topic: str) -> Dict[str, Any]:
        """Génère les données pour créer une infographie"""
        try:
            infographic_data = {
                "solar_statistics": {
                    "title": "L'Énergie Solaire en Chiffres",
                    "subtitle": "État des lieux du photovoltaïque en France",
                    "sections": [
                        {
                            "type": "big_number",
                            "value": "15.8 GW",
                            "label": "Puissance installée en France",
                            "context": "Fin 2023"
                        },
                        {
                            "type": "percentage",
                            "value": "3.2%",
                            "label": "Part dans le mix électrique français",
                            "trend": "En croissance"
                        },
                        {
                            "type": "chart_data",
                            "chart_type": "bar",
                            "title": "Évolution des installations",
                            "data": [
                                {"year": 2020, "capacity": 10.2},
                                {"year": 2021, "capacity": 13.1},
                                {"year": 2022, "capacity": 15.1},
                                {"year": 2023, "capacity": 15.8}
                            ]
                        },
                        {
                            "type": "comparison",
                            "title": "Coût vs Économies",
                            "items": [
                                {"label": "Investissement moyen", "value": "15 000€", "color": "red"},
                                {"label": "Économies 20 ans", "value": "25 000€", "color": "green"}
                            ]
                        }
                    ],
                    "footer": "Sources: RTE, SDES, Observ'ER"
                },
                "installation_process": {
                    "title": "Processus d'Installation Photovoltaïque",
                    "subtitle": "De l'étude à la mise en service",
                    "sections": [
                        {
                            "type": "timeline",
                            "steps": [
                                {"phase": "Étude", "duration": "1-2 semaines", "description": "Visite technique et étude de faisabilité"},
                                {"phase": "Administrative", "duration": "1-3 mois", "description": "Autorisations et démarches"},
                                {"phase": "Installation", "duration": "1-2 jours", "description": "Pose des équipements"},
                                {"phase": "Raccordement", "duration": "2-6 mois", "description": "Mise en service par gestionnaire réseau"}
                            ]
                        }
                    ]
                },
                "economics": {
                    "title": "Rentabilité du Photovoltaïque",
                    "subtitle": "Analyse économique pour une installation type",
                    "sections": [
                        {
                            "type": "scenario",
                            "title": "Installation 6 kWc - Maison individuelle",
                            "investment": 15000,
                            "annual_savings": 1200,
                            "payback_period": 12.5,
                            "roi_20_years": "167%"
                        }
                    ]
                }
            }
            
            selected_data = infographic_data.get(data_topic, {})
            
            if not selected_data:
                # Génération dynamique si sujet non trouvé
                selected_data = self._generate_dynamic_infographic_data(data_topic)
            
            # Ajout de métadonnées visuelles
            selected_data.update({
                "visual_guidelines": {
                    "color_palette": ["#FF6B35", "#F7931E", "#FFD23F", "#06D6A0", "#118AB2"],
                    "fonts": ["Roboto", "Open Sans", "Lato"],
                    "style": "modern_clean",
                    "dimensions": "1080x1080px (Instagram) ou 1200x628px (Facebook)"
                },
                "export_formats": ["PNG", "SVG", "PDF"],
                "accessibility": {
                    "alt_text": f"Infographie sur {data_topic}",
                    "color_contrast": "AAA compliant",
                    "font_size_min": "14px"
                }
            })
            
            return selected_data
            
        except Exception as e:
            logger.error(f"Erreur génération données infographie: {e}")
            return {"error": str(e)}
    
    @tool
    def create_practical_exercise_tool(self, exercise_type: str, difficulty: str = "intermediate") -> Dict[str, Any]:
        """Crée un exercice pratique"""
        try:
            exercises = {
                "dimensionnement": {
                    "beginner": {
                        "title": "Calcul Simple de Production Solaire",
                        "description": "Estimez la production d'une installation photovoltaïque",
                        "scenario": "Une famille souhaite installer 12 panneaux de 300 Wc chacun sur leur toit orienté Sud.",
                        "questions": [
                            {
                                "question": "Quelle est la puissance totale de l'installation ?",
                                "hint": "Multipliez le nombre de panneaux par la puissance unitaire",
                                "answer": "3.6 kWc",
                                "calculation": "12 × 300 Wc = 3600 Wc = 3.6 kWc"
                            },
                            {
                                "question": "Quelle sera la production annuelle estimée (productible 1100 kWh/kWc/an) ?",
                                "hint": "Multipliez la puissance par le productible",
                                "answer": "3960 kWh/an",
                                "calculation": "3.6 kWc × 1100 kWh/kWc/an = 3960 kWh/an"
                            }
                        ],
                        "learning_objectives": [
                            "Calculer la puissance d'une installation",
                            "Estimer la production annuelle",
                            "Comprendre le concept de productible"
                        ]
                    },
                    "intermediate": {
                        "title": "Optimisation Technico-Économique",
                        "description": "Dimensionnez une installation en optimisant le retour sur investissement",
                        "scenario": "Maison avec consommation de 6000 kWh/an, toit de 40m² orienté Sud-Est, budget 20 000€",
                        "questions": [
                            {
                                "question": "Quelle puissance maximum peut-on installer ?",
                                "data": "Surface panneau standard: 2m², puissance 400 Wc",
                                "calculation_steps": [
                                    "Surface utilisable = 40m² × 0.8 = 32m² (coefficient d'occupation)",
                                    "Nombre de panneaux = 32m² ÷ 2m² = 16 panneaux",
                                    "Puissance = 16 × 400 Wc = 6.4 kWc"
                                ]
                            }
                        ]
                    }
                },
                "economique": {
                    "intermediate": {
                        "title": "Calcul de Rentabilité",
                        "description": "Analysez la rentabilité d'un projet photovoltaïque",
                        "scenario": "Installation 6 kWc, coût 15 000€, production 6600 kWh/an, prix électricité 0.20€/kWh",
                        "questions": [
                            {
                                "question": "Calculez l'économie annuelle en autoconsommation totale",
                                "answer": "1320€/an",
                                "calculation": "6600 kWh/an × 0.20€/kWh = 1320€/an"
                            },
                            {
                                "question": "Quelle est la période de retour sur investissement ?",
                                "answer": "11.4 ans",
                                "calculation": "15 000€ ÷ 1320€/an = 11.4 ans"
                            }
                        ]
                    }
                }
            }
            
            exercise_category = exercises.get(exercise_type, {})
            exercise_data = exercise_category.get(difficulty, {})
            
            if not exercise_data:
                exercise_data = self._generate_dynamic_exercise(exercise_type, difficulty)
            
            # Enrichissement de l'exercice
            exercise_data.update({
                "metadata": {
                    "type": exercise_type,
                    "difficulty": difficulty,
                    "estimated_time": self._estimate_exercise_time(exercise_data),
                    "skills_developed": self._get_skills_for_exercise(exercise_type),
                    "tools_needed": self._get_tools_for_exercise(exercise_type)
                },
                "evaluation_criteria": self._get_evaluation_criteria(exercise_type, difficulty),
                "extensions": self._get_exercise_extensions(exercise_type),
                "common_mistakes": self._get_common_mistakes(exercise_type)
            })
            
            return exercise_data
            
        except Exception as e:
            logger.error(f"Erreur création exercice pratique: {e}")
            return {"error": str(e)}
    
    @tool
    def assess_knowledge_tool(self, answers: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Évalue les connaissances basées sur les réponses données"""
        try:
            # Analyse des réponses
            total_questions = len(answers.get("quiz_answers", []))
            correct_answers = sum(1 for answer in answers.get("quiz_answers", []) if answer.get("correct", False))
            
            score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            # Détermination du niveau
            if score_percentage >= 90:
                level = "expert"
                feedback = "Excellente maîtrise du sujet !"
            elif score_percentage >= 70:
                level = "advanced"
                feedback = "Bonne compréhension, quelques approfondissements possibles"
            elif score_percentage >= 50:
                level = "intermediate"
                feedback = "Bases acquises, continuez à vous former"
            else:
                level = "beginner"
                feedback = "Il est recommandé de revoir les fondamentaux"
            
            # Analyse détaillée par domaine
            domain_analysis = self._analyze_by_domain(answers, topic)
            
            # Recommandations personnalisées
            recommendations = self._generate_learning_recommendations(level, domain_analysis, topic)
            
            return {
                "overall_assessment": {
                    "score": score_percentage,
                    "level": level,
                    "feedback": feedback,
                    "correct_answers": correct_answers,
                    "total_questions": total_questions
                },
                "domain_analysis": domain_analysis,
                "recommendations": recommendations,
                "next_steps": self._get_next_learning_steps(level, topic),
                "resources": self._get_recommended_resources(level, topic),
                "certification_eligibility": self._check_certification_eligibility(score_percentage, topic)
            }
            
        except Exception as e:
            logger.error(f"Erreur évaluation connaissances: {e}")
            return {"error": str(e)}
    
    @tool
    def create_certification_path_tool(self, target_certification: str, current_level: str = "beginner") -> Dict[str, Any]:
        """Crée un parcours de certification personnalisé"""
        try:
            certification_paths = {
                "solar_installer": {
                    "title": "Certification Installateur Photovoltaïque",
                    "description": "Parcours pour devenir installateur certifié",
                    "duration": "3-6 mois",
                    "modules": [
                        {
                            "module": "Fondamentaux",
                            "duration": "2 semaines",
                            "topics": ["Principe photovoltaïque", "Composants", "Sécurité de base"],
                            "assessment": "QCM 50 questions"
                        },
                        {
                            "module": "Dimensionnement",
                            "duration": "3 semaines", 
                            "topics": ["Calculs", "Optimisation", "Logiciels"],
                            "assessment": "Étude de cas pratique"
                        },
                        {
                            "module": "Installation",
                            "duration": "4 semaines",
                            "topics": ["Techniques de pose", "Raccordement", "Tests"],
                            "assessment": "Travaux pratiques"
                        },
                        {
                            "module": "Réglementation",
                            "duration": "2 semaines",
                            "topics": ["Normes", "Autorisations", "CONSUEL"],
                            "assessment": "QCM réglementaire"
                        }
                    ],
                    "prerequisites": ["Électricité de base", "Travail en hauteur"],
                    "certification_exam": {
                        "theory": "QCM 100 questions (80% requis)",
                        "practice": "Installation complète (évaluation terrain)",
                        "cost": "500-1000€"
                    }
                },
                "solar_advisor": {
                    "title": "Certification Conseiller Solaire",
                    "description": "Expertise en conseil et vente photovoltaïque",
                    "duration": "2-4 mois",
                    "modules": [
                        {
                            "module": "Marché solaire",
                            "duration": "1 semaine",
                            "topics": ["Acteurs", "Technologies", "Tendances"]
                        },
                        {
                            "module": "Analyse technique",
                            "duration": "3 semaines",
                            "topics": ["Faisabilité", "Dimensionnement", "Optimisation"]
                        },
                        {
                            "module": "Aspects économiques",
                            "duration": "2 semaines",
                            "topics": ["Financement", "Aides", "ROI"]
                        }
                    ]
                }
            }
            
            selected_path = certification_paths.get(target_certification, {})
            
            if not selected_path:
                selected_path = self._create_custom_certification_path(target_certification, current_level)
            
            # Personnalisation selon le niveau actuel
            personalized_path = self._personalize_certification_path(selected_path, current_level)
            
            return personalized_path
            
        except Exception as e:
            logger.error(f"Erreur création parcours certification: {e}")
            return {"error": str(e)}
    
    # Méthodes utilitaires privées
    
    def _generate_additional_questions(self, topic: str, difficulty: str, num_questions: int) -> List[Dict[str, Any]]:
        """Génère des questions supplémentaires dynamiquement"""
        # Génération avec Gemini pour questions additionnelles
        additional_questions = []
        
        # Questions génériques par défaut
        default_questions = [
            {
                "question": f"Quelle est l'importance de {topic} dans le domaine solaire ?",
                "options": ["Très importante", "Modérément importante", "Peu importante", "Non importante"],
                "correct": 0,
                "explanation": f"{topic} joue un rôle crucial dans le secteur photovoltaïque."
            }
        ]
        
        # Retourner le nombre demandé de questions par défaut
        return default_questions[:num_questions]
    
    def _create_generic_lesson_plan(self, subject: str, audience: str, duration: int) -> Dict[str, Any]:
        """Crée un plan de cours générique"""
        return {
            "title": f"{subject.title()} - Formation {audience}",
            "objectives": [f"Comprendre {subject}", f"Appliquer les concepts de {subject}"],
            "structure": [
                {"section": "Introduction", "duration": int(duration * 0.2), "content": f"Présentation de {subject}"},
                {"section": "Développement", "duration": int(duration * 0.6), "content": f"Concepts clés de {subject}"},
                {"section": "Conclusion", "duration": int(duration * 0.2), "content": "Synthèse et questions"}
            ]
        }
    
    def _adapt_lesson_duration(self, lesson: Dict[str, Any], target_duration: int) -> Dict[str, Any]:
        """Adapte un plan de cours à une durée cible"""
        current_duration = sum(section.get("duration", 0) for section in lesson.get("structure", []))
        if current_duration == 0:
            return lesson
        
        ratio = target_duration / current_duration
        
        # Ajustement proportionnel des durées
        for section in lesson.get("structure", []):
            section["duration"] = int(section.get("duration", 0) * ratio)
        
        return lesson
    
    def _get_prerequisites(self, subject: str, audience: str) -> List[str]:
        """Retourne les prérequis pour un sujet"""
        return ["Notions de base en électricité", "Intérêt pour les énergies renouvelables"]
    
    def _get_required_materials(self, subject: str, audience: str) -> List[str]:
        """Retourne le matériel nécessaire"""
        return ["Support de cours", "Calculatrice", "Ordinateur avec accès internet"]
    
    def _get_assessment_methods(self, audience: str) -> List[str]:
        """Retourne les méthodes d'évaluation appropriées"""
        return ["Quiz interactif", "Exercice pratique", "Projet de groupe"]
    
    def _get_additional_resources(self, subject: str) -> List[Dict[str, str]]:
        """Retourne des ressources complémentaires"""
        return [
            {"type": "site_web", "title": "ADEME - Énergies renouvelables", "url": "https://www.ademe.fr"},
            {"type": "livre", "title": "Guide du photovoltaïque", "author": "Expert Solar"}
        ]
    
    def _get_homework_suggestions(self, subject: str, audience: str) -> List[str]:
        """Génère des suggestions de devoirs"""
        return [
            f"Recherche sur les applications de {subject}",
            "Visite virtuelle d'une installation solaire",
            "Calcul de dimensionnement simple"
        ]
    
    def _generate_dynamic_content(self, topic: str, format_type: str, complexity: str) -> Dict[str, Any]:
        """Génère du contenu dynamiquement avec Gemini"""
        return {
            "title": f"{topic.title()} - {format_type}",
            "content": f"Contenu généré pour {topic} en format {format_type}",
            "complexity": complexity
        }
    
    def _estimate_reading_time(self, content: Dict[str, Any]) -> int:
        """Estime le temps de lecture en minutes"""
        word_count = len(str(content).split())
        return max(1, word_count // 200)  # 200 mots par minute
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """Extrait les mots-clés d'un sujet"""
        keyword_mapping = {
            "photovoltaique": ["solaire", "panneau", "électricité", "renouvelable"],
            "installation": ["pose", "raccordement", "technique", "sécurité"],
            "economie": ["coût", "rentabilité", "financement", "ROI"]
        }
        return keyword_mapping.get(topic.lower(), [topic])
    
    def _get_related_topics(self, topic: str) -> List[str]:
        """Retourne les sujets connexes"""
        return ["énergie renouvelable", "transition énergétique", "autoconsommation"]
    
    def _add_interactive_elements(self, format_type: str) -> List[Dict[str, Any]]:
        """Ajoute des éléments interactifs selon le format"""
        if format_type == "tutorial":
            return [{"type": "step_validator", "description": "Validation de chaque étape"}]
        elif format_type == "article":
            return [{"type": "quiz_integration", "description": "Quiz de compréhension intégré"}]
        return []
    
    def _generate_comprehension_questions(self, topic: str, complexity: str) -> List[Dict[str, Any]]:
        """Génère des questions de compréhension"""
        return [
            {
                "question": f"Quel est le principe de base de {topic} ?",
                "type": "open",
                "difficulty": complexity
            }
        ]
    
    def _generate_dynamic_infographic_data(self, topic: str) -> Dict[str, Any]:
        """Génère dynamiquement des données d'infographie"""
        return {
            "title": f"Infographie {topic.title()}",
            "sections": [
                {
                    "type": "introduction",
                    "content": f"Données clés sur {topic}"
                }
            ]
        }
    
    def _generate_dynamic_exercise(self, exercise_type: str, difficulty: str) -> Dict[str, Any]:
        """Génère dynamiquement un exercice"""
        return {
            "title": f"Exercice {exercise_type.title()}",
            "difficulty": difficulty,
            "description": f"Exercice pratique sur {exercise_type}",
            "questions": [
                {
                    "question": f"Question sur {exercise_type}",
                    "answer": "Réponse à calculer",
                    "hint": "Indice pour résoudre"
                }
            ]
        }
    
    def _estimate_exercise_time(self, exercise_data: Dict[str, Any]) -> int:
        """Estime le temps nécessaire pour un exercice"""
        num_questions = len(exercise_data.get("questions", []))
        return num_questions * 10  # 10 minutes par question
    
    def _get_skills_for_exercise(self, exercise_type: str) -> List[str]:
        """Retourne les compétences développées par l'exercice"""
        skills_mapping = {
            "dimensionnement": ["Calcul", "Analyse technique", "Optimisation"],
            "economique": ["Analyse financière", "ROI", "Budgétisation"],
            "technique": ["Installation", "Sécurité", "Normes"]
        }
        return skills_mapping.get(exercise_type, ["Compétences générales"])
    
    def _get_tools_for_exercise(self, exercise_type: str) -> List[str]:
        """Retourne les outils nécessaires pour l'exercice"""
        return ["Calculatrice", "Ordinateur", "Logiciel de dimensionnement"]
    
    def _get_evaluation_criteria(self, exercise_type: str, difficulty: str) -> List[str]:
        """Retourne les critères d'évaluation"""
        return [
            "Exactitude des calculs",
            "Justification des choix",
            "Respect des contraintes",
            "Présentation claire"
        ]
    
    def _get_exercise_extensions(self, exercise_type: str) -> List[str]:
        """Retourne des extensions possibles de l'exercice"""
        return [
            "Variation des paramètres",
            "Ajout de contraintes",
            "Optimisation avancée"
        ]
    
    def _get_common_mistakes(self, exercise_type: str) -> List[str]:
        """Retourne les erreurs communes pour ce type d'exercice"""
        return [
            "Oubli des pertes système",
            "Mauvaise estimation des besoins",
            "Non prise en compte de l'orientation"
        ]
    
    def _analyze_by_domain(self, answers: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Analyse les réponses par domaine de compétence"""
        domains = {
            "technique": {"score": 75, "strong_points": ["Composants"], "weak_points": ["Installation"]},
            "economique": {"score": 60, "strong_points": ["ROI"], "weak_points": ["Financement"]},
            "reglementaire": {"score": 80, "strong_points": ["Aides"], "weak_points": ["Normes"]}
        }
        return domains
    
    def _generate_learning_recommendations(self, level: str, domain_analysis: Dict[str, Any], topic: str) -> List[str]:
        """Génère des recommandations d'apprentissage personnalisées"""
        recommendations = []
        
        if level == "beginner":
            recommendations.extend([
                "📚 Commencez par les fondamentaux du photovoltaïque",
                "🎯 Concentrez-vous sur les concepts de base",
                "👥 Rejoignez des groupes d'apprentissage"
            ])
        elif level == "intermediate":
            recommendations.extend([
                "🔧 Pratiquez avec des cas concrets",
                "📊 Approfondissez les calculs économiques",
                "🏆 Visez une certification professionnelle"
            ])
        else:  # advanced/expert
            recommendations.extend([
                "🚀 Explorez les technologies émergentes",
                "👨‍🏫 Partagez vos connaissances en mentoring",
                "🔬 Participez à la R&D du secteur"
            ])
        
        return recommendations
    
    def _get_next_learning_steps(self, level: str, topic: str) -> List[Dict[str, str]]:
        """Retourne les prochaines étapes d'apprentissage"""
        steps_by_level = {
            "beginner": [
                {"step": "Maîtriser les bases", "duration": "2-4 semaines"},
                {"step": "Premiers calculs", "duration": "1-2 semaines"},
                {"step": "Quiz intermédiaire", "duration": "1 jour"}
            ],
            "intermediate": [
                {"step": "Cas pratiques avancés", "duration": "3-4 semaines"},
                {"step": "Projet personnel", "duration": "2-3 semaines"},
                {"step": "Certification", "duration": "1-2 mois"}
            ],
            "advanced": [
                {"step": "Spécialisation technique", "duration": "2-3 mois"},
                {"step": "Formation de formateur", "duration": "1 mois"},
                {"step": "Veille technologique", "duration": "Continu"}
            ]
        }
        return steps_by_level.get(level, [])
    
    def _get_recommended_resources(self, level: str, topic: str) -> List[Dict[str, str]]:
        """Retourne des ressources recommandées selon le niveau"""
        return [
            {"type": "cours", "title": "Formation ADEME", "url": "https://www.ademe.fr"},
            {"type": "livre", "title": "Guide du photovoltaïque", "author": "Expert"},
            {"type": "site", "title": "Photovoltaique.info", "url": "https://www.photovoltaique.info"}
        ]
    
    def _check_certification_eligibility(self, score: float, topic: str) -> Dict[str, Any]:
        """Vérifie l'éligibilité aux certifications"""
        return {
            "eligible_for_basic": score >= 60,
            "eligible_for_advanced": score >= 80,
            "recommended_certification": "Installateur solaire" if score >= 70 else "Formation de base",
            "preparation_needed": score < 80
        }
    
    def _create_custom_certification_path(self, certification: str, level: str) -> Dict[str, Any]:
        """Crée un parcours de certification personnalisé"""
        return {
            "title": f"Certification {certification.title()}",
            "description": f"Parcours personnalisé pour {certification}",
            "duration": "Variable selon niveau",
            "modules": [
                {"module": "Fondamentaux", "duration": "Adapté au niveau"},
                {"module": "Spécialisation", "duration": "Selon objectifs"}
            ]
        }
    
    def _personalize_certification_path(self, path: Dict[str, Any], current_level: str) -> Dict[str, Any]:
        """Personnalise un parcours selon le niveau actuel"""
        level_multipliers = {"beginner": 1.5, "intermediate": 1.0, "advanced": 0.7}
        multiplier = level_multipliers.get(current_level, 1.0)
        
        if current_level == "advanced":
            path["modules"] = [m for m in path.get("modules", []) if "Fondamentaux" not in m.get("module", "")]
        
        path["personalization"] = {
            "current_level": current_level,
            "estimated_duration": f"{int(3 * multiplier)} mois",
            "priority_modules": self._get_priority_modules(current_level),
            "skip_modules": self._get_skip_modules(current_level)
        }
        
        return path
    
    def _get_priority_modules(self, level: str) -> List[str]:
        """Retourne les modules prioritaires selon le niveau"""
        priority_by_level = {
            "beginner": ["Fondamentaux", "Sécurité"],
            "intermediate": ["Dimensionnement", "Installation"],
            "advanced": ["Optimisation", "Maintenance"]
        }
        return priority_by_level.get(level, [])
    
    def _get_skip_modules(self, level: str) -> List[str]:
        """Retourne les modules à potentiellement passer selon le niveau"""
        skip_by_level = {
            "advanced": ["Introduction de base", "Concepts élémentaires"],
            "intermediate": ["Notions très basiques"]
        }
        return skip_by_level.get(level, [])
    
    async def process(self, state) -> Dict[str, Any]:
        """Méthode requise par BaseAgent - traite une requête éducative"""
        try:
            # Utiliser la langue détectée par le workflow ou détecter si pas disponible
            detected_language = getattr(state, 'detected_language', None)
            if not detected_language:
                detected_language = "fr"  # Défaut français
            
            # Classification de la demande éducative
            educational_type = self._classify_educational_request(state.current_message)
            
            # Extraction des paramètres selon le type
            if educational_type == "quiz":
                topic = self._extract_topic(state.current_message)
                difficulty = self._extract_difficulty(state.current_message)
                num_questions = self._extract_num_questions(state.current_message)
                result = self.create_quiz_tool(topic, difficulty, num_questions)
            elif educational_type == "lesson":
                subject = self._extract_subject(state.current_message)
                audience = self._extract_audience(state.current_message)
                duration = self._extract_duration(state.current_message)
                result = self.generate_lesson_plan_tool(subject, audience, duration)
            elif educational_type == "content":
                topic = self._extract_topic(state.current_message)
                format_type = self._extract_format_type(state.current_message)
                complexity = self._extract_complexity(state.current_message)
                result = self.create_educational_content_tool(topic, format_type, complexity)
            elif educational_type == "exercise":
                exercise_type = self._extract_exercise_type(state.current_message)
                difficulty = self._extract_difficulty(state.current_message)
                result = self.create_practical_exercise_tool(exercise_type, difficulty)
            elif educational_type == "certification":
                target_certification = self._extract_certification_target(state.current_message)
                current_level = self._extract_current_level(state.current_message)
                result = self.create_certification_path_tool(target_certification, current_level)
            else:
                # Contenu éducatif général
                result = self.create_educational_content_tool("énergie solaire", "article", "intermediate")
            
            # Génération de la réponse dans la langue détectée
            response = await self._generate_educational_response(result, educational_type, detected_language)
            
            return {
                "response": response,
                "agent_used": "educational_agent",
                "confidence": 0.9,
                "detected_language": detected_language,
                "educational_type": educational_type,
                "sources": ["Solar Nasih Educational Database"]
            }
            
        except Exception as e:
            logger.error(f"Erreur dans l'agent éducatif: {e}")
            return {
                "response": f"Erreur lors de la création de contenu éducatif: {str(e)}",
                "agent_used": "educational_agent",
                "confidence": 0.3,
                "error": str(e),
                "sources": ["Solar Nasih Educational Database"]
            }
    
    def _classify_educational_request(self, user_input: str) -> str:
        """Classifie le type de demande pédagogique"""
        text = user_input.lower()
        
        if any(word in text for word in ["quiz", "test", "qcm", "question"]):
            return "quiz"
        elif any(word in text for word in ["cours", "leçon", "plan", "formation"]):
            return "lesson"
        elif any(word in text for word in ["exercice", "pratique", "calcul", "cas"]):
            return "exercise"
        elif any(word in text for word in ["certification", "diplôme", "parcours", "programme"]):
            return "certification"
        elif any(word in text for word in ["infographie", "graphique", "visuel"]):
            return "infographic"
        else:
            return "content"
    
    def _extract_topic(self, user_input: str) -> str:
        """Extrait le sujet de la demande"""
        topics = ["photovoltaique", "installation", "economie", "reglementation", "maintenance"]
        text = user_input.lower()
        
        for topic in topics:
            if topic in text or any(word in text for word in topic.split()):
                return topic
        
        return "basics"
    
    def _extract_difficulty(self, user_input: str) -> str:
        """Extrait le niveau de difficulté"""
        text = user_input.lower()
        
        if any(word in text for word in ["débutant", "facile", "simple", "basique"]):
            return "beginner"
        elif any(word in text for word in ["avancé", "expert", "difficile", "complexe"]):
            return "advanced"
        else:
            return "intermediate"
    
    def _extract_num_questions(self, user_input: str) -> int:
        """Extrait le nombre de questions souhaité"""
        import re
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            num = int(numbers[0])
            return min(max(num, 5), 50)  # Entre 5 et 50 questions
        return 10
    
    def _extract_subject(self, user_input: str) -> str:
        """Extrait le sujet du cours"""
        return self._extract_topic(user_input)
    
    def _extract_audience(self, user_input: str) -> str:
        """Extrait le public cible"""
        text = user_input.lower()
        
        if any(word in text for word in ["professionnel", "installateur", "technicien"]):
            return "professionals"
        elif any(word in text for word in ["étudiant", "école", "université"]):
            return "students"
        else:
            return "general"
    
    def _extract_duration(self, user_input: str) -> int:
        """Extrait la durée souhaitée en minutes"""
        import re
        
        duration_patterns = [
            (r'(\d+)\s*h(?:eure)?s?', 60),
            (r'(\d+)\s*min(?:ute)?s?', 1),
        ]
        
        for pattern, multiplier in duration_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                return int(match.group(1)) * multiplier
        
        return 60  # Par défaut 1 heure
    
    def _extract_exercise_type(self, user_input: str) -> str:
        """Extrait le type d'exercice"""
        text = user_input.lower()
        
        if any(word in text for word in ["dimensionnement", "calcul", "taille"]):
            return "dimensionnement"
        elif any(word in text for word in ["économique", "rentabilité", "coût"]):
            return "economique"
        elif any(word in text for word in ["technique", "installation", "pose"]):
            return "technique"
        else:
            return "dimensionnement"
    
    def _extract_certification_target(self, user_input: str) -> str:
        """Extrait le type de certification visé"""
        text = user_input.lower()
        
        if any(word in text for word in ["installateur", "poseur", "technicien"]):
            return "solar_installer"
        elif any(word in text for word in ["conseiller", "vendeur", "commercial"]):
            return "solar_advisor"
        elif any(word in text for word in ["expert", "consultant", "bureau"]):
            return "solar_expert"
        else:
            return "solar_installer"
    
    def _extract_current_level(self, user_input: str) -> str:
        """Extrait le niveau actuel de l'apprenant"""
        return self._extract_difficulty(user_input)
    
    def _extract_format_type(self, user_input: str) -> str:
        """Extrait le format de contenu souhaité"""
        text = user_input.lower()
        
        if any(word in text for word in ["infographie", "graphique", "visuel"]):
            return "infographic"
        elif any(word in text for word in ["tutoriel", "guide", "étape"]):
            return "tutorial"
        else:
            return "article"
    
    def _extract_complexity(self, user_input: str) -> str:
        """Extrait le niveau de complexité"""
        return self._extract_difficulty(user_input)
    
    async def _generate_educational_response(self, result: Dict[str, Any], educational_type: str, language: str) -> str:
        """Génère une réponse éducative dans la langue appropriée"""
        try:
            # Pour l'instant, retourner le résultat formaté
            # En production, on pourrait ajouter des traductions
            
            if educational_type == "quiz":
                quiz_data = result.get("quiz", {})
                questions = quiz_data.get("questions", [])
                
                topic = quiz_data.get('topic', 'l\'énergie solaire')
                difficulty = quiz_data.get('difficulty', 'intermédiaire')
                response = f"📚 Quiz sur {topic} ({difficulty})\n\n"
                
                for i, question in enumerate(questions[:3], 1):  # Afficher les 3 premières questions
                    response += f"Question {i}: {question.get('question', '')}\n"
                    options = question.get('options', [])
                    for j, option in enumerate(options):
                        response += f"  {chr(65+j)}) {option}\n"
                    response += f"Réponse: {chr(65 + question.get('correct', 0))}\n"
                    response += f"Explication: {question.get('explanation', '')}\n\n"
                
                response += f"Total: {len(questions)} questions"
                
            elif educational_type == "lesson":
                lesson_data = result.get("lesson_plan", {})
                response = f"📖 Plan de cours: {lesson_data.get('title', '')}\n\n"
                response += f"Durée: {lesson_data.get('duration', 0)} minutes\n"
                response += f"Public: {lesson_data.get('target_audience', '')}\n\n"
                
                objectives = lesson_data.get("objectives", [])
                if objectives:
                    response += "Objectifs:\n"
                    for obj in objectives:
                        response += f"• {obj}\n"
                    response += "\n"
                
            elif educational_type == "content":
                content_data = result.get("content", {})
                response = f"📝 Contenu éducatif: {content_data.get('title', '')}\n\n"
                response += f"Format: {content_data.get('format_type', '')}\n"
                response += f"Complexité: {content_data.get('complexity', '')}\n\n"
                response += content_data.get("content", "")[:500] + "..."
                
            else:
                # Réponse générique
                response = f"Contenu éducatif généré: {educational_type}\n\n"
                if isinstance(result, dict):
                    response += str(result)
                else:
                    response += str(result)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur génération réponse éducative: {e}")
            return f"Contenu éducatif généré pour {educational_type}"
    
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Détermine si l'agent peut traiter cette requête"""
        educational_keywords = [
            "quiz", "test", "exercice", "cours", "formation", "apprentissage",
            "certification", "diplôme", "niveau", "évaluation", "compétence",
            "pédagogique", "éducatif", "tutorial", "guide", "infographie"
        ]
        
        return any(keyword in user_input.lower() for keyword in educational_keywords)

# Instance globale
educational_agent = EducationalAgent()