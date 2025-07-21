from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages
from models.schemas import AgentType


class SolarNasihState(TypedDict):
    """
    État partagé du système multi-agent Solar Nasih
    """
    
    # Message et conversation
    messages: Annotated[List[Dict[str, str]], add_messages]
    current_message: str
    response: str
    
    # Détection et routage
    detected_language: str
    user_intent: str
    confidence_score: float
    agent_route: AgentType
    
    # Contexte utilisateur
    user_context: Dict[str, Any]
    session_context: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    
    # Résultats et métadonnées
    agent_results: Dict[str, Any]
    sources: List[str]
    processing_steps: List[str]
    
    # États spécialisés
    voice_data: Optional[Dict[str, Any]]
    simulation_params: Optional[Dict[str, Any]]
    document_context: Optional[Dict[str, Any]]
    
    # Erreurs et logging
    errors: List[str]
    debug_info: Dict[str, Any]

def create_initial_state(message: str, context: Dict[str, Any] = None) -> SolarNasihState:
    """
    Crée l'état initial du système
    
    Args:
        message: Message utilisateur initial
        context: Contexte optionnel
        
    Returns:
        État initial configuré
    """
    
    return SolarNasihState(
        messages=[{"role": "user", "content": message}],
        current_message=message,
        response="",
        
        detected_language="fr",
        user_intent="",
        confidence_score=0.0,
        agent_route=AgentType.TASK_DIVIDER,
        
        user_context=context or {},
        session_context={},
        conversation_history=[],
        
        agent_results={},
        sources=[],
        processing_steps=[],
        
        voice_data=None,
        simulation_params=None,
        document_context=None,
        
        errors=[],
        debug_info={}
    )

def update_state_with_agent_result(
    state: SolarNasihState, 
    agent_type: AgentType, 
    result: Dict[str, Any]
) -> SolarNasihState:
    """
    Met à jour l'état avec le résultat d'un agent
    """
    # Mise à jour des résultats
    state["agent_results"][agent_type.value] = result
    
    # Mise à jour de la réponse si fournie
    if "response" in result:
        resp = result["response"]
        # Vérifier que la réponse est une chaîne de caractères valide
        if isinstance(resp, str) and resp.strip():
            state["response"] = resp
        elif isinstance(resp, AgentType):
            # Si c'est un AgentType, on garde la réponse précédente ou on met un message par défaut
            if not state.get("response") or not state["response"].strip():
                state["response"] = "Solar Nasih est un assistant intelligent dédié à l'énergie solaire. Posez-moi vos questions sur l'installation, la réglementation, la simulation, la certification ou le financement."
        else:
            # Pour les autres types, on convertit en string
            state["response"] = str(resp) if resp else ""
    
    # Mise à jour de la confiance
    if "confidence" in result:
        state["confidence_score"] = result["confidence"]
    
    # Mise à jour des sources
    if "sources" in result:
        state["sources"].extend(result["sources"])
    
    # Ajout de l'étape de processing
    state["processing_steps"].append(f"Processed by {agent_type.value}")
    
    return state

def add_error_to_state(state: SolarNasihState, error: str) -> SolarNasihState:
    """
    Ajoute une erreur à l'état
    
    Args:
        state: État actuel
        error: Message d'erreur
        
    Returns:
        État avec erreur ajoutée
    """
    
    state["errors"].append(error)
    state["debug_info"]["last_error"] = error
    
    return state

def add_debug_info(state: SolarNasihState, key: str, value: Any) -> SolarNasihState:
    """
    Ajoute des informations de debug à l'état
    
    Args:
        state: État actuel
        key: Clé pour l'information de debug
        value: Valeur à ajouter
        
    Returns:
        État avec information de debug ajoutée
    """
    
    state["debug_info"][key] = value
    
    return state