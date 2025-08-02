from typing import Dict, Any, List
from langchain.tools import Tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType
from services.tavily_service import TavilyService
import json

class TechnicalAdvisorAgent(BaseAgent):
    """
    Agent Conseiller Technique - Expertise technique en installation solaire
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.TECHNICAL_ADVISOR,
            description="Expert technique en installation photovoltaïque"
        )
        self.tavily_service = TavilyService()
        
        # Base de connaissances techniques
        self.technical_knowledge = {
            "onduleurs": {
                "types": ["string", "micro-onduleurs", "optimiseurs"],
                "criteres_choix": ["puissance", "rendement", "garantie", "monitoring"],
                "marques_recommandees": ["SMA", "Fronius", "Enphase", "SolarEdge"]
            },
            "panneaux": {
                "technologies": ["monocristallin", "polycristallin", "amorphe"],
                "puissances": ["300W", "400W", "500W", "600W+"],
                "criteres": ["rendement", "coefficient_temperature", "garantie"]
            },
            "cablage": {
                "sections": ["4mm²", "6mm²", "10mm²"],
                "types": ["DC", "AC"],
                "protections": ["fusibles", "disjoncteurs", "parafoudre"]
            }
        }
    
    def _init_tools(self) -> List[Tool]:
        """Initialise les outils du conseiller technique"""
        return [
            Tool(
                name="analyze_technical_problem",
                description="Analyse un problème technique",
                func=self._analyze_technical_problem
            ),
            Tool(
                name="recommend_equipment",
                description="Recommande des équipements",
                func=self._recommend_equipment
            ),
            Tool(
                name="calculate_sizing",
                description="Calcule le dimensionnement",
                func=self._calculate_sizing
            ),
            Tool(
                name="search_technical_info",
                description="Recherche d'informations techniques",
                func=self._search_technical_info
            ),
            Tool(
                name="troubleshoot",
                description="Aide au diagnostic de pannes",
                func=self._troubleshoot
            )
        ]
    
    def _get_system_prompt(self) -> str:
        """Prompt système pour le conseiller technique"""
        return """
        Tu es l'Agent Conseiller Technique du système Solar Nasih.
        
        Tu es un expert en installation photovoltaïque avec une expertise approfondie sur :
        
        **Domaines d'expertise :**
        - Dimensionnement d'installations photovoltaïques
        - Choix et configuration d'onduleurs
        - Sélection de panneaux solaires
        - Schémas de câblage et protections électriques
        - Diagnostic de pannes et maintenance
        - Optimisation de performance
        - Intégration réseau et monitoring
        
        **Ton approche :**
        1. Analyse technique rigoureuse
        2. Recommandations basées sur les normes (NF C 15-100, IEC 61215)
        3. Prise en compte des contraintes budgétaires
        4. Solutions pratiques et réalisables
        5. Respect des règles de sécurité
        
        Réponds toujours en français avec des explications claires et des recommandations concrètes.
        Utilise ta base de connaissances et les outils à disposition.
        """
    
    def _analyze_technical_problem(self, problem_description: str) -> str:
        """Analyse un problème technique"""
        problem_lower = problem_description.lower()
        
        # Catégorisation du problème
        if "onduleur" in problem_lower:
            return self._analyze_inverter_problem(problem_description)
        elif "panneau" in problem_lower or "module" in problem_lower:
            return self._analyze_panel_problem(problem_description)
        elif "production" in problem_lower or "rendement" in problem_lower:
            return self._analyze_performance_problem(problem_description)
        elif "câblage" in problem_lower or "câble" in problem_lower:
            return self._analyze_wiring_problem(problem_description)
        else:
            return "Problème technique général détecté. Analyse en cours..."
    
    def _analyze_inverter_problem(self, description: str) -> str:
        """Analyse spécifique aux onduleurs"""
        common_issues = {
            "erreur": "Vérifier les codes d'erreur dans la documentation",
            "surchauffe": "Contrôler la ventilation et la température ambiante",
            "déconnexion": "Vérifier les connexions DC et AC",
            "rendement": "Analyser les courbes de performance"
        }
        
        for issue, solution in common_issues.items():
            if issue in description.lower():
                return f"Problème d'onduleur détecté: {issue}. Solution: {solution}"
        
        return "Problème d'onduleur nécessitant une analyse approfondie"
    
    def _analyze_panel_problem(self, description: str) -> str:
        """Analyse spécifique aux panneaux"""
        return "Analyse des panneaux solaires en cours..."
    
    def _analyze_performance_problem(self, description: str) -> str:
        """Analyse des problèmes de performance"""
        return "Analyse de performance en cours..."
    
    def _analyze_wiring_problem(self, description: str) -> str:
        """Analyse des problèmes de câblage"""
        return "Analyse du câblage en cours..."
    
    def _recommend_equipment(self, requirements: str) -> str:
        """Recommande des équipements selon les besoins"""
        requirements_lower = requirements.lower()
        
        recommendations = []
        
        if "onduleur" in requirements_lower:
            recommendations.append("Onduleurs recommandés:")
            recommendations.append("- SMA Sunny Boy (résidentiel)")
            recommendations.append("- Fronius Symo (commercial)")
            recommendations.append("- Enphase IQ7+ (micro-onduleurs)")
        
        if "panneau" in requirements_lower:
            recommendations.append("Panneaux recommandés:")
            recommendations.append("- Monocristallins 400W+ (haute performance)")
            recommendations.append("- Polycristallins 300W (économique)")
            recommendations.append("- Bifaciaux (gains supplémentaires)")
        
        return "\n".join(recommendations) if recommendations else "Spécifiez vos besoins pour des recommandations précises"
    
    def _calculate_sizing(self, parameters: str) -> str:
        """Calcule le dimensionnement de l'installation"""
        try:
            # Extraction des paramètres (simulation simple)
            if "puissance" in parameters.lower():
                return "Calcul de dimensionnement:\n- Puissance crête recommandée: 6 kWc\n- Nombre de panneaux: 15 x 400W\n- Onduleur: 6 kW"
            else:
                return "Paramètres insuffisants pour le dimensionnement"
        except Exception as e:
            return f"Erreur dans le calcul: {str(e)}"
    
    def _search_technical_info(self, query: str) -> str:
        """Recherche d'informations techniques via Tavily"""
        try:
            results = self.tavily_service.search(f"installation photovoltaïque {query}")
            
            if results:
                info = "Informations techniques trouvées:\n"
                for result in results[:3]:
                    info += f"- {result.get('title', '')}\n"
                return info
            else:
                return "Aucune information technique trouvée"
                
        except Exception as e:
            return f"Erreur lors de la recherche: {str(e)}"
    
    def _troubleshoot(self, issue: str) -> str:
        """Aide au diagnostic de pannes"""
        issue_lower = issue.lower()
        
        troubleshooting_guide = {
            "pas de production": [
                "1. Vérifier l'onduleur (voyants, écran)",
                "2. Contrôler les fusibles et disjoncteurs",
                "3. Vérifier les connexions DC",
                "4. Tester la continuité des câbles"
            ],
            "production faible": [
                "1. Vérifier l'ombrage sur les panneaux",
                "2. Nettoyer les panneaux si nécessaire",
                "3. Contrôler les connexions",
                "4. Analyser les données de monitoring"
            ],
            "erreur onduleur": [
                "1. Noter le code d'erreur",
                "2. Consulter la documentation",
                "3. Vérifier les paramètres réseau",
                "4. Redémarrer l'onduleur si nécessaire"
            ]
        }
        
        for problem, steps in troubleshooting_guide.items():
            if problem in issue_lower:
                return f"Diagnostic pour '{problem}':\n" + "\n".join(steps)
        
        return "Décrivez plus précisément le problème pour un diagnostic ciblé"
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        """Évalue si l'agent peut traiter la requête technique"""
        technical_keywords = [
            "installation", "onduleur", "panneau", "câblage", "dimensionnement",
            "maintenance", "panne", "technique", "schéma", "protection",
            "rendement", "performance", "diagnostic", "réparation"
        ]
        
        user_input_lower = user_input.lower()
        matches = sum(1 for keyword in technical_keywords if keyword in user_input_lower)
        
        return min(matches * 0.2, 1.0)  # Score basé sur les mots-clés techniques