from typing import Dict, Any
from graph.state import SolarNasihState, update_state_with_agent_result, add_error_to_state
from models.schemas import AgentType
from services.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)

# Initialisation des services
rag_service = RAGService()

async def language_detection_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud de détection de langue
    """
    try:
        # Détection simple de la langue (à améliorer)
        message = state["current_message"].lower()
        
        # Détection basique français/anglais
        french_indicators = ["le", "la", "les", "un", "une", "des", "est", "sont", "avec", "pour"]
        english_indicators = ["the", "is", "are", "with", "for", "and", "or", "but"]
        
        french_score = sum(1 for word in french_indicators if word in message)
        english_score = sum(1 for word in english_indicators if word in message)
        
        if french_score > english_score:
            state["detected_language"] = "fr"
        else:
            state["detected_language"] = "en"
        
        state["processing_steps"].append("Language detection completed")
        
    except Exception as e:
        state = add_error_to_state(state, f"Language detection error: {str(e)}")
        state["detected_language"] = "fr"  # Défaut en français
    
    return state

async def task_division_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud de division de tâches intelligent : route et exécute la requête via TaskDividerAgent
    """
    try:
        from agents.task_divider import TaskDividerAgent
        from graph.workflow import SolarNasihWorkflow
        # Récupérer le mapping des agents depuis le workflow (singleton)
        workflow = SolarNasihWorkflow._instance if hasattr(SolarNasihWorkflow, '_instance') else None
        if workflow is None:
            workflow = SolarNasihWorkflow()
            SolarNasihWorkflow._instance = workflow
        agents_map = workflow.agents
        agent = agents_map.get(AgentType.TASK_DIVIDER)
        if agent:
            # Conversion de l'état en AgentState
            from models.schemas import AgentState
            agent_state = AgentState(
                current_message=state["current_message"],
                detected_language=state["detected_language"],
                user_intent=state["user_intent"],
                agent_route=AgentType.TASK_DIVIDER,
                context=state["user_context"],
                response="",
                confidence=0.0,
                sources=[],
                processing_history=state["conversation_history"]
            )
            
            # Appel correct avec les deux paramètres
            result = await agent.process(agent_state, agents_map)
            
            # Protection : s'assurer que result est un dict avec 'response' string
            if not isinstance(result, dict) or 'response' not in result or not isinstance(result['response'], str):
                result = {
                    'response': 'Solar Nasih : Je n\'ai pas pu traiter votre demande, mais je reste à votre disposition pour toute question sur l\'énergie solaire.',
                    'confidence': 0.2,
                    'sources': ['Fallback TaskDivider']
                }
            
            # Mise à jour de l'état avec le résultat
            state = update_state_with_agent_result(state, AgentType.TASK_DIVIDER, result)
            
            # S'assurer que la réponse est bien définie
            if not state.get("response") or not state["response"].strip():
                state["response"] = result.get("response", "Aucune réponse générée")
            
            # IMPORTANT: Ne pas modifier agent_route ici, laisser le workflow décider
            # Le TaskDividerAgent va gérer le routage interne
                
        else:
            state['response'] = "Erreur : agent de division des tâches non disponible."
    except Exception as e:
        state['response'] = f"Erreur dans le node de division des tâches : {str(e)}"
    
    # Protection finale : forcer response à être une string valide
    if not isinstance(state.get('response', ''), str):
        state['response'] = str(state.get('response', ''))
    
    # NE PAS modifier agent_route ici - laisser le TaskDividerAgent gérer le routage
    # state['agent_route'] reste AgentType.TASK_DIVIDER pour ce nœud
    
    logger.info(f"[TaskDividerNode] response: {state['response'][:100]}... | agent_route: {state.get('agent_route')}")
    return state

