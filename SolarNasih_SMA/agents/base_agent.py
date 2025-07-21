from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain.schema import BaseMessage
from services.gemini_service import GeminiService
from models.schemas import AgentState, AgentType
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Classe de base pour tous les agents du système Solar Nasih
    """
    
    def __init__(self, agent_type: AgentType, description: str):
        self.agent_type = agent_type
        self.description = description
        self.gemini_service = GeminiService()
        self.tools = self._init_tools()
        self.executor = self._init_executor()
        
    @abstractmethod
    def _init_tools(self) -> List[Tool]:
        """Initialise les outils spécifiques à l'agent"""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Retourne le prompt système spécifique à l'agent"""
        pass
    
    def _init_executor(self) -> AgentExecutor:
        """Initialise l'exécuteur d'agent avec LangChain"""
        try:
            # Configuration basique avec Gemini
            llm = self.gemini_service.get_llm()
            
            # Création d'un agent simple pour cette implémentation
            from langchain.agents import create_react_agent
            from langchain.prompts import PromptTemplate
            
            prompt = PromptTemplate.from_template(
                self._get_system_prompt() +
                "\n\nOutils disponibles :\n{tools}\n\n" +
                "Question: {input}\n" +
                "Noms des outils : {tool_names}\n" +
                "Raisonnement: {agent_scratchpad}"
            )
            
            agent = create_react_agent(llm, self.tools, prompt)
            return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de l'agent {self.agent_type}: {e}")
            raise
    
    async def process(self, state: AgentState) -> Dict[str, Any]:
        """
        Traite une requête et retourne le résultat
        """
        try:
            # Préparation du contexte
            context = self._prepare_context(state)
            
            # Exécution de l'agent avec gestion des erreurs de parsing
            try:
                result = await self.executor.ainvoke({
                    "input": state.current_message,
                    "context": context
                })
                
                # Traitement du résultat
                return self._process_result(result, state)
                
            except Exception as parsing_error:
                # En cas d'erreur de parsing, on utilise une approche directe
                logger.warning(f"Erreur de parsing dans l'agent {self.agent_type}, utilisation de l'approche directe: {parsing_error}")
                
                # Appel direct au LLM sans parser
                llm = self.gemini_service.get_llm()
                prompt = self._get_system_prompt() + f"\n\nQuestion de l'utilisateur: {state.current_message}\n\nRéponds directement à la question en français de manière claire et détaillée."
                
                direct_response = await llm.ainvoke(prompt)
                
                return {
                    "response": direct_response.content if hasattr(direct_response, 'content') else str(direct_response),
                    "confidence": 0.7,  # Confiance réduite car pas d'outils utilisés
                    "sources": [],
                    "agent_used": self.agent_type
                }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement par l'agent {self.agent_type}: {e}")
            return {
                "response": f"Erreur lors du traitement: {str(e)}",
                "confidence": 0.0,
                "sources": []
            }
    
    def _prepare_context(self, state: AgentState) -> Dict[str, Any]:
        """Prépare le contexte pour l'agent"""
        return {
            "language": state.detected_language,
            "user_intent": state.user_intent,
            "conversation_history": state.processing_history,
            "agent_context": state.context.get(self.agent_type.value, {})
        }
    
    def _process_result(self, result: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """Traite le résultat de l'agent"""
        return {
            "response": result.get("output", ""),
            "confidence": self._calculate_confidence(result),
            "sources": self._extract_sources(result),
            "agent_used": self.agent_type
        }
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calcule le niveau de confiance de la réponse"""
        # Logique simple de calcul de confiance
        output_length = len(result.get("output", ""))
        if output_length > 100:
            return 0.8
        elif output_length > 50:
            return 0.6
        else:
            return 0.4
    
    def _extract_sources(self, result: Dict[str, Any]) -> List[str]:
        """Extrait les sources utilisées"""
        # À implémenter selon les besoins spécifiques
        return []
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        """
        Détermine si l'agent peut traiter la requête
        Retourne un score de confiance entre 0 et 1
        """
        # Logique de base - à surcharger dans les agents spécialisés
        return 0.5