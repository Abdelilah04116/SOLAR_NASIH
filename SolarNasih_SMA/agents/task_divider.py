from typing import Dict, Any, List
from langchain.tools import Tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType, AgentState
from services.tavily_service import TavilyService
from services.gemini_service import GeminiService
from services.rag_service import RAGService
import re
import logging

logger = logging.getLogger(__name__)

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
        self.rag_service = RAGService()  # Service RAG pour appels directs
        
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
                r"attestation", r"certificat", r"devis", r"devis détaillé", r"prix", 
                r"estimation", r"tarif", r"pdf", r"document", r"génère", r"créer"
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
                r"translate", r"traduction", r"langue", r"the", r"and", r"is", r"are",
                r"كيف", r"لماذا", r"أين", r"من", r"ماذا", r"متى", r"كيفاش", r"علاش",
                r"ⵎⴰⵏ", r"ⵎⴰⵏⵉ", r"ⵎⴰⵏⵉⵎ"
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
        """Méthode principale de traitement - analyse et route les requêtes"""
        try:
            # Stocker la question originale pour l'agent résumeur
            self.current_user_question = state.current_message
            
            # 1. Détecter les agents pertinents
            detected_agents = self._detect_relevant_agents(state.current_message)
            
            if not detected_agents:
                logger.warning("Aucun agent détecté, utilisation du RAG par défaut")
                detected_agents = [AgentType.RAG_SYSTEM]
            
            # 2. Vérifier d'abord le RAG si disponible
            rag_result = await self._check_rag_first(state.current_message)
            
            # 3. Obtenir les réponses des agents
            agent_responses = await self._get_agent_responses(state, detected_agents, agents_map)
            
            # 4. Construire la réponse finale
            final_response = await self._build_final_response(agent_responses, detected_agents)
            
            # 5. Calculer la confiance globale
            overall_confidence = self._calculate_overall_confidence(agent_responses)
            
            # 6. Collecter les sources
            sources = self._collect_sources(agent_responses)
        
            return {
                "response": final_response,
                "agent_used": "task_divider",
                "confidence": overall_confidence,
                "sources": sources,
                "agent_responses": agent_responses,
                "detected_agents": [agent.value for agent in detected_agents],
                "rag_result": rag_result
            }
            
        except Exception as e:
            logger.error(f"Erreur dans TaskDividerAgent: {e}")
            return {
                "response": f"Erreur lors du traitement: {str(e)}",
                "agent_used": "task_divider",
                "confidence": 0.0,
                "error": str(e),
                "sources": []
            }
    
    def _detect_relevant_agents(self, message: str) -> List[AgentType]:
        """Détecte les agents pertinents pour la requête avec stratégie RAG-first"""
        query_lower = message.lower()
        detected_agents = []
        
        # 🔍 DÉTECTION AUTOMATIQUE DE LANGUE NON-FRANÇAISE
        # Détecter si le message contient des caractères non-latins ou des mots-clés anglais
        has_arabic = bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', message))
        has_tamazight = bool(re.search(r'[\u2D30-\u2D7F]', message))
        has_english = any(word in query_lower for word in ["the", "and", "is", "are", "was", "were", "with", "for", "but", "or"])
        
        # Si une langue non-française est détectée, ajouter l'agent multilingue en priorité
        if has_arabic or has_tamazight or has_english:
            detected_agents.append(AgentType.MULTILINGUAL_DETECTOR)
            logger.info(f"🌐 Langue non-française détectée - Ajout de l'agent multilingue")
        
        # Vérification des patterns pour les agents spécialisés
        for agent_type, patterns in self.route_patterns.items():
            # Ignorer RAG_SYSTEM car il sera traité séparément
            if agent_type == AgentType.RAG_SYSTEM:
                continue
                
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # Éviter les doublons
                    if agent_type not in detected_agents:
                        detected_agents.append(agent_type)
                    break
        
        # Ajout du RAG_SYSTEM en premier pour vérification prioritaire
        # Le RAG est toujours pertinent pour enrichir le contexte
        detected_agents.insert(0, AgentType.RAG_SYSTEM)
        
        # Si aucun agent spécialisé détecté, garder seulement RAG
        if len(detected_agents) == 1:
            logger.info("🔍 Aucun agent spécialisé détecté, utilisation du RAG uniquement")
        
        logger.info(f"🤖 Agents détectés: {[agent.value for agent in detected_agents]}")
        return detected_agents
    
    async def _get_agent_responses(self, state: AgentState, agents: List[AgentType], agents_map: dict) -> List[Dict[str, Any]]:
        """Récupère les réponses des agents avec stratégie RAG-first"""
        responses = []
        
        # 1. 🔍 VÉRIFICATION RAG EN PREMIER - Appel direct au système RAG
        logger.info("🔍 Vérification RAG en premier...")
        rag_response = await self._check_rag_first(state.current_message)
        
        if rag_response and rag_response.get("success"):
            responses.append(rag_response)
            logger.info("✅ RAG a trouvé une réponse pertinente")
        else:
            logger.info("❌ RAG n'a pas trouvé de réponse pertinente")
        
        # 2. 🌐 TRAITEMENT MULTILINGUE EN PRIORITÉ (si présent)
        detected_language = "fr"  # Défaut français
        multilingual_agent = None
        
        # Chercher l'agent multilingue dans la liste
        for agent_type in agents:
            if agent_type == AgentType.MULTILINGUAL_DETECTOR:
                multilingual_agent = agents_map.get(agent_type)
                break
        
        # Traiter l'agent multilingue en premier s'il est présent
        if multilingual_agent:
            try:
                logger.info("🌐 Traitement de l'agent multilingue en priorité...")
                agent_state = self._prepare_agent_state(state, AgentType.MULTILINGUAL_DETECTOR)
                result = await multilingual_agent.process(agent_state)
                
                # Extraire la langue détectée
                if "detected_language" in result:
                    detected_language = result["detected_language"]
                    logger.info(f"🌐 Langue détectée: {detected_language}")
                
                # Si l'agent multilingue a généré une réponse complète, l'utiliser
                if result.get("response") and result.get("confidence", 0) > 0.7:
                    responses.append({
                        "agent_type": "multilingual_detector",
                        "response": result["response"],
                        "confidence": result.get("confidence", 0.8),
                        "sources": result.get("sources", []),
                        "success": True,
                        "detected_language": detected_language
                    })
                    logger.info("✅ Agent multilingue a généré une réponse complète")
                    return responses  # Retourner directement si réponse complète
                
                # Sinon, continuer avec les autres agents
                logger.info("🌐 Agent multilingue a détecté la langue, traitement des autres agents...")
                
            except Exception as e:
                logger.error(f"❌ Erreur avec l'agent multilingue: {e}")
        
        # 3. 🤖 APPEL DES AUTRES AGENTS SPÉCIALISÉS
        for agent_type in agents:
            # Ignorer RAG_SYSTEM et MULTILINGUAL_DETECTOR car déjà traités
            if agent_type in [AgentType.RAG_SYSTEM, AgentType.MULTILINGUAL_DETECTOR]:
                continue
                
            agent = agents_map.get(agent_type)
            if agent:
                try:
                    # Préparation de l'état pour l'agent avec la langue détectée
                    agent_state = self._prepare_agent_state(state, agent_type)
                    agent_state.detected_language = detected_language  # Passer la langue détectée
                    
                    # Appel de l'agent
                    if agent_type == AgentType.TASK_DIVIDER:
                        result = await agent.process(agent_state, agents_map)
                    else:
                        result = await agent.process(agent_state)
                    
                    # Validation et nettoyage de la réponse
                    cleaned_response = self._clean_agent_response(result, agent_type)
                    
                    if cleaned_response:
                        responses.append({
                            "agent_type": agent_type.value,
                            "response": cleaned_response,
                            "confidence": result.get("confidence", 0.7),
                            "sources": result.get("sources", []),
                            "success": True,
                            "detected_language": detected_language
                        })
                        logger.info(f"✅ {agent_type.value} a généré une réponse")
                    else:
                        responses.append({
                            "agent_type": agent_type.value,
                            "response": f"L'agent {agent_type.value} n'a pas pu générer de réponse.",
                            "confidence": 0.0,
                            "sources": [],
                            "success": False
                        })
                        logger.info(f"❌ {agent_type.value} n'a pas généré de réponse")
                        
                except Exception as e:
                    responses.append({
                        "agent_type": agent_type.value,
                        "response": f"Erreur lors de l'appel à l'agent {agent_type.value}: {str(e)}",
                        "confidence": 0.0,
                        "sources": [],
                        "success": False,
                        "error": str(e)
                    })
                    logger.error(f"❌ Erreur avec {agent_type.value}: {e}")
            else:
                responses.append({
                    "agent_type": agent_type.value,
                    "response": f"Agent {agent_type.value} non disponible.",
                    "confidence": 0.0,
                    "sources": [],
                    "success": False
                })
                logger.warning(f"⚠️ {agent_type.value} non disponible")
        
        return responses
    
    async def _check_rag_first(self, query: str) -> Dict[str, Any]:
        """Vérifie d'abord le système RAG pour une réponse pertinente"""
        try:
            logger.info(f"🔍 Appel direct au système RAG pour: {query[:50]}...")
            
            # Appel direct au service RAG
            rag_result = await self.rag_service.query(
                query=query,
                language="fr",
                max_results=3
            )
            
            # Vérification de la qualité de la réponse RAG
            if self._is_rag_response_quality(rag_result):
                return {
                    "agent_type": AgentType.RAG_SYSTEM.value,
                    "response": rag_result.get("answer", ""),
                    "confidence": rag_result.get("confidence", 0.8),
                    "sources": rag_result.get("sources", []),
                    "success": True,
                    "rag_score": rag_result.get("similarity_score", 0.0)
                }
            else:
                logger.info("❌ Réponse RAG de qualité insuffisante")
                return {
                    "agent_type": AgentType.RAG_SYSTEM.value,
                    "response": "Aucune information pertinente trouvée dans la base de connaissances.",
                    "confidence": 0.0,
                    "sources": [],
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'appel RAG: {e}")
            return {
                "agent_type": AgentType.RAG_SYSTEM.value,
                "response": f"Erreur lors de la consultation de la base de connaissances: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "success": False,
                "error": str(e)
            }
    
    def _is_rag_response_quality(self, rag_result: Dict[str, Any]) -> bool:
        """Vérifie si la réponse RAG est de qualité suffisante"""
        try:
            # Vérification de la présence d'une réponse
            answer = rag_result.get("answer", "")
            if not answer or len(answer.strip()) < 20:
                return False
            
            # Vérification du score de similarité
            similarity_score = rag_result.get("similarity_score", 0.0)
            if similarity_score < 0.6:  # Seuil de qualité
                return False
            
            # Vérification de la confiance
            confidence = rag_result.get("confidence", 0.0)
            if confidence < 0.5:  # Seuil de confiance
                return False
            
            # Vérification des sources
            sources = rag_result.get("sources", [])
            if not sources:
                return False
            
            logger.info(f"✅ Qualité RAG validée - Score: {similarity_score:.2f}, Confiance: {confidence:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de qualité RAG: {e}")
            return False
    
    def _prepare_agent_state(self, state: AgentState, agent_type: AgentType) -> AgentState:
        """Prépare l'état spécifique pour un agent"""
        # Création d'un nouvel état avec le bon agent_route
        agent_state = AgentState(
            current_message=state.current_message,
            detected_language=state.detected_language,
            user_intent=state.user_intent,
            agent_route=agent_type,
            context=state.context,
            response="",
            confidence=0.0,
            sources=[],
            processing_history=state.processing_history
        )
        return agent_state
    
    def _clean_agent_response(self, result: Dict[str, Any], agent_type: AgentType) -> str:
        """Nettoie et valide la réponse d'un agent"""
        response = result.get("response", "")
        
        # Vérification que la réponse est valide
        if not response or not isinstance(response, str):
            return ""
        
        # Suppression des réponses par défaut
        default_responses = [
            "solar nasih est un assistant",
            "je n'ai pas pu traiter",
            "aucune réponse générée"
        ]
        
        response_lower = response.lower()
        for default in default_responses:
            if default in response_lower:
                return ""
        
        return response.strip()
    
    async def _build_final_response(self, agent_responses: List[Dict[str, Any]], detected_agents: List[AgentType]) -> str:
        """Construit la réponse finale en format ChatGPT avec résumé automatique"""
        successful_responses = [r for r in agent_responses if r["success"] and r["response"]]
        
        if not successful_responses:
            return self._get_fallback_response()
        
        # 🌐 DÉTECTION DE LA LANGUE POUR TRADUCTION
        detected_language = "fr"  # Défaut français
        for response in successful_responses:
            if "detected_language" in response:
                detected_language = response["detected_language"]
                break
        
        # NOUVELLE APPROCHE : Réponse structurée style ChatGPT
        # 1. Combiner les meilleures réponses
        combined_response = self._combine_agent_responses(successful_responses)
        
        # 2. Utiliser l'agent résumeur pour formater la réponse
        summarized_response = await self._summarize_with_agent(combined_response)
        
        # 3. Si l'agent résumeur échoue, utiliser le formatage automatique
        if not summarized_response or "Erreur" in summarized_response:
            summarized_response = self._format_chatgpt_style(combined_response)
        
        # 🌐 TRADUCTION AUTOMATIQUE SI NÉCESSAIRE
        if detected_language != "fr":
            try:
                from agents.multilingual_detector import MultilingualDetectorAgent
                multilingual_agent = MultilingualDetectorAgent()
                
                translation_result = await multilingual_agent.translate_text(
                    summarized_response, "fr", detected_language
                )
                
                if translation_result.get("confidence", 0) > 0.5:
                    summarized_response = translation_result["translated_text"]
                    logger.info(f"🌐 Réponse traduite en {detected_language}")
                    
            except Exception as e:
                logger.error(f"🌐 Erreur lors de la traduction: {e}")
        
        return summarized_response
    
    def _combine_agent_responses(self, responses: List[Dict[str, Any]]) -> str:
        """Combine les réponses des agents en une seule réponse"""
        if not responses:
            return ""
        
        # Prendre la meilleure réponse (la plus pertinente)
        best_response = max(responses, key=lambda x: x.get("confidence", 0))
        
        # Si c'est une réponse RAG de qualité, la prioriser
        rag_responses = [r for r in responses if r["agent_type"] == AgentType.RAG_SYSTEM.value]
        if rag_responses:
            best_rag = max(rag_responses, key=lambda x: x.get("rag_score", 0))
            if best_rag.get("rag_score", 0) > 0.6:
                return best_rag["response"]
        
        return best_response["response"]
    
    async def _summarize_with_agent(self, response: str) -> str:
        """Utilise l'agent résumeur pour formater la réponse"""
        try:
            from agents.response_summarizer import ResponseSummarizerAgent
            from models.schemas import AgentState
            
            # Créer l'agent résumeur
            summarizer = ResponseSummarizerAgent()
            
            # Récupérer la question originale depuis le contexte
            user_question = ""
            if hasattr(self, 'current_user_question'):
                user_question = self.current_user_question
            
            # Créer l'état avec la réponse à résumer et la question originale
            state = AgentState(
                current_message=response,
                detected_language="fr",
                user_intent="",
                agent_route=AgentType.RESPONSE_SUMMARIZER,
                context={"user_question": user_question},
                response="",
                confidence=0.0,
                sources=[],
                processing_history=[]
            )
            
            # Traiter avec l'agent résumeur
            result = await summarizer.process(state)
            
            return result.get("response", response)
            
        except Exception as e:
            logger.error(f"Erreur avec l'agent résumeur: {e}")
            return response
    
    def _format_chatgpt_style(self, response: str) -> str:
        """Formate la réponse en style ChatGPT automatiquement"""
        try:
            # Nettoyer la réponse
            cleaned_response = self._clean_response(response)
            
            # Générer un résumé automatique
            summary = self._generate_auto_summary(cleaned_response)
            
            # Extraire les points clés
            key_points = self._extract_key_points(cleaned_response)
            
            # Formater en style ChatGPT
            formatted_response = f"""**{summary}**

{key_points}

**Détails :**
{cleaned_response[:300]}{'...' if len(cleaned_response) > 300 else ''}"""
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Erreur formatage ChatGPT: {e}")
            return response
    
    def _clean_response(self, response: str) -> str:
        """Nettoie la réponse des métadonnées"""
        if not response:
            return ""
        
        # Supprimer les métadonnées et émojis
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ignorer les lignes avec métadonnées
            if any(skip in line.lower() for skip in [
                "confiance:", "similarité:", "score:", "agent:", "base de connaissances",
                "🟢", "🟡", "🔴", "📚", "🤖", "🔍", "**analyse de votre demande**"
            ]):
                continue
            
            # Ignorer les lignes trop techniques ou verbeuses
            if any(verbose in line.lower() for verbose in [
                "calcul de production énergétique:", "estimation des économies annuelles:",
                "calcul du retour sur investissement:", "dimensionnement optimal:",
                "impact environnemental:", "pour calculer le roi", "méthode:", "facteurs:"
            ]):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _generate_auto_summary(self, response: str) -> str:
        """Génère un résumé automatique"""
        try:
            # Extraire les informations principales
            lines = response.split('\n')
            summary_parts = []
            
            for line in lines[:3]:  # Prendre les 3 premières lignes utiles
                if any(keyword in line.lower() for keyword in ['kwh', 'kwc', '€', 'ans', 'production', 'coût', 'prix']):
                    summary_parts.append(line)
            
            if summary_parts:
                return summary_parts[0][:100] + "..."
            else:
                return "Informations sur l'énergie solaire disponibles."
                
        except Exception as e:
            logger.error(f"Erreur génération résumé auto: {e}")
            return "Résumé de la réponse généré."
    
    def _extract_key_points(self, response: str) -> str:
        """Extrait les points clés d'une réponse"""
        try:
            # Extraction automatique des points clés
            lines = response.split('\n')
            key_points = []
            
            # Chercher les lignes avec des données importantes
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Détecter les lignes avec des données chiffrées
                if any(keyword in line.lower() for keyword in ['kwh', 'kwc', '€', 'ans', 'production', 'coût', 'prix', 'économie']):
                    key_points.append(line)
                elif len(line) > 10 and len(line) < 100 and not line.startswith('*'):
                    key_points.append(line)
            
            # Limiter à 5 points maximum
            if len(key_points) > 5:
                key_points = key_points[:5]
            
            if key_points:
                return "**Points clés :**\n" + "\n".join([f"• {point}" for point in key_points])
            else:
                return "**Informations principales :**\n" + response[:200] + "..."
                
        except Exception as e:
            logger.error(f"Erreur extraction points clés: {e}")
            return "**Informations :**\n" + response[:200] + "..."
    
    def _get_fallback_response(self) -> str:
        """Génère une réponse de fallback avec Gemini"""
        try:
            # Utilisation de Gemini pour une réponse de fallback
            fallback_prompt = """
            Tu es Solar Nasih, un assistant spécialisé en énergie solaire.
            L'utilisateur a posé une question mais les agents spécialisés n'ont pas pu répondre.
            Génère une réponse utile et informative en français, en restant dans le domaine de l'énergie solaire.
            """
            # Note: Cette méthode nécessiterait l'intégration avec Gemini
            return "Je n'ai pas pu traiter votre demande avec les agents spécialisés, mais je reste à votre disposition pour toute question sur l'énergie solaire."
        except:
            return "Solar Nasih est un assistant intelligent dédié à l'énergie solaire. Posez-moi vos questions sur l'installation, la réglementation, la simulation, la certification ou le financement."
    
    def _calculate_overall_confidence(self, agent_responses: List[Dict[str, Any]]) -> float:
        """Calcule la confiance globale basée sur les réponses des agents"""
        successful_responses = [r for r in agent_responses if r["success"]]
        
        if not successful_responses:
            return 0.3
        
        confidences = [r["confidence"] for r in successful_responses]
        return sum(confidences) / len(confidences)
    
    def _collect_sources(self, agent_responses: List[Dict[str, Any]]) -> List[str]:
        """Collecte toutes les sources des agents"""
        sources = set()
        for response in agent_responses:
            if response["success"]:
                sources.update(response.get("sources", []))
        return list(sources)
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        """Le diviseur de tâches peut toujours traiter les requêtes"""
        return 1.0