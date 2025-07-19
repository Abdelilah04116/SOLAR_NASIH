from typing import Dict, Any, List
from langchain.tools import Tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType, AgentState
from services.tavily_service import TavilyService
from services.gemini_service import GeminiService
import re

class TaskDividerAgent(BaseAgent):
    """
    Agent Diviseur de Tâches - Route les requêtes vers les agents appropriés
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.TASK_DIVIDER,
            description="Agent qui analyse et route les requêtes vers les agents spécialisés"
        )
        self.tavily_service = TavilyService()
        self.gemini_service = GeminiService()
        
        # Patterns de routage COMPLETS pour tous les agents
        self.route_patterns = {
            AgentType.RAG_SYSTEM: [
                r"qu'est-ce que", r"définition", r"expliquer", r"comment fonctionne",
                r"principe", r"théorie", r"concept", r"information sur", r"c'est quoi"
            ],
            AgentType.TECHNICAL_ADVISOR: [
                r"installation", r"technique", r"câblage", r"onduleur", r"panneau",
                r"dimensionnement", r"problème technique", r"maintenance", r"diagnostic",
                r"schéma", r"protection", r"fusible", r"disjoncteur"
            ],
            AgentType.ENERGY_SIMULATOR: [
                r"simulation", r"calculer", r"estimation", r"production", r"économie",
                r"rentabilité", r"amortissement", r"rendement", r"kwh", r"kwc",
                r"retour sur investissement", r"roi", r"payback"
            ],
            AgentType.REGULATORY_ASSISTANT: [
                r"réglementation", r"loi", r"norme", r"obligation", r"conformité",
                r"permis", r"autorisation", r"législation", r"code", r"arrêté",
                r"nf c 15-100", r"consuel", r"enedis"
            ],
            AgentType.COMMERCIAL_ASSISTANT: [
                r"prix", r"coût", r"devis", r"tarif", r"financement", r"crédit",
                r"subvention", r"aide", r"prêt", r"budget", r"offre", r"taux"
            ],
            AgentType.CERTIFICATION_ASSISTANT: [
                r"certification", r"rge", r"qualibat", r"label", r"formation",
                r"qualification", r"agrément", r"habilitation", r"recyclage"
            ],
            AgentType.DOCUMENT_GENERATOR: [
                r"générer", r"créer document", r"rapport", r"contrat", r"facture",
                r"attestation", r"certificat", r"devis détaillé", r"pdf"
            ],
            AgentType.EDUCATIONAL_AGENT: [
                r"apprendre", r"cours", r"formation", r"tutoriel", r"guide",
                r"étape par étape", r"explication simple", r"comprendre",
                r"niveau débutant", r"quiz", r"exercice"
            ],
            AgentType.VOICE_PROCESSOR: [
                r"vocal", r"audio", r"parler", r"écouter", r"micro",
                r"transcription", r"synthèse vocale"
            ],
            AgentType.MULTILINGUAL_DETECTOR: [
                r"english", r"español", r"deutsch", r"italiano",
                r"translate", r"traduction", r"langue"
            ],
            AgentType.DOCUMENT_INDEXER: [
                r"indexer", r"ajouter document", r"upload", r"intégrer",
                r"base documentaire", r"catalogue"
            ]
    }

    
    def _init_tools(self) -> List[Tool]:
        """Initialise les outils du diviseur de tâches"""
        return [
            Tool(
                name="analyze_intent",
                description="Analyse l'intention de l'utilisateur",
                func=self._analyze_intent
            ),
            Tool(
                name="route_to_agent",
                description="Route vers l'agent approprié",
                func=self._route_to_agent
            ),
            Tool(
                name="search_context",
                description="Recherche du contexte supplémentaire",
                func=self._search_context
            )
        ]
    
    def _get_system_prompt(self) -> str:
        """Prompt système pour le diviseur de tâches"""
        return """
        Tu es l'Agent Diviseur de Tâches du système Solar Nasih.
        
        Ton rôle est d'analyser les requêtes utilisateur et de les router vers l'agent approprié :
        
        1. **RAG_SYSTEM** : Questions informatives, définitions, explications générales
        2. **TECHNICAL_ADVISOR** : Questions techniques, installation, maintenance
        3. **ENERGY_SIMULATOR** : Simulations, calculs, estimations énergétiques
        4. **REGULATORY_ASSISTANT** : Réglementation, normes, obligations légales
        5. **COMMERCIAL_ASSISTANT** : Prix, devis, financement, aides
        6. **CERTIFICATION_ASSISTANT** : Certifications, formations, qualifications
        7. **DOCUMENT_GENERATOR** : Génération de documents, rapports
        8. **EDUCATIONAL_AGENT** : Apprentissage, formation, tutoriels
        
        Analyse la requête et détermine l'agent le plus approprié.
        Si plusieurs agents peuvent traiter la requête, choisis le plus spécialisé.
        
        Réponds en français et sois précis dans ton analyse.
        """
    
    def _analyze_intent(self, query: str) -> str:
        """Analyse l'intention de l'utilisateur"""
        query_lower = query.lower()
        
        # Détection des intentions principales
        intentions = []
        
        if any(word in query_lower for word in ["simulation", "calcul", "estimation"]):
            intentions.append("simulation_energetique")
        
        if any(word in query_lower for word in ["installation", "technique", "câblage"]):
            intentions.append("conseil_technique")
        
        if any(word in query_lower for word in ["prix", "coût", "financement"]):
            intentions.append("assistance_commerciale")
        
        if any(word in query_lower for word in ["réglementation", "norme", "loi"]):
            intentions.append("assistance_reglementaire")
        
        if any(word in query_lower for word in ["qu'est-ce que", "définition", "expliquer"]):
            intentions.append("information_generale")
        
        return f"Intentions détectées: {', '.join(intentions) if intentions else 'generale'}"
    
    def _route_to_agent(self, query: str) -> str:
        """Route la requête vers l'agent approprié"""
        query_lower = query.lower()
        
        # Scores pour chaque agent
        agent_scores = {}
        
        for agent_type, patterns in self.route_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            agent_scores[agent_type] = score
        
        # Agent avec le score le plus élevé
        best_agent = max(agent_scores, key=agent_scores.get)
        
        # Si aucun pattern ne correspond, utiliser le RAG par défaut
        if agent_scores[best_agent] == 0:
            best_agent = AgentType.RAG_SYSTEM
        
        return f"Agent recommandé: {best_agent.value}"
    
    def _search_context(self, query: str) -> str:
        """Recherche du contexte supplémentaire avec Tavily"""
        try:
            # Recherche avec Tavily pour enrichir le contexte
            results = self.tavily_service.search(f"énergie solaire {query}")
            
            if results:
                context = "Contexte supplémentaire trouvé:\n"
                for result in results[:2]:  # Limiter à 2 résultats
                    context += f"- {result.get('title', '')}: {result.get('content', '')[:100]}...\n"
                return context
            else:
                return "Aucun contexte supplémentaire trouvé"
                
        except Exception as e:
            return f"Erreur lors de la recherche de contexte: {str(e)}"
    
    async def route_request(self, state: AgentState) -> AgentType:
        """
        Route la requête vers l'agent approprié
        """
        try:
            # Analyse de l'intention
            intent_analysis = self._analyze_intent(state.current_message)
            
            # Routage vers l'agent
            agent_recommendation = self._route_to_agent(state.current_message)
            
            # Extraction du type d'agent recommandé
            agent_name = agent_recommendation.split(": ")[1]
            
            # Mise à jour de l'état
            state.user_intent = intent_analysis
            state.agent_route = AgentType(agent_name)
            
            return AgentType(agent_name)
            
        except Exception as e:
            # En cas d'erreur, router vers le RAG par défaut
            return AgentType.RAG_SYSTEM
    
    async def process(self, state: AgentState, agents_map: dict) -> dict:
        """
        Analyse la requête, détecte les intentions multiples, route vers les agents pertinents,
        et construit une réponse utilisateur expliquant la division des tâches et agrégeant les réponses.
        Si aucun agent ne peut répondre, utilise Gemini (LLM) pour générer une réponse intelligente.
        """
        from models.schemas import AgentState as AgentStateObj
        query_lower = state.current_message.lower() if hasattr(state, 'current_message') else state.get('current_message', '').lower()
        detected_agents = set()
        explanations = []
        for agent_type, patterns in self.route_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    detected_agents.add(agent_type)
                    explanations.append(f"Mot-clé '{pattern}' → {agent_type.value}")
                    break
        if not detected_agents:
            detected_agents.add(AgentType.RAG_SYSTEM)
            explanations.append("Aucun mot-clé spécifique détecté, routage vers RAG_SYSTEM (connaissances générales)")
        responses = []
        sources = set()
        confidences = []
        agent_answered = False
        for agent_type in detected_agents:
            agent = agents_map.get(agent_type)
            if agent:
                try:
                    # Conversion dict -> AgentState si besoin
                    agent_state = state
                    if isinstance(state, dict):
                        agent_state = AgentStateObj(**state)
                    result = await agent.process(agent_state, agents_map) if agent_type == AgentType.TASK_DIVIDER else await agent.process(agent_state)
                    resp = result.get("response", "")
                    if resp and not resp.lower().startswith("solar nasih est un assistant"):
                        responses.append(f"Réponse de {agent_type.value} : {resp}")
                        agent_answered = True
                    if "sources" in result:
                        sources.update(result["sources"])
                    if "confidence" in result:
                        confidences.append(result["confidence"])
                except Exception as e:
                    responses.append(f"Erreur lors de l'appel à l'agent {agent_type.value} : {str(e)}")
            else:
                responses.append(f"Aucun agent {agent_type.value} disponible.")
        if not agent_answered:
            gemini_resp = await self.gemini_service.generate_response(state.current_message if hasattr(state, 'current_message') else state.get('current_message', ''))
            responses.append(f"Réponse générée par l'IA Gemini : {gemini_resp}")
            sources.add("Gemini LLM fallback")
            confidences.append(0.7)
        if responses:
            response_text = "\n\n".join(responses)
        else:
            response_text = "Solar Nasih est un assistant intelligent dédié à l'énergie solaire. Posez-moi vos questions sur l'installation, la réglementation, la simulation, la certification ou le financement."
        routing_explanation = "Division des tâches :\n" + "\n".join(explanations)
        final_response = f"{routing_explanation}\n\n{response_text}"
        return {
            "response": final_response,
            "confidence": float(sum(confidences)) / len(confidences) if confidences else 0.7,
            "sources": list(sources) if sources else ["Gemini LLM fallback"]
        }
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        """Le diviseur de tâches peut toujours traiter les requêtes"""
        return 1.0