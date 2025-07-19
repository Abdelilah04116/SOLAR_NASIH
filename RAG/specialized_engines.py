"""
Moteurs spécialisés et extensions SMA pour l'agent RAG
Architecture modulaire pour ajouter des capacités spécialisées
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Protocol, runtime_checkable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import json

# Imports pour les agents spécialisés
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)

# ==================== Interfaces et Protocoles ====================

@runtime_checkable
class SpecializedEngine(Protocol):
    """Interface pour les moteurs spécialisés"""
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> bool:
        """Détermine si ce moteur peut traiter la requête"""
        ...
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Traite la requête avec ce moteur spécialisé"""
        ...
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités de ce moteur"""
        ...

class EngineType(Enum):
    """Types de moteurs spécialisés"""
    MATHEMATICAL = "mathematical"
    TECHNICAL = "technical"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    FACTUAL = "factual"
    CONVERSATIONAL = "conversational"

@dataclass
class EngineResponse:
    """Réponse d'un moteur spécialisé"""
    content: str
    confidence: float
    engine_type: EngineType
    processing_time: float
    metadata: Dict[str, Any]
    sources_used: List[str] = None

# ==================== Moteurs Spécialisés ====================

class MathematicalEngine:
    """Moteur spécialisé pour les questions mathématiques et calculs"""
    
    def __init__(self, gemini_llm):
        self.llm = gemini_llm
        self.engine_type = EngineType.MATHEMATICAL
        
        self.math_prompt = """
        Vous êtes un expert en mathématiques et calculs. Répondez aux questions mathématiques
        avec précision et clarté.
        
        Question: {query}
        Contexte disponible: {context}
        
        Instructions:
        1. Fournissez des calculs étape par étape
        2. Expliquez le raisonnement mathématique
        3. Utilisez des notations mathématiques claires
        4. Vérifiez vos calculs
        5. Indiquez les limites ou approximations
        
        Réponse mathématique:
        """
        
        self.math_keywords = [
            'calcul', 'équation', 'formule', 'mathématique', 'statistique',
            'probabilité', 'algèbre', 'géométrie', 'trigonométrie',
            'dérivée', 'intégrale', 'fonction', 'graphique', 'analyse',
            'nombre', 'pourcentage', 'ratio', 'moyenne', 'médiane'
        ]
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> bool:
        """Détermine si la requête est mathématique"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.math_keywords)
    
    async def process(self, query: str, context: Dict[str, Any]) -> EngineResponse:
        """Traite une requête mathématique"""
        import time
        start_time = time.time()
        
        try:
            # Préparer le contexte mathématique
            math_context = self._extract_math_context(context)
            
            prompt = self.math_prompt.format(
                query=query,
                context=math_context
            )
            
            response = await self.llm.generate_response(prompt)
            
            processing_time = time.time() - start_time
            
            return EngineResponse(
                content=response,
                confidence=0.9,  # Haute confiance pour les calculs
                engine_type=self.engine_type,
                processing_time=processing_time,
                metadata={
                    "math_keywords_found": [kw for kw in self.math_keywords if kw in query.lower()],
                    "context_type": "mathematical"
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur moteur mathématique: {e}")
            return EngineResponse(
                content=f"Erreur lors du traitement mathématique: {str(e)}",
                confidence=0.0,
                engine_type=self.engine_type,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    def _extract_math_context(self, context: Dict[str, Any]) -> str:
        """Extrait le contexte pertinent pour les mathématiques"""
        math_context_parts = []
        
        chunks = context.get('relevant_chunks', [])
        for chunk in chunks:
            content = chunk.get('content', '')
            # Rechercher des formules, nombres, tableaux
            if any(indicator in content.lower() for indicator in ['=', '%', 'tableau', 'graphique', 'données']):
                math_context_parts.append(f"Source: {content[:300]}...")
        
        return "\n".join(math_context_parts) if math_context_parts else "Aucun contexte mathématique spécifique."
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités mathématiques"""
        return [
            "Calculs arithmétiques",
            "Résolution d'équations",
            "Analyse statistique",
            "Géométrie et trigonométrie",
            "Analyse de données numériques"
        ]

