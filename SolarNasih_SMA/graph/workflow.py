from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolExecutor, ToolInvocation
from graph.state import SolarNasihState, create_initial_state, update_state_with_agent_result
from graph.nodes import *
from models.schemas import AgentType
import logging

logger = logging.getLogger(__name__)

class SolarNasihWorkflow:
    _instance = None
    """
    Workflow principal du système multi-agent Solar Nasih
    """
    
    def __init__(self):
        SolarNasihWorkflow._instance = self
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
        
        # Initialisation des agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialise tous les agents du système"""
        try:
            from agents.task_divider import TaskDividerAgent
            from agents.technical_advisor import TechnicalAdvisorAgent
            from agents.energy_simulator import EnergySimulatorAgent
            from agents.voice_processor import VoiceProcessorAgent
            from agents.multilingual_detector import MultilingualDetectorAgent
            from agents.regulatory_assistant import RegulatoryAssistantAgent
            from agents.educational_agent import EducationalAgent
            from agents.commercial_assistant import CommercialAssistantAgent
            from agents.certification_assistant import CertificationAssistantAgent
            from agents.document_generator import DocumentGeneratorAgent
            from agents.document_indexer import DocumentIndexerAgent
            self.agents = {
                AgentType.TASK_DIVIDER: TaskDividerAgent(),
                AgentType.TECHNICAL_ADVISOR: TechnicalAdvisorAgent(),
                AgentType.ENERGY_SIMULATOR: EnergySimulatorAgent(),
                AgentType.VOICE_PROCESSOR: VoiceProcessorAgent(),
                AgentType.MULTILINGUAL_DETECTOR: MultilingualDetectorAgent(),
                AgentType.REGULATORY_ASSISTANT: RegulatoryAssistantAgent(),
                AgentType.EDUCATIONAL_AGENT: EducationalAgent(),
                AgentType.COMMERCIAL_ASSISTANT: CommercialAssistantAgent(),
                AgentType.CERTIFICATION_ASSISTANT: CertificationAssistantAgent(),
                AgentType.DOCUMENT_GENERATOR: DocumentGeneratorAgent(),
                AgentType.DOCUMENT_INDEXER: DocumentIndexerAgent()
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des agents: {e}")
            raise
    
    def _build_graph(self) -> StateGraph:
        """
        Construit le graphe LangGraph du workflow
        
        Returns:
            Graphe configuré
        """
        
        # Création du graphe
        graph = StateGraph(SolarNasihState)
    
    # Ajout de TOUS les nœuds
        graph.add_node("language_detection", language_detection_node)
        graph.add_node("task_division", task_division_node)
        
        # Nœuds de traitement spécialisés
        graph.add_node("rag_processing", rag_processing_node)
        graph.add_node("technical_processing", technical_processing_node)
        graph.add_node("simulation_processing", simulation_processing_node)
        graph.add_node("regulatory_processing", regulatory_processing_node)
        graph.add_node("commercial_processing", commercial_processing_node)
        graph.add_node("educational_processing", educational_processing_node)
        graph.add_node("certification_processing", certification_processing_node)
        graph.add_node("document_generation", document_generation_node)
        graph.add_node("voice_processing", voice_processing_node)
        graph.add_node("multilingual_processing", multilingual_processing_node)
        graph.add_node("document_indexing", document_indexer_node)

        # Nœud final
        graph.add_node("response_formatting", response_formatting_node)
    
        # Point d'entrée
        graph.set_entry_point("language_detection")
        
        # Transitions depuis la détection de langue
        graph.add_edge("language_detection", "task_division")
        
        # Transitions depuis la division de tâches
        graph.add_conditional_edges(
            "task_division",
            self._route_decision,
            {
                AgentType.RAG_SYSTEM: "rag_processing",
                AgentType.TECHNICAL_ADVISOR: "technical_processing",
                AgentType.ENERGY_SIMULATOR: "simulation_processing",
                AgentType.REGULATORY_ASSISTANT: "regulatory_processing",
                AgentType.COMMERCIAL_ASSISTANT: "commercial_processing",
                AgentType.EDUCATIONAL_AGENT: "educational_processing",
                AgentType.CERTIFICATION_ASSISTANT: "certification_processing",
                AgentType.DOCUMENT_GENERATOR: "document_generation",
                AgentType.VOICE_PROCESSOR: "voice_processing",
                AgentType.MULTILINGUAL_DETECTOR: "multilingual_processing",
                AgentType.DOCUMENT_INDEXER: "document_indexing"
           }
        )
        
        # Transitions vers le formatage de réponse
        graph.add_edge("rag_processing", "response_formatting")
        graph.add_edge("technical_processing", "response_formatting")
        graph.add_edge("simulation_processing", "response_formatting")
        graph.add_edge("regulatory_processing", "response_formatting")
        graph.add_edge("commercial_processing", "response_formatting")
        graph.add_edge("educational_processing", "response_formatting")
        graph.add_edge("certification_processing", "response_formatting")
        graph.add_edge("document_generation", "response_formatting")
        graph.add_edge("voice_processing", "response_formatting")
        graph.add_edge("multilingual_processing", "response_formatting")
        graph.add_edge("document_indexing", "response_formatting")
    
        # Fin du workflow
        graph.add_edge("response_formatting", END)
        
        return graph
    
    def _route_decision(self, state: SolarNasihState) -> AgentType:
        """
        Décide du routage basé sur l'état actuel
        
        Args:
            state: État actuel du système
            
        Returns:
            Type d'agent vers lequel router
        """
        
        agent_route = state.get("agent_route", AgentType.TASK_DIVIDER)
        
        # Si agent_route est déjà un AgentType, le retourner directement
        if isinstance(agent_route, AgentType):
            return agent_route
        
        # Si c'est une string, essayer de la convertir en AgentType
        if isinstance(agent_route, str):
            try:
                return AgentType(agent_route)
            except ValueError:
                # Si la conversion échoue, retourner TASK_DIVIDER par défaut
                logger.warning(f"Agent route invalide: {agent_route}, utilisation de TASK_DIVIDER par défaut")
                return AgentType.TASK_DIVIDER
        
        # Si c'est un autre type, retourner TASK_DIVIDER par défaut
        logger.warning(f"Type d'agent route inattendu: {type(agent_route)}, utilisation de TASK_DIVIDER par défaut")
        return AgentType.TASK_DIVIDER
    
    async def run(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Exécute le workflow principal
        
        Args:
            message: Message utilisateur
            context: Contexte optionnel
            
        Returns:
            Résultat du traitement
        """
        
        try:
            # Création de l'état initial
            initial_state = create_initial_state(message, context)
            
            # Exécution du graphe
            result = await self.compiled_graph.ainvoke(initial_state)
            
            # Formatage du résultat
            return self._format_final_result(result)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du workflow: {e}")
            return {
                "response": f"Erreur lors du traitement: {str(e)}",
                "agent_used": "task_divider",
                "confidence": 0.0,
                "sources": [],
                "error": str(e)
            }
    
    async def run_voice_processing(self, audio_file) -> Dict[str, Any]:
        """
        Traitement spécialisé pour les requêtes vocales
        
        Args:
            audio_file: Fichier audio à traiter
            
        Returns:
            Résultat du traitement vocal
        """
        
        try:
            # Création d'un état spécialisé pour le vocal
            initial_state = create_initial_state("", {})
            initial_state["voice_data"] = {"audio_file": audio_file}
            initial_state["agent_route"] = AgentType.VOICE_PROCESSOR
            
            # Exécution directe du nœud vocal
            result = await voice_processing_node(initial_state)
            
            return self._format_final_result(result)
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement vocal: {e}")
            return {
                "error": str(e),
                "transcribed_text": "",
                "response": "Erreur lors du traitement vocal"
            }
    
    async def run_energy_simulation(self, simulation_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulation énergétique directe
        
        Args:
            simulation_params: Paramètres de simulation
            
        Returns:
            Résultat de la simulation
        """
        
        try:
            # Création d'un état spécialisé pour la simulation
            initial_state = create_initial_state("", {})
            initial_state["simulation_params"] = simulation_params
            initial_state["agent_route"] = AgentType.ENERGY_SIMULATOR
            
            # Exécution directe du nœud de simulation
            result = await simulation_processing_node(initial_state)
            
            return self._format_final_result(result)
            
        except Exception as e:
            logger.error(f"Erreur lors de la simulation: {e}")
            return {
                "error": str(e),
                "simulation_result": None
            }
    
    async def run_document_generation(self, doc_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génération de documents directe
        
        Args:
            doc_params: Paramètres de génération
            
        Returns:
            Résultat de la génération
        """
        
        try:
            # Création d'un état spécialisé pour la génération
            initial_state = create_initial_state("", {})
            initial_state["document_context"] = doc_params
            initial_state["agent_route"] = AgentType.DOCUMENT_GENERATOR
            
            # Exécution directe du nœud de génération
            result = await document_generation_node(initial_state)
            
            return self._format_final_result(result)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            return {
                "error": str(e),
                "document_url": None
            }
    
    def _format_final_result(self, state: SolarNasihState) -> Dict[str, Any]:
        """
        Formate le résultat final du workflow
        """
        try:
            agent_route = state.get("agent_route", AgentType.TASK_DIVIDER)
            if isinstance(agent_route, AgentType):
                agent_route_val = agent_route.value
            else:
                agent_route_val = str(agent_route)
            
            # Récupération de la réponse
            response = state.get("response", "")
            if not response and state.get("errors"):
                response = f"Erreur lors du traitement: {', '.join(state['errors'])}"
            
            return {
                "response": response,
                "agent_used": agent_route_val,
                "confidence": state.get("confidence_score", 0.0),
                "sources": state.get("sources", []),
                "processing_steps": state.get("processing_steps", []),
                "detected_language": state.get("detected_language", "fr"),
                "user_intent": state.get("user_intent", ""),
                "errors": state.get("errors", []),
                "debug_info": state.get("debug_info", {})
            }
        except Exception as e:
            logger.error(f"Erreur dans _format_final_result: {e}")
            return {
                "response": f"Erreur lors du formatage de la réponse: {str(e)}",
                "agent_used": "task_divider",
                "confidence": 0.0,
                "sources": [],
                "processing_steps": [],
                "detected_language": "fr",
                "user_intent": "",
                "errors": [str(e)],
                "debug_info": {}
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Retourne le statut du workflow
        
        Returns:
            Informations sur le statut
        """
        
        return {
            "workflow_compiled": self.compiled_graph is not None,
            "agents_loaded": len(self.agents),
            "available_agents": list(self.agents.keys()),
            "graph_nodes": len(self.graph.nodes) if hasattr(self.graph, 'nodes') else 0
        }