async def rag_processing_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud de traitement RAG - Interface avec le système RAG existant
    """
    try:
        # Appel au service RAG
        rag_result = await rag_service.query(
            query=state["current_message"],
            language=state["detected_language"]
        )
        
        # Mise à jour de l'état avec le résultat RAG
        result = {
            "response": rag_result.get("answer", "Aucune réponse trouvée"),
            "confidence": rag_result.get("confidence", 0.7),
            "sources": rag_result.get("sources", [])
        }
        
        state = update_state_with_agent_result(state, AgentType.RAG_SYSTEM, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"RAG processing error: {str(e)}")
        state["response"] = "Erreur lors de la recherche d'informations"
    
    return state

async def technical_processing_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud de traitement technique
    """
    try:
        from agents.technical_advisor import TechnicalAdvisorAgent
        
        # Initialisation de l'agent technique
        technical_agent = TechnicalAdvisorAgent()
        
        # Conversion de l'état
        from models.schemas import AgentState
        agent_state = AgentState(
            current_message=state["current_message"],
            detected_language=state["detected_language"],
            user_intent=state["user_intent"],
            agent_route=AgentType.TECHNICAL_ADVISOR,
            context=state["user_context"],
            response="",
            confidence=0.0,
            sources=[],
            processing_history=state["conversation_history"]
        )
        
        # Traitement par l'agent technique
        result = await technical_agent.process(agent_state)
        
        # Mise à jour de l'état
        state = update_state_with_agent_result(state, AgentType.TECHNICAL_ADVISOR, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Technical processing error: {str(e)}")
        state["response"] = "Erreur lors du conseil technique"
    
    return state

async def simulation_processing_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud de simulation énergétique
    """
    try:
        from agents.energy_simulator import EnergySimulatorAgent
        
        # Initialisation de l'agent simulateur
        simulator_agent = EnergySimulatorAgent()
        
        # Conversion de l'état
        from models.schemas import AgentState
        agent_state = AgentState(
            current_message=state["current_message"],
            detected_language=state["detected_language"],
            user_intent=state["user_intent"],
            agent_route=AgentType.ENERGY_SIMULATOR,
            context=state.get("simulation_params", state["user_context"]),
            response="",
            confidence=0.0,
            sources=[],
            processing_history=state["conversation_history"]
        )
        
        # Traitement par l'agent simulateur
        result = await simulator_agent.process(agent_state)
        
        # Mise à jour de l'état
        state = update_state_with_agent_result(state, AgentType.ENERGY_SIMULATOR, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Simulation processing error: {str(e)}")
        # Si l'agent a retourné une réponse partielle, la conserver
        if "response" not in state or not state["response"]:
            state["response"] = (
                "Pour calculer le ROI (retour sur investissement) d'une installation solaire :\n"
                "1. Estimez le coût total de l'installation (ex: 12 000€).\n"
                "2. Calculez les économies annuelles sur la facture d'électricité (ex: 1 200€/an).\n"
                "3. ROI = coût / économies annuelles (ex: 12 000 / 1 200 = 10 ans).\n"
                "Le ROI correspond au nombre d'années nécessaires pour rentabiliser l'investissement."
            )
    
    return state

async def regulatory_processing_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud d'assistance réglementaire
    """
    try:
        # Simulation d'un agent réglementaire
        from services.tavily_service import TavilyService
        from services.gemini_service import GeminiService
        
        tavily_service = TavilyService()
        gemini_service = GeminiService()
        
        # Recherche d'informations réglementaires
        regulatory_info = tavily_service.search_solar_regulations()
        
        # Génération de réponse avec Gemini
        context_info = "\n".join([info.get("content", "") for info in regulatory_info[:3]])
        
        prompt = f"""
        En tant qu'expert en réglementation photovoltaïque, réponds à cette question:
        {state['current_message']}
        
        Contexte réglementaire:
        {context_info}
        
        Fournis une réponse précise sur les aspects réglementaires.
        """
        
        response = await gemini_service.generate_response(prompt)
        
        result = {
            "response": response,
            "confidence": 0.8,
            "sources": [info.get("url", "") for info in regulatory_info]
        }
        
        state = update_state_with_agent_result(state, AgentType.REGULATORY_ASSISTANT, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Regulatory processing error: {str(e)}")
        state["response"] = "Erreur lors de la consultation réglementaire"
    
    return state

async def commercial_processing_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud d'assistance commerciale
    """
    try:
        from services.tavily_service import TavilyService
        from services.gemini_service import GeminiService
        
        tavily_service = TavilyService()
        gemini_service = GeminiService()
        
        # Recherche d'informations commerciales
        price_info = tavily_service.search_solar_prices()
        incentive_info = tavily_service.search_solar_incentives()
        
        # Compilation des informations
        commercial_context = ""
        if price_info:
            commercial_context += "Informations tarifaires:\n"
            commercial_context += "\n".join([info.get("content", "")[:200] for info in price_info[:2]])
        
        if incentive_info:
            commercial_context += "\n\nAides disponibles:\n"
            commercial_context += "\n".join([info.get("content", "")[:200] for info in incentive_info[:2]])
        
        prompt = f"""
        En tant qu'expert commercial en énergie solaire, réponds à cette question:
        {state['current_message']}
        
        Contexte commercial:
        {commercial_context}
        
        Fournis des informations précises sur les aspects financiers, prix, et aides disponibles.
        """
        
        response = await gemini_service.generate_response(prompt)
        
        result = {
            "response": response,
            "confidence": 0.8,
            "sources": [info.get("url", "") for info in (price_info + incentive_info)]
        }
        
        state = update_state_with_agent_result(state, AgentType.COMMERCIAL_ASSISTANT, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Commercial processing error: {str(e)}")
        state["response"] = "Erreur lors de la consultation commerciale"
    
    return state

async def educational_processing_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud d'assistance pédagogique
    """
    try:
        from services.gemini_service import GeminiService
        
        gemini_service = GeminiService()
        
        prompt = f"""
        En tant qu'expert pédagogique en énergie solaire, réponds à cette question de formation:
        {state['current_message']}
        
        Fournis une réponse éducative avec:
        - Explications claires et progressives
        - Exemples concrets
        - Étapes d'apprentissage
        - Ressources recommandées
        
        Adapte le niveau selon la question posée.
        """
        
        response = await gemini_service.generate_response(prompt)
        
        result = {
            "response": response,
            "confidence": 0.8,
            "sources": ["Formation Solar Nasih"]
        }
        
        state = update_state_with_agent_result(state, AgentType.EDUCATIONAL_AGENT, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Educational processing error: {str(e)}")
        state["response"] = "Erreur lors de l'assistance pédagogique"
    
    return state

async def certification_processing_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud d'assistance certification
    """
    try:
        from services.tavily_service import TavilyService
        from services.gemini_service import GeminiService
        
        tavily_service = TavilyService()
        gemini_service = GeminiService()
        
        # Recherche d'informations sur les certifications
        cert_info = tavily_service.search("certification RGE photovoltaïque formation")
        
        context_info = "\n".join([info.get("content", "")[:300] for info in cert_info[:3]])
        
        prompt = f"""
        En tant qu'expert en certifications photovoltaïques, réponds à cette question:
        {state['current_message']}
        
        Contexte certifications:
        {context_info}
        
        Fournis des informations sur:
        - Certifications RGE nécessaires
        - Processus de formation
        - Organismes certificateurs
        - Démarches à suivre
        """
        
        response = await gemini_service.generate_response(prompt)
        
        result = {
            "response": response,
            "confidence": 0.8,
            "sources": [info.get("url", "") for info in cert_info]
        }
        
        state = update_state_with_agent_result(state, AgentType.CERTIFICATION_ASSISTANT, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Certification processing error: {str(e)}")
        state["response"] = "Erreur lors de l'assistance certification"
    
    return state

async def document_generation_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud de génération de documents
    """
    try:
        from services.gemini_service import GeminiService
        
        gemini_service = GeminiService()
        doc_context = state.get("document_context", {})
        
        # Détermination du type de document
        doc_type = doc_context.get("document_type", "rapport")
        
        prompt = f"""
        Génère un {doc_type} professionnel basé sur ces informations:
        
        Message: {state['current_message']}
        Contexte: {doc_context}
        
        Structure le document avec:
        - En-tête professionnel
        - Sections organisées
        - Données techniques si applicable
        - Conclusion et recommandations
        
        Format: Markdown pour faciliter l'export
        """
        
        response = await gemini_service.generate_response(prompt)
        
        # Simulation de sauvegarde du document
        doc_id = f"doc_{hash(response)}"
        doc_url = f"/documents/{doc_id}.pdf"
        
        result = {
            "response": f"Document généré avec succès: {doc_url}",
            "confidence": 0.9,
            "sources": ["Générateur Solar Nasih"],
            "document_content": response,
            "document_url": doc_url
        }
        
        state = update_state_with_agent_result(state, AgentType.DOCUMENT_GENERATOR, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Document generation error: {str(e)}")
        state["response"] = "Erreur lors de la génération du document"
    
    return state

async def voice_processing_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud de traitement vocal
    """
    try:
        voice_data = state.get("voice_data", {})
        audio_file = voice_data.get("audio_file")
        
        if not audio_file:
            raise ValueError("Aucun fichier audio fourni")
        
        # Simulation du traitement vocal
        # En production, utiliser speech_recognition et gTTS
        transcribed_text = "Simulation: Combien coûte une installation photovoltaïque ?"
        
        # Mise à jour du message avec le texte transcrit
        state["current_message"] = transcribed_text
        
        # Génération de réponse vocale
        from services.gemini_service import GeminiService
        gemini_service = GeminiService()
        
        response = await gemini_service.generate_response(
            f"Réponds de manière concise à cette question vocale: {transcribed_text}"
        )
        
        result = {
            "response": response,
            "confidence": 0.8,
            "sources": ["Traitement vocal"],
            "transcribed_text": transcribed_text,
            "audio_response_url": "/audio/response.mp3"  # Simulation
        }
        
        state = update_state_with_agent_result(state, AgentType.VOICE_PROCESSOR, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Voice processing error: {str(e)}")
        state["response"] = "Erreur lors du traitement vocal"
    
    return state

async def response_formatting_node(state: SolarNasihState) -> SolarNasihState:
    """
    Nœud de formatage final de la réponse
    """
    try:
        # Amélioration de la réponse si nécessaire
        if state.get("response"):
            # Ajout d'informations contextuelles
            if state.get("sources"):
                state["response"] += f"\n\nSources: {', '.join(state['sources'][:3])}"
            # Ajout de la signature
            state["response"] += "\n\n---\nSolar Nasih - Votre assistant en énergie solaire"
        
        # Logging des étapes de traitement
        state["processing_steps"].append("Response formatting completed")
        
        # Ajout à l'historique de conversation
        agent_route = state.get("agent_route", AgentType.TASK_DIVIDER)
        if isinstance(agent_route, AgentType):
            agent_route_val = agent_route.value
        else:
            agent_route_val = str(agent_route)
            
        state["conversation_history"].append({
            "user_message": state["current_message"],
            "assistant_response": state["response"],
            "agent_used": agent_route_val,
            "timestamp": "2024-01-01T00:00:00Z"  # À remplacer par datetime.now()
        })
    except Exception as e:
        state = add_error_to_state(state, f"Response formatting error: {str(e)}")
    return state

async def multilingual_processing_node(state: SolarNasihState) -> SolarNasihState:
    """Nœud de traitement multilingue"""
    try:
        from agents.complete_remaining_agents import MultilingualDetectorAgent
        
        multilingual_agent = MultilingualDetectorAgent()
        
        from models.schemas import AgentState
        agent_state = AgentState(
            current_message=state["current_message"],
            detected_language=state["detected_language"],
            user_intent=state["user_intent"],
            agent_route=AgentType.MULTILINGUAL_DETECTOR,
            context=state["user_context"],
            response="",
            confidence=0.0,
            sources=[],
            processing_history=state["conversation_history"]
        )
        
        result = await multilingual_agent.process(agent_state)
        state = update_state_with_agent_result(state, AgentType.MULTILINGUAL_DETECTOR, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Multilingual processing error: {str(e)}")
        state["response"] = "Erreur lors du traitement multilingue"
    
    return state

async def educational_processing_node(state: SolarNasihState) -> SolarNasihState:
    """Nœud de traitement pédagogique"""
    try:
        from agents.complete_remaining_agents import EducationalAgent
        
        educational_agent = EducationalAgent()
        
        from models.schemas import AgentState
        agent_state = AgentState(
            current_message=state["current_message"],
            detected_language=state["detected_language"],
            user_intent=state["user_intent"],
            agent_route=AgentType.EDUCATIONAL_AGENT,
            context=state["user_context"],
            response="",
            confidence=0.0,
            sources=[],
            processing_history=state["conversation_history"]
        )
        
        result = await educational_agent.process(agent_state)
        state = update_state_with_agent_result(state, AgentType.EDUCATIONAL_AGENT, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Educational processing error: {str(e)}")
        state["response"] = "Erreur lors de l'assistance pédagogique"
    
    return state

async def certification_processing_node(state: SolarNasihState) -> SolarNasihState:
    """Nœud de traitement certification"""
    try:
        from agents.complete_remaining_agents import CertificationAssistantAgent
        
        cert_agent = CertificationAssistantAgent()
        
        from models.schemas import AgentState
        agent_state = AgentState(
            current_message=state["current_message"],
            detected_language=state["detected_language"],
            user_intent=state["user_intent"],
            agent_route=AgentType.CERTIFICATION_ASSISTANT,
            context=state["user_context"],
            response="",
            confidence=0.0,
            sources=[],
            processing_history=state["conversation_history"]
        )
        
        result = await cert_agent.process(agent_state)
        state = update_state_with_agent_result(state, AgentType.CERTIFICATION_ASSISTANT, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Certification processing error: {str(e)}")
        state["response"] = "Erreur lors de l'assistance certification"
    
    return state

async def document_indexer_node(state: SolarNasihState) -> SolarNasihState:
    """Nœud d'indexation de documents"""
    try:
        from agents.complete_remaining_agents import DocumentIndexerAgent
        
        indexer_agent = DocumentIndexerAgent()
        
        from models.schemas import AgentState
        agent_state = AgentState(
            current_message=state["current_message"],
            detected_language=state["detected_language"],
            user_intent=state["user_intent"],
            agent_route=AgentType.DOCUMENT_INDEXER,
            context=state.get("document_context", state["user_context"]),
            response="",
            confidence=0.0,
            sources=[],
            processing_history=state["conversation_history"]
        )
        
        result = await indexer_agent.process(agent_state)
        state = update_state_with_agent_result(state, AgentType.DOCUMENT_INDEXER, result)
        
    except Exception as e:
        state = add_error_to_state(state, f"Document indexing error: {str(e)}")
        state["response"] = "Erreur lors de l'indexation du document"
    
    return state