"""
Agent RAG multimodal avec LangGraph et Gemini 2.0
Architecture basée sur le diagramme fourni avec MEM (Memory), Query Expansion, Re-ranking
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass
from datetime import datetime
import json

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Gemini imports
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Imports locaux
from models import SearchResult, SearchQuery
from pipeline import MultimodalRAGPipeline
from config import RAGPipelineConfig

logger = logging.getLogger(__name__)

# ==================== Configuration Gemini ====================

@dataclass
class GeminiConfig:
    """Configuration pour Gemini 2.0"""
    api_key: str
    model_name: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_output_tokens: int = 2048
    safety_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.safety_settings is None:
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

class GeminiLLM:
    """Interface Gemini 2.0 pour la génération de réponses"""
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        genai.configure(api_key=config.api_key)
        
        self.model = genai.GenerativeModel(
            model_name=config.model_name,
            safety_settings=config.safety_settings
        )
        
        # Configuration de génération
        self.generation_config = genai.types.GenerationConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
            top_p=0.8,
            top_k=20
        )
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Génère une réponse avec Gemini"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=self.generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Erreur Gemini: {e}")
            return f"Erreur lors de la génération: {str(e)}"
    
    def generate_response_sync(self, prompt: str, context: str = "") -> str:
        """Version synchrone de la génération"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Erreur Gemini: {e}")
            return f"Erreur lors de la génération: {str(e)}"

# ==================== États LangGraph ====================

class AgentState(TypedDict):
    """État de l'agent RAG"""
    # Entrées utilisateur
    user_query: str
    conversation_history: List[BaseMessage]
    
    # Expansion de requête
    expanded_queries: List[str]
    search_intent: str
    
    # Récupération
    search_results: List[SearchResult]
    relevant_chunks: List[Dict[str, Any]]
    
    # Mémoire et contexte
    memory_context: Dict[str, Any]
    session_id: str
    
    # Génération
    generated_response: str
    confidence_score: float
    
    # Métadonnées
    processing_steps: List[str]
    timestamp: str
    iteration_count: int

# ==================== Composants Spécialisés ====================

class QueryExpander:
    """Composant d'expansion de requête utilisant Gemini"""
    
    def __init__(self, gemini_llm: GeminiLLM):
        self.llm = gemini_llm
        
        self.expansion_prompt = """
        Vous êtes un expert en expansion de requêtes pour la recherche d'informations.
        
        Requête originale: {query}
        
        Tâches:
        1. Identifiez l'intention de recherche (information, comparaison, procédure, etc.)
        2. Générez 3-5 requêtes alternatives qui capturent différents aspects de la question
        3. Incluez des synonymes et des reformulations
        4. Considerez les termes techniques et vulgarisés
        
        Format de réponse:
        INTENTION: [intention de recherche]
        REQUETES:
        1. [requête alternative 1]
        2. [requête alternative 2]
        3. [requête alternative 3]
        4. [requête alternative 4]
        5. [requête alternative 5]
        """
    
    def expand_query(self, query: str) -> Dict[str, Any]:
        """Expanse une requête en plusieurs variantes"""
        try:
            prompt = self.expansion_prompt.format(query=query)
            response = self.llm.generate_response_sync(prompt)
            
            # Parse de la réponse
            lines = response.strip().split('\n')
            intention = ""
            expanded_queries = []
            
            for line in lines:
                if line.startswith("INTENTION:"):
                    intention = line.replace("INTENTION:", "").strip()
                elif line.strip() and (line[0].isdigit() or line.startswith("-")):
                    # Nettoyer la requête (enlever numéros et tirets)
                    clean_query = line.split(".", 1)[-1].strip()
                    clean_query = clean_query.lstrip("- ").strip()
                    if clean_query:
                        expanded_queries.append(clean_query)
            
            return {
                "intention": intention,
                "expanded_queries": expanded_queries[:5],  # Limiter à 5
                "original_query": query
            }
            
        except Exception as e:
            logger.error(f"Erreur expansion requête: {e}")
            return {
                "intention": "information",
                "expanded_queries": [query],
                "original_query": query
            }