class TechnicalEngine:
    """Moteur spécialisé pour les questions techniques et d'ingénierie"""
    
    def __init__(self, gemini_llm):
        self.llm = gemini_llm
        self.engine_type = EngineType.TECHNICAL
        
        self.technical_prompt = """
        Vous êtes un expert technique avec une expertise approfondie en ingénierie,
        informatique, et sciences appliquées.
        
        Question technique: {query}
        Documentation disponible: {context}
        
        Instructions:
        1. Fournissez des explications techniques précises
        2. Incluez des détails d'implémentation si pertinent
        3. Mentionnez les bonnes pratiques
        4. Identifiez les risques ou limitations
        5. Suggérez des ressources additionnelles
        
        Réponse technique détaillée:
        """
        
        self.technical_keywords = [
            'algorithme', 'architecture', 'système', 'réseau', 'base de données',
            'programmation', 'code', 'framework', 'api', 'protocole',
            'sécurité', 'performance', 'optimisation', 'debug', 'test',
            'infrastructure', 'cloud', 'serveur', 'client', 'interface'
        ]
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> bool:
        """Détermine si la requête est technique"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.technical_keywords)
    
    async def process(self, query: str, context: Dict[str, Any]) -> EngineResponse:
        """Traite une requête technique"""
        import time
        start_time = time.time()
        
        try:
            # Analyser le type de question technique
            tech_type = self._analyze_technical_type(query)
            
            # Préparer le contexte technique
            tech_context = self._extract_technical_context(context, tech_type)
            
            prompt = self.technical_prompt.format(
                query=query,
                context=tech_context
            )
            
            response = await self.llm.generate_response(prompt)
            
            processing_time = time.time() - start_time
            
            return EngineResponse(
                content=response,
                confidence=0.85,
                engine_type=self.engine_type,
                processing_time=processing_time,
                metadata={
                    "technical_type": tech_type,
                    "keywords_found": [kw for kw in self.technical_keywords if kw in query.lower()]
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur moteur technique: {e}")
            return EngineResponse(
                content=f"Erreur lors du traitement technique: {str(e)}",
                confidence=0.0,
                engine_type=self.engine_type,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    def _analyze_technical_type(self, query: str) -> str:
        """Analyse le type de question technique"""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ['code', 'programmation', 'algorithme']):
            return "programming"
        elif any(kw in query_lower for kw in ['réseau', 'protocole', 'tcp', 'http']):
            return "networking"
        elif any(kw in query_lower for kw in ['base de données', 'sql', 'requête']):
            return "database"
        elif any(kw in query_lower for kw in ['sécurité', 'cryptage', 'authentification']):
            return "security"
        else:
            return "general_technical"
    
    def _extract_technical_context(self, context: Dict[str, Any], tech_type: str) -> str:
        """Extrait le contexte technique pertinent"""
        chunks = context.get('relevant_chunks', [])
        tech_chunks = []
        
        for chunk in chunks:
            content = chunk.get('content', '').lower()
            # Filtrer selon le type technique
            if tech_type == "programming" and any(kw in content for kw in ['code', 'fonction', 'class']):
                tech_chunks.append(chunk.get('content', ''))
            elif tech_type == "networking" and any(kw in content for kw in ['réseau', 'protocole', 'tcp']):
                tech_chunks.append(chunk.get('content', ''))
            else:
                tech_chunks.append(chunk.get('content', ''))
        
        return "\n".join(tech_chunks[:3])  # Limiter à 3 chunks les plus pertinents
    
    def get_capabilities(self) -> List[str]:
        return [
            "Architecture logicielle",
            "Programmation et algorithmes",
            "Réseaux et protocoles",
            "Bases de données",
            "Sécurité informatique",
            "Optimisation de performance"
        ]

class AnalyticalEngine:
    """Moteur spécialisé pour l'analyse de données et insights"""
    
    def __init__(self, gemini_llm):
        self.llm = gemini_llm
        self.engine_type = EngineType.ANALYTICAL
        
        self.analytical_prompt = """
        Vous êtes un expert en analyse de données avec une expertise en statistiques,
        business intelligence et data science.
        
        Demande d'analyse: {query}
        Données disponibles: {context}
        
        Instructions:
        1. Analysez les données de manière structurée
        2. Identifiez les tendances et patterns
        3. Fournissez des insights actionnables
        4. Quantifiez vos observations quand possible
        5. Suggérez des analyses complémentaires
        
        Analyse détaillée:
        """
        
        self.analytical_keywords = [
            'analyse', 'tendance', 'pattern', 'insight', 'correlation',
            'données', 'métrique', 'kpi', 'performance', 'évolution',
            'comparaison', 'benchmark', 'croissance', 'diminution',
            'distribution', 'variance', 'écart-type'
        ]
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> bool:
        """Détermine si la requête nécessite une analyse"""
        query_lower = query.lower()
        
        # Vérifier les mots-clés analytiques
        has_analytical_keywords = any(keyword in query_lower for keyword in self.analytical_keywords)
        
        # Vérifier la présence de données tabulaires
        chunks = context.get('relevant_chunks', [])
        has_tables = any(chunk.get('chunk_type') == 'table' for chunk in chunks)
        
        return has_analytical_keywords or has_tables
    
    async def process(self, query: str, context: Dict[str, Any]) -> EngineResponse:
        """Traite une requête analytique"""
        import time
        start_time = time.time()
        
        try:
            # Extraire et structurer les données
            structured_data = self._structure_data(context)
            
            prompt = self.analytical_prompt.format(
                query=query,
                context=structured_data
            )
            
            response = await self.llm.generate_response(prompt)
            
            processing_time = time.time() - start_time
            
            return EngineResponse(
                content=response,
                confidence=0.8,
                engine_type=self.engine_type,
                processing_time=processing_time,
                metadata={
                    "data_sources": len(context.get('relevant_chunks', [])),
                    "tables_found": len([c for c in context.get('relevant_chunks', []) if c.get('chunk_type') == 'table'])
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur moteur analytique: {e}")
            return EngineResponse(
                content=f"Erreur lors de l'analyse: {str(e)}",
                confidence=0.0,
                engine_type=self.engine_type,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    def _structure_data(self, context: Dict[str, Any]) -> str:
        """Structure les données pour l'analyse"""
        chunks = context.get('relevant_chunks', [])
        structured_parts = []
        
        # Séparer par type de contenu
        tables = [c for c in chunks if c.get('chunk_type') == 'table']
        texts = [c for c in chunks if c.get('chunk_type') == 'text']
        
        if tables:
            structured_parts.append("=== DONNÉES TABULAIRES ===")
            for i, table in enumerate(tables, 1):
                structured_parts.append(f"Tableau {i}: {table.get('content', '')[:500]}...")
        
        if texts:
            structured_parts.append("=== INFORMATIONS CONTEXTUELLES ===")
            for text in texts[:2]:  # Limiter à 2 textes
                structured_parts.append(f"Contexte: {text.get('content', '')[:300]}...")
        
        return "\n".join(structured_parts)
    
    def get_capabilities(self) -> List[str]:
        return [
            "Analyse de tendances",
            "Identification de patterns",
            "Analyse comparative",
            "Insights métiers",
            "Recommandations data-driven"
        ]

# ==================== Système Multi-Agents (SMA) ====================

class AgentCoordinator:
    """Coordinateur pour le système multi-agents"""
    
    def __init__(self, gemini_llm):
        self.llm = gemini_llm
        self.engines = {}
        self.decision_history = []
        
        # Prompt pour le routage intelligent
        self.routing_prompt = """
        Analysez cette requête et déterminez quel(s) moteur(s) spécialisé(s) 
        devrait(ent) la traiter.
        
        Requête: {query}
        Moteurs disponibles: {available_engines}
        
        Pour chaque moteur, évaluez:
        1. Pertinence (0-10)
        2. Confiance dans le traitement (0-10)
        3. Justification
        
        Format de réponse:
        MOTEUR: [nom]
        PERTINENCE: [score]
        CONFIANCE: [score]
        JUSTIFICATION: [explication]
        
        RECOMMANDATION: [moteur principal recommandé]
        """
    
    def register_engine(self, name: str, engine: SpecializedEngine):
        """Enregistre un moteur spécialisé"""
        self.engines[name] = engine
        logger.info(f"Moteur {name} enregistré avec capacités: {engine.get_capabilities()}")
    
    async def route_query(self, query: str, context: Dict[str, Any]) -> List[str]:
        """Détermine quels moteurs utiliser pour une requête"""
        available_engines = []
        
        # Vérifier quels moteurs peuvent traiter la requête
        for name, engine in self.engines.items():
            if engine.can_handle(query, context):
                available_engines.append({
                    "name": name,
                    "capabilities": engine.get_capabilities()
                })
        
        if not available_engines:
            return ["default"]  # Moteur par défaut
        
        # Si un seul moteur peut traiter, l'utiliser
        if len(available_engines) == 1:
            return [available_engines[0]["name"]]
        
        # Utiliser l'IA pour le routage intelligent
        try:
            engines_info = "\n".join([
                f"- {eng['name']}: {', '.join(eng['capabilities'])}"
                for eng in available_engines
            ])
            
            prompt = self.routing_prompt.format(
                query=query,
                available_engines=engines_info
            )
            
            response = await self.llm.generate_response(prompt)
            
            # Parser la réponse pour extraire la recommandation
            recommended_engine = self._parse_routing_response(response, available_engines)
            
            return [recommended_engine] if recommended_engine else [available_engines[0]["name"]]
            
        except Exception as e:
            logger.error(f"Erreur routage: {e}")
            return [available_engines[0]["name"]]  # Fallback sur le premier disponible
    
    def _parse_routing_response(self, response: str, available_engines: List[Dict]) -> Optional[str]:
        """Parse la réponse de routage de l'IA"""
        lines = response.strip().split('\n')
        
        for line in lines:
            if line.startswith("RECOMMANDATION:"):
                recommended = line.split(":", 1)[1].strip()
                # Vérifier que le moteur recommandé est disponible
                engine_names = [eng["name"] for eng in available_engines]
                for name in engine_names:
                    if name.lower() in recommended.lower():
                        return name
        
        return None
    
    async def process_with_engines(self, query: str, context: Dict[str, Any], 
                                 engine_names: List[str]) -> List[EngineResponse]:
        """Traite une requête avec les moteurs spécifiés"""
        responses = []
        
        for engine_name in engine_names:
            if engine_name in self.engines:
                try:
                    response = await self.engines[engine_name].process(query, context)
                    responses.append(response)
                except Exception as e:
                    logger.error(f"Erreur moteur {engine_name}: {e}")
            elif engine_name == "default":
                # Traitement par défaut (moteur principal)
                responses.append(EngineResponse(
                    content="Traitement par le moteur principal",
                    confidence=0.7,
                    engine_type=EngineType.CONVERSATIONAL,
                    processing_time=0.0,
                    metadata={"engine": "default"}
                ))
        
        return responses

class MultiAgentResponseSynthesizer:
    """Synthétise les réponses de plusieurs agents/moteurs"""
    
    def __init__(self, gemini_llm):
        self.llm = gemini_llm
        
        self.synthesis_prompt = """
        Vous devez synthétiser plusieurs réponses d'experts spécialisés 
        pour créer une réponse complète et cohérente.
        
        Question originale: {query}
        
        Réponses des experts:
        {expert_responses}
        
        Instructions:
        1. Intégrez les meilleures informations de chaque expert
        2. Résolvez les éventuelles contradictions
        3. Organisez la réponse de manière logique
        4. Indiquez les domaines d'expertise utilisés
        5. Mentionnez les niveaux de confiance
        
        Réponse synthétisée:
        """
    
    async def synthesize_responses(self, query: str, 
                                 responses: List[EngineResponse]) -> EngineResponse:
        """Synthétise plusieurs réponses d'experts"""
        if not responses:
            return EngineResponse(
                content="Aucune réponse disponible",
                confidence=0.0,
                engine_type=EngineType.CONVERSATIONAL,
                processing_time=0.0,
                metadata={}
            )
        
        if len(responses) == 1:
            return responses[0]
        
        try:
            # Préparer les réponses des experts
            expert_responses = []
            total_confidence = 0
            
            for i, response in enumerate(responses, 1):
                expert_info = f"""
                Expert {i} ({response.engine_type.value}):
                Confiance: {response.confidence:.2f}
                Réponse: {response.content}
                ---
                """
                expert_responses.append(expert_info)
                total_confidence += response.confidence
            
            expert_text = "\n".join(expert_responses)
            
            prompt = self.synthesis_prompt.format(
                query=query,
                expert_responses=expert_text
            )
            
            synthesized = await self.llm.generate_response(prompt)
            
            # Calculer la confiance moyenne pondérée
            avg_confidence = total_confidence / len(responses)
            
            return EngineResponse(
                content=synthesized,
                confidence=min(avg_confidence, 1.0),
                engine_type=EngineType.CONVERSATIONAL,
                processing_time=sum(r.processing_time for r in responses),
                metadata={
                    "engines_used": [r.engine_type.value for r in responses],
                    "expert_count": len(responses),
                    "synthesis_method": "multi_expert"
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur synthèse: {e}")
            # Fallback: retourner la réponse avec la plus haute confiance
            best_response = max(responses, key=lambda r: r.confidence)
            return best_response

# ==================== Intégration avec l'Agent Principal ====================

class EnhancedRAGAgent:
    """Agent RAG amélioré avec moteurs spécialisés et SMA"""
    
    def __init__(self, base_agent, gemini_llm):
        self.base_agent = base_agent
        self.coordinator = AgentCoordinator(gemini_llm)
        self.synthesizer = MultiAgentResponseSynthesizer(gemini_llm)
        
        # Enregistrer les moteurs spécialisés
        self._register_specialized_engines(gemini_llm)
    
    def _register_specialized_engines(self, gemini_llm):
        """Enregistre tous les moteurs spécialisés"""
        self.coordinator.register_engine("mathematical", MathematicalEngine(gemini_llm))
        self.coordinator.register_engine("technical", TechnicalEngine(gemini_llm))
        self.coordinator.register_engine("analytical", AnalyticalEngine(gemini_llm))
        
        logger.info("Moteurs spécialisés enregistrés")
    
    async def process_query_enhanced(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Traite une requête avec les moteurs spécialisés"""
        # Étape 1: Traitement de base avec l'agent principal
        base_result = await self.base_agent.process_query(query, session_id)
        
        # Étape 2: Routage vers les moteurs spécialisés
        context = {
            'relevant_chunks': base_result.get('sources', []),
            'search_intent': base_result.get('search_intent', ''),
            'expanded_queries': base_result.get('expanded_queries', [])
        }
        
        engine_names = await self.coordinator.route_query(query, context)
        
        # Étape 3: Traitement par les moteurs spécialisés
        specialized_responses = await self.coordinator.process_with_engines(
            query, context, engine_names
        )
        
        # Étape 4: Synthèse des réponses
        if specialized_responses:
            # Ajouter la réponse de base comme une réponse d'expert
            base_response = EngineResponse(
                content=base_result['response'],
                confidence=base_result['confidence'],
                engine_type=EngineType.CONVERSATIONAL,
                processing_time=0.0,
                metadata={"engine": "base_rag"}
            )
            
            all_responses = [base_response] + specialized_responses
            final_response = await self.synthesizer.synthesize_responses(query, all_responses)
            
            # Mettre à jour le résultat
            base_result.update({
                'response': final_response.content,
                'confidence': final_response.confidence,
                'engines_used': final_response.metadata.get('engines_used', []),
                'specialized_processing': True,
                'synthesis_metadata': final_response.metadata
            })
        
        return base_result

# ==================== Factory et Configuration ====================

def create_enhanced_rag_agent(base_agent, gemini_api_key: str) -> EnhancedRAGAgent:
    """Crée un agent RAG amélioré avec moteurs spécialisés"""
    from rag_agent_langgraph import GeminiLLM, GeminiConfig
    
    gemini_config = GeminiConfig(api_key=gemini_api_key)
    gemini_llm = GeminiLLM(gemini_config)
    
    return EnhancedRAGAgent(base_agent, gemini_llm)

# ==================== Exemple d'utilisation ====================

async def demo_specialized_engines():
    """Démonstration des moteurs spécialisés"""
    from rag_agent_langgraph import create_rag_agent
    from pipeline import create_pipeline
    from config import RAGPipelineConfig
    
    # Configuration de base
    rag_config = RAGPipelineConfig()
    rag_pipeline = create_pipeline(rag_config)
    
    GEMINI_API_KEY = "your-gemini-api-key-here"
    
    # Créer l'agent de base
    base_agent = create_rag_agent(rag_pipeline, GEMINI_API_KEY)
    
    # Créer l'agent amélioré
    enhanced_agent = create_enhanced_rag_agent(base_agent, GEMINI_API_KEY)
    
    # Tester différents types de requêtes
    test_queries = [
        "Calculez la moyenne des ventes du premier trimestre",  # Mathématique + Analytique
        "Comment optimiser les performances d'une base de données?",  # Technique
        "Analysez les tendances de croissance dans les données",  # Analytique
        "Expliquez l'algorithme de tri rapide",  # Technique
        "Quelle est la probabilité de succès du projet?"  # Mathématique
    ]
    
    for query in test_queries:
        print(f"\n🔍 Requête: {query}")
        print("=" * 60)
        
        result = await enhanced_agent.process_query_enhanced(query)
        
        print(f"🤖 Moteurs utilisés: {result.get('engines_used', ['base'])}")
        print(f"📊 Confiance: {result['confidence']:.3f}")
        print(f"🎯 Traitement spécialisé: {result.get('specialized_processing', False)}")
        print(f"📝 Réponse: {result['response'][:300]}...")
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(demo_specialized_engines())