class ResponseGenerator:
    """Générateur de réponse final utilisant Gemini"""
    
    def __init__(self, gemini_llm: GeminiLLM):
        self.llm = gemini_llm
        
        self.response_prompt = """
        Vous êtes un assistant IA expert qui aide les utilisateurs en répondant à leurs questions 
        basées sur des documents fournis.
        
        CONTEXTE RÉCUPÉRÉ:
        {context}
        
        QUESTION UTILISATEUR: {query}
        
        INSTRUCTIONS:
        1. Répondez de manière précise et complète à la question
        2. Basez votre réponse sur les informations fournies dans le contexte
        3. Si les informations sont insuffisantes, indiquez-le clairement
        4. Structurez votre réponse de manière claire avec des sections si nécessaire
        5. Citez les sources pertinentes (pages, sections) quand c'est possible
        6. Soyez objectif et factuel
        
        RÉPONSE:
        """
        
        self.synthesis_prompt = """
        Vous devez synthétiser plusieurs éléments d'information pour répondre à une question.
        
        QUESTION: {query}
        INTENTION: {intention}
        
        INFORMATIONS DISPONIBLES:
        {chunks_info}
        
        Créez une réponse cohérente qui:
        1. Répond directement à la question
        2. Intègre toutes les informations pertinentes
        3. Résout les éventuelles contradictions
        4. Fournit une perspective complète
        5. Structure l'information de manière logique
        
        RÉPONSE SYNTHÉTISÉE:
        """
    
    def generate_response(self, query: str, chunks: List[Dict[str, Any]], 
                         intention: str = "") -> Dict[str, Any]:
        """Génère une réponse basée sur les chunks récupérés"""
        try:
            # Préparer le contexte
            context_parts = []
            for i, chunk in enumerate(chunks, 1):
                chunk_info = f"""
                [Source {i} - Page {chunk.get('page_number', 'N/A')}]
                Type: {chunk.get('chunk_type', 'text')}
                Contenu: {chunk.get('content', '')[:500]}...
                Score: {chunk.get('score', 0):.3f}
                """
                context_parts.append(chunk_info)
            
            context = "\n".join(context_parts)
            
            # Choisir le prompt selon le nombre de chunks
            if len(chunks) > 3:
                # Utiliser le prompt de synthèse pour plusieurs sources
                chunks_info = "\n".join([
                    f"• {chunk.get('content', '')[:200]}... (Page {chunk.get('page_number', 'N/A')})"
                    for chunk in chunks
                ])
                
                prompt = self.synthesis_prompt.format(
                    query=query,
                    intention=intention,
                    chunks_info=chunks_info
                )
            else:
                # Utiliser le prompt simple
                prompt = self.response_prompt.format(
                    context=context,
                    query=query
                )
            
            # Générer la réponse
            response = self.llm.generate_response_sync(prompt)
            
            # Calculer un score de confiance basique
            confidence = self._calculate_confidence(chunks, response)
            
            return {
                "response": response,
                "confidence": confidence,
                "sources_used": len(chunks),
                "context_length": len(context)
            }
            
        except Exception as e:
            logger.error(f"Erreur génération réponse: {e}")
            return {
                "response": f"Erreur lors de la génération de la réponse: {str(e)}",
                "confidence": 0.0,
                "sources_used": 0,
                "context_length": 0
            }
    
    def _calculate_confidence(self, chunks: List[Dict[str, Any]], response: str) -> float:
        """Calcule un score de confiance basique"""
        if not chunks:
            return 0.0
        
        # Facteurs de confiance
        avg_score = sum(chunk.get('score', 0) for chunk in chunks) / len(chunks)
        num_sources = min(len(chunks) / 5, 1.0)  # Bonus pour plus de sources
        response_length = min(len(response) / 500, 1.0)  # Bonus pour réponses détaillées
        
        # Score composite
        confidence = (avg_score * 0.5 + num_sources * 0.3 + response_length * 0.2)
        return min(confidence, 1.0)

class MemoryManager:
    """Gestionnaire de mémoire conversationnelle"""
    
    def __init__(self):
        self.sessions = {}
        self.max_history_length = 10
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Récupère le contexte d'une session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "conversation_history": [],
                "topics": [],
                "preferences": {},
                "created_at": datetime.now().isoformat()
            }
        
        return self.sessions[session_id]
    
    def update_session(self, session_id: str, query: str, response: str, 
                      topics: List[str] = None):
        """Met à jour le contexte de session"""
        context = self.get_session_context(session_id)
        
        # Ajouter à l'historique
        context["conversation_history"].append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limiter la taille de l'historique
        if len(context["conversation_history"]) > self.max_history_length:
            context["conversation_history"] = context["conversation_history"][-self.max_history_length:]
        
        # Mettre à jour les sujets
        if topics:
            for topic in topics:
                if topic not in context["topics"]:
                    context["topics"].append(topic)
        
        # Limiter les sujets
        context["topics"] = context["topics"][-20:]
    
    def get_context_summary(self, session_id: str) -> str:
        """Génère un résumé du contexte pour l'IA"""
        context = self.get_session_context(session_id)
        
        if not context["conversation_history"]:
            return ""
        
        # Récupérer les dernières interactions
        recent_history = context["conversation_history"][-3:]
        
        summary_parts = []
        if context["topics"]:
            summary_parts.append(f"Sujets abordés: {', '.join(context['topics'][-5:])}")
        
        if recent_history:
            summary_parts.append("Dernières interactions:")
            for item in recent_history:
                summary_parts.append(f"Q: {item['query'][:100]}...")
                summary_parts.append(f"R: {item['response'][:100]}...")
        
        return "\n".join(summary_parts)

# ==================== Nœuds LangGraph ====================

class RAGAgent:
    """Agent RAG principal utilisant LangGraph"""
    
    def __init__(self, rag_pipeline: MultimodalRAGPipeline, gemini_config: GeminiConfig):
        self.rag_pipeline = rag_pipeline
        self.gemini_llm = GeminiLLM(gemini_config)
        
        # Composants spécialisés
        self.query_expander = QueryExpander(self.gemini_llm)
        self.response_generator = ResponseGenerator(self.gemini_llm)
        self.memory_manager = MemoryManager()
        
        # Configuration du graphe
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construit le graphe LangGraph de l'agent"""
        workflow = StateGraph(AgentState)
        
        # Ajout des nœuds
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("expand_query", self._expand_query_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("rerank", self._rerank_node)
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Définition du flux
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "expand_query")
        workflow.add_edge("expand_query", "retrieve")
        workflow.add_edge("retrieve", "rerank")
        workflow.add_edge("rerank", "generate")
        workflow.add_edge("generate", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _initialize_node(self, state: AgentState) -> AgentState:
        """Nœud d'initialisation"""
        state["processing_steps"] = ["initialization"]
        state["timestamp"] = datetime.now().isoformat()
        state["iteration_count"] = 0
        
        # Récupérer le contexte de mémoire
        session_id = state.get("session_id", "default")
        memory_context = self.memory_manager.get_session_context(session_id)
        state["memory_context"] = memory_context
        
        logger.info(f"Agent initialisé pour requête: {state['user_query'][:50]}...")
        return state
    
    def _expand_query_node(self, state: AgentState) -> AgentState:
        """Nœud d'expansion de requête"""
        state["processing_steps"].append("query_expansion")
        
        try:
            expansion_result = self.query_expander.expand_query(state["user_query"])
            
            state["expanded_queries"] = expansion_result["expanded_queries"]
            state["search_intent"] = expansion_result["intention"]
            
            logger.info(f"Requête expansée: {len(state['expanded_queries'])} variantes")
            
        except Exception as e:
            logger.error(f"Erreur expansion: {e}")
            state["expanded_queries"] = [state["user_query"]]
            state["search_intent"] = "information"
        
        return state
    
    def _retrieve_node(self, state: AgentState) -> AgentState:
        """Nœud de récupération de documents"""
        state["processing_steps"].append("retrieval")
        
        all_results = []
        
        # Rechercher avec la requête originale et les expansions
        queries_to_search = [state["user_query"]] + state.get("expanded_queries", [])
        
        for query in queries_to_search[:4]:  # Limiter à 4 requêtes max
            try:
                results = self.rag_pipeline.search(query, k=3)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Erreur recherche '{query}': {e}")
        
        # Déduplication basée sur chunk_id
        unique_results = {}
        for result in all_results:
            if result.chunk_id not in unique_results:
                unique_results[result.chunk_id] = result
            else:
                # Garder le meilleur score
                if result.score > unique_results[result.chunk_id].score:
                    unique_results[result.chunk_id] = result
        
        state["search_results"] = list(unique_results.values())
        
        logger.info(f"Récupération: {len(state['search_results'])} chunks uniques trouvés")
        return state
    
    def _rerank_node(self, state: AgentState) -> AgentState:
        """Nœud de re-ranking des résultats"""
        state["processing_steps"].append("reranking")
        
        # Re-ranking simple basé sur la pertinence et la diversité
        results = state["search_results"]
        
        if not results:
            state["relevant_chunks"] = []
            return state
        
        # Trier par score décroissant
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        
        # Sélectionner les meilleurs en favorisant la diversité
        selected_chunks = []
        seen_pages = set()
        seen_types = set()
        
        for result in sorted_results:
            chunk_dict = {
                "chunk_id": result.chunk_id,
                "content": result.content,
                "chunk_type": result.chunk_type.value,
                "page_number": result.page_number,
                "score": result.score,
                "metadata": result.metadata
            }
            
            # Critères de sélection
            add_chunk = True
            
            # Favoriser la diversité des pages
            if len(selected_chunks) >= 3 and result.page_number in seen_pages:
                if result.score < 0.8:  # Seuil de score élevé
                    add_chunk = False
            
            # Favoriser la diversité des types
            if len(selected_chunks) >= 5 and result.chunk_type.value in seen_types:
                if result.score < 0.9:
                    add_chunk = False
            
            if add_chunk:
                selected_chunks.append(chunk_dict)
                seen_pages.add(result.page_number)
                seen_types.add(result.chunk_type.value)
            
            # Limiter à 8 chunks maximum
            if len(selected_chunks) >= 8:
                break
        
        state["relevant_chunks"] = selected_chunks
        
        logger.info(f"Re-ranking: {len(selected_chunks)} chunks sélectionnés")
        return state
    
    def _generate_node(self, state: AgentState) -> AgentState:
        """Nœud de génération de réponse"""
        state["processing_steps"].append("generation")
        
        try:
            generation_result = self.response_generator.generate_response(
                query=state["user_query"],
                chunks=state["relevant_chunks"],
                intention=state.get("search_intent", "")
            )
            
            state["generated_response"] = generation_result["response"]
            state["confidence_score"] = generation_result["confidence"]
            
            logger.info(f"Réponse générée (confiance: {generation_result['confidence']:.3f})")
            
        except Exception as e:
            logger.error(f"Erreur génération: {e}")
            state["generated_response"] = "Désolé, je n'ai pas pu générer une réponse appropriée."
            state["confidence_score"] = 0.0
        
        return state
    
    def _finalize_node(self, state: AgentState) -> AgentState:
        """Nœud de finalisation"""
        state["processing_steps"].append("finalization")
        state["iteration_count"] += 1
        
        # Mettre à jour la mémoire
        session_id = state.get("session_id", "default")
        self.memory_manager.update_session(
            session_id=session_id,
            query=state["user_query"],
            response=state["generated_response"]
        )
        
        logger.info("Traitement terminé")
        return state
    
    async def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Traite une requête utilisateur"""
        # État initial
        initial_state = AgentState(
            user_query=query,
            session_id=session_id,
            conversation_history=[],
            expanded_queries=[],
            search_intent="",
            search_results=[],
            relevant_chunks=[],
            memory_context={},
            generated_response="",
            confidence_score=0.0,
            processing_steps=[],
            timestamp="",
            iteration_count=0
        )
        
        # Exécution du graphe
        try:
            final_state = await asyncio.to_thread(self.graph.invoke, initial_state)
            
            return {
                "response": final_state["generated_response"],
                "confidence": final_state["confidence_score"],
                "sources": final_state["relevant_chunks"],
                "processing_steps": final_state["processing_steps"],
                "expanded_queries": final_state.get("expanded_queries", []),
                "search_intent": final_state.get("search_intent", ""),
                "timestamp": final_state["timestamp"]
            }
        
        except Exception as e:
            logger.error(f"Erreur traitement requête: {e}")
            return {
                "response": f"Erreur lors du traitement: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "processing_steps": ["error"],
                "expanded_queries": [],
                "search_intent": "",
                "timestamp": datetime.now().isoformat()
            }
    
    def process_query_sync(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Version synchrone du traitement"""
        return asyncio.run(self.process_query(query, session_id))

# ==================== Factory et Interface ====================

def create_rag_agent(rag_pipeline: MultimodalRAGPipeline, 
                    gemini_api_key: str,
                    model_name: str = "gemini-2.0-flash-exp") -> RAGAgent:
    """Factory pour créer un agent RAG"""
    gemini_config = GeminiConfig(
        api_key=gemini_api_key,
        model_name=model_name
    )
    
    return RAGAgent(rag_pipeline, gemini_config)

# ==================== Exemple d'utilisation ====================

async def example_usage():
    """Exemple d'utilisation de l'agent RAG"""
    # Configuration
    rag_config = RAGPipelineConfig()
    rag_pipeline = MultimodalRAGPipeline(rag_config)
    
    # Clé API Gemini (à configurer)
    GEMINI_API_KEY = "your-gemini-api-key-here"
    
    # Création de l'agent
    agent = create_rag_agent(rag_pipeline, GEMINI_API_KEY)
    
    # Exemples de requêtes
    queries = [
        "Qu'est-ce que l'intelligence artificielle?",
        "Comment fonctionne un réseau de neurones?",
        "Quelles sont les applications du machine learning?",
        "Explique-moi le deep learning",
        "Quelle est la différence entre IA et ML?"
    ]
    
    session_id = "demo_session"
    
    for query in queries:
        print(f"\n🤖 Requête: {query}")
        print("=" * 50)
        
        result = await agent.process_query(query, session_id)
        
        print(f"💭 Intention: {result['search_intent']}")
        print(f"🔍 Requêtes expansées: {result['expanded_queries']}")
        print(f"📊 Confiance: {result['confidence']:.3f}")
        print(f"📚 Sources: {len(result['sources'])}")
        print(f"📝 Réponse: {result['response'][:200]}...")
        
        # Pause pour la démo
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Exemple d'exécution
    asyncio.run(example_usage())