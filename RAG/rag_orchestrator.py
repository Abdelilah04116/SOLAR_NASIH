"""
Orchestrateur RAG complet intégrant tous les composants
Interface simplifiée pour l'utilisation de l'ensemble du système
"""
import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json
import time

# Imports des modules créés
from config import RAGPipelineConfig
from pipeline import create_pipeline
from rag_agent_langgraph import create_rag_agent, GeminiConfig
from specialized_engines import create_enhanced_rag_agent

logger = logging.getLogger(__name__)

# ==================== Configuration Globale ====================

@dataclass
class RAGSystemConfig:
    """Configuration complète du système RAG"""
    # Configuration de base
    vector_store_type: str = "chroma"
    vector_store_path: str = "./vector_store"
    
    # Configuration Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_temperature: float = 0.7
    
    # Configuration des documents
    documents_path: str = "./documents"
    supported_formats: List[str] = None
    
    # Configuration avancée
    enable_specialized_engines: bool = True
    enable_memory: bool = True
    max_chunks_per_query: int = 8
    confidence_threshold: float = 0.3
    
    # Configuration de logging
    log_level: str = "INFO"
    log_file: str = "./logs/rag_system.log"
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = [".pdf", ".txt", ".md"]
        
        # Créer les répertoires nécessaires
        Path(self.vector_store_path).mkdir(parents=True, exist_ok=True)
        Path(self.documents_path).mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

# ==================== Orchestrateur Principal ====================

class RAGSystemOrchestrator:
    """Orchestrateur principal du système RAG multimodal"""
    
    def __init__(self, config: RAGSystemConfig):
        self.config = config
        self.setup_logging()
        
        # États du système
        self.is_initialized = False
        self.documents_indexed = 0
        self.last_query_time = None
        
        # Composants principaux
        self.rag_pipeline = None
        self.base_agent = None
        self.enhanced_agent = None
        
        # Statistiques
        self.stats = {
            "queries_processed": 0,
            "documents_ingested": 0,
            "average_response_time": 0.0,
            "success_rate": 0.0,
            "last_activity": None
        }
    
    def setup_logging(self):
        """Configure le système de logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        
        logger.info("Logging configuré")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialise le système RAG complet"""
        logger.info("🚀 Initialisation du système RAG multimodal...")
        
        try:
            # Étape 1: Configuration de la pipeline RAG
            logger.info("📊 Configuration de la pipeline RAG...")
            rag_config = self._create_rag_config()
            self.rag_pipeline = create_pipeline(rag_config)
            
            # Étape 2: Vérification de Gemini
            logger.info("🤖 Configuration de Gemini...")
            if not self.config.gemini_api_key:
                raise ValueError("Clé API Gemini manquante")
            
            # Étape 3: Création de l'agent de base
            logger.info("🧠 Création de l'agent RAG de base...")
            self.base_agent = create_rag_agent(
                self.rag_pipeline, 
                self.config.gemini_api_key,
                self.config.gemini_model
            )
            
            # Étape 4: Création de l'agent amélioré avec moteurs spécialisés
            if self.config.enable_specialized_engines:
                logger.info("⚙️ Activation des moteurs spécialisés...")
                self.enhanced_agent = create_enhanced_rag_agent(
                    self.base_agent,
                    self.config.gemini_api_key
                )
            
            # Étape 5: Test de santé du système
            logger.info("🏥 Vérification de santé du système...")
            health_check = await self._perform_health_check()
            
            if not health_check["healthy"]:
                raise Exception(f"Échec du test de santé: {health_check['errors']}")
            
            self.is_initialized = True
            logger.info("✅ Système RAG initialisé avec succès!")
            
            return {
                "success": True,
                "components_loaded": [
                    "rag_pipeline",
                    "base_agent",
                    "enhanced_agent" if self.config.enable_specialized_engines else None
                ],
                "health_check": health_check,
                "config_summary": self._get_config_summary()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            return {
                "success": False,
                "error": str(e),
                "components_loaded": []
            }
    
    def _create_rag_config(self) -> RAGPipelineConfig:
        """Crée la configuration RAG à partir de la configuration système"""
        config = RAGPipelineConfig()
        
        # Configuration du vector store
        config.vector_store.store_type = self.config.vector_store_type
        config.vector_store.store_path = self.config.vector_store_path
        
        # Configuration du parsing
        config.parsing.supported_formats = self.config.supported_formats
        
        # Configuration du chunking
        config.chunking.text_chunk_size = 1000
        config.chunking.text_chunk_overlap = 200
        
        # Configuration des embeddings
        config.embedding.batch_size = 32
        
        return config
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Effectue un test de santé complet du système"""
        health_status = {
            "healthy": True,
            "components": {},
            "errors": []
        }
        
        try:
            # Test de la pipeline RAG
            pipeline_health = self.rag_pipeline.health_check()
            health_status["components"]["rag_pipeline"] = pipeline_health["status"]
            if pipeline_health["status"] != "healthy":
                health_status["errors"].extend(pipeline_health.get("errors", []))
            
            # Test de l'agent de base
            try:
                test_result = await self.base_agent.process_query("test", "health_check")
                health_status["components"]["base_agent"] = "healthy"
            except Exception as e:
                health_status["components"]["base_agent"] = "error"
                health_status["errors"].append(f"Base agent: {str(e)}")
            
            # Test de l'agent amélioré
            if self.enhanced_agent:
                try:
                    test_result = await self.enhanced_agent.process_query_enhanced("test")
                    health_status["components"]["enhanced_agent"] = "healthy"
                except Exception as e:
                    health_status["components"]["enhanced_agent"] = "error"
                    health_status["errors"].append(f"Enhanced agent: {str(e)}")
            
            # Statut global
            health_status["healthy"] = len(health_status["errors"]) == 0
            
        except Exception as e:
            health_status["healthy"] = False
            health_status["errors"].append(f"Health check failed: {str(e)}")
        
        return health_status
    
    def _get_config_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la configuration"""
        return {
            "vector_store": self.config.vector_store_type,
            "gemini_model": self.config.gemini_model,
            "specialized_engines": self.config.enable_specialized_engines,
            "supported_formats": self.config.supported_formats,
            "documents_path": self.config.documents_path
        }
    
    async def ingest_documents(self, file_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Ingère des documents dans le système"""
        if not self.is_initialized:
            return {"success": False, "error": "Système non initialisé"}
        
        logger.info("📥 Début de l'ingestion de documents...")
        
        # Déterminer les fichiers à traiter
        if file_paths is None:
            file_paths = self._discover_documents()
        
        if not file_paths:
            return {"success": False, "error": "Aucun document trouvé"}
        
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            try:
                logger.info(f"📄 Traitement: {file_path}")
                result = self.rag_pipeline.ingest_document(file_path)
                
                if result.success:
                    successful += 1
                    self.stats["documents_ingested"] += 1
                else:
                    failed += 1
                
                results.append({
                    "file": file_path,
                    "success": result.success,
                    "chunks_created": result.chunks_created,
                    "processing_time": result.processing_time,
                    "error": result.error_message if not result.success else None
                })
                
            except Exception as e:
                failed += 1
                logger.error(f"❌ Erreur traitement {file_path}: {e}")
                results.append({
                    "file": file_path,
                    "success": False,
                    "error": str(e)
                })
        
        self.documents_indexed = successful
        
        summary = {
            "success": True,
            "total_files": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results,
            "processing_summary": {
                "total_chunks": sum(r.get("chunks_created", 0) for r in results),
                "total_time": sum(r.get("processing_time", 0) for r in results),
                "success_rate": successful / len(file_paths) if file_paths else 0
            }
        }
        
        logger.info(f"✅ Ingestion terminée: {successful}/{len(file_paths)} fichiers traités")
        return summary
    
    def _discover_documents(self) -> List[str]:
        """Découvre automatiquement les documents à ingérer"""
        documents_dir = Path(self.config.documents_path)
        
        if not documents_dir.exists():
            logger.warning(f"Répertoire de documents non trouvé: {documents_dir}")
            return []
        
        found_files = []
        
        for ext in self.config.supported_formats:
            # Recherche récursive
            pattern = f"**/*{ext}"
            files = list(documents_dir.glob(pattern))
            found_files.extend([str(f) for f in files])
        
        logger.info(f"📚 Documents découverts: {len(found_files)} fichiers")
        return found_files
    
    async def query(self, question: str, session_id: str = "default", 
                   use_specialized_engines: bool = None) -> Dict[str, Any]:
        """Traite une requête utilisateur"""
        if not self.is_initialized:
            return {"success": False, "error": "Système non initialisé"}
        
        start_time = time.time()
        self.last_query_time = start_time
        
        try:
            logger.info(f"🔍 Traitement de la requête: '{question[:50]}...'")
            
            # Choisir l'agent à utiliser
            if use_specialized_engines is None:
                use_specialized_engines = self.config.enable_specialized_engines
            
            if use_specialized_engines and self.enhanced_agent:
                result = await self.enhanced_agent.process_query_enhanced(question, session_id)
                agent_used = "enhanced"
            else:
                result = await self.base_agent.process_query(question, session_id)
                agent_used = "base"
            
            processing_time = time.time() - start_time
            
            # Mettre à jour les statistiques
            self.stats["queries_processed"] += 1
            self.stats["average_response_time"] = (
                (self.stats["average_response_time"] * (self.stats["queries_processed"] - 1) + processing_time) /
                self.stats["queries_processed"]
            )
            self.stats["last_activity"] = time.time()
            
            # Enrichir le résultat
            enriched_result = {
                "success": True,
                "question": question,
                "answer": result["response"],
                "confidence": result["confidence"],
                "sources": result["sources"],
                "processing_time": processing_time,
                "agent_used": agent_used,
                "session_id": session_id,
                "metadata": {
                    "search_intent": result.get("search_intent", ""),
                    "expanded_queries": result.get("expanded_queries", []),
                    "engines_used": result.get("engines_used", []),
                    "specialized_processing": result.get("specialized_processing", False)
                }
            }
            
            logger.info(f"✅ Requête traitée en {processing_time:.2f}s (confiance: {result['confidence']:.3f})")
            return enriched_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Erreur traitement requête: {e}")
            
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "processing_time": processing_time,
                "agent_used": "none"
            }
    
    async def batch_query(self, questions: List[str], session_id: str = "default") -> List[Dict[str, Any]]:
        """Traite plusieurs requêtes en lot"""
        logger.info(f"🔄 Traitement de {len(questions)} requêtes en lot")
        
        results = []
        for i, question in enumerate(questions, 1):
            logger.info(f"📝 Requête {i}/{len(questions)}")
            result = await self.query(question, f"{session_id}_batch_{i}")
            results.append(result)
            
            # Pause courte entre les requêtes
            await asyncio.sleep(0.5)
        
        # Statistiques du lot
        successful = sum(1 for r in results if r["success"])
        avg_confidence = sum(r.get("confidence", 0) for r in results if r["success"]) / max(successful, 1)
        
        logger.info(f"✅ Lot traité: {successful}/{len(questions)} succès, confiance moyenne: {avg_confidence:.3f}")
        
        return results
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        pipeline_stats = self.rag_pipeline.get_statistics() if self.rag_pipeline else {}
        
        return {
            "system_status": {
                "initialized": self.is_initialized,
                "documents_indexed": self.documents_indexed,
                "last_query_time": self.last_query_time
            },
            "usage_stats": self.stats,
            "pipeline_stats": pipeline_stats,
            "config": self._get_config_summary()
        }
    
    async def clear_vector_store(self) -> Dict[str, Any]:
        """Vide la base vectorielle"""
        if not self.is_initialized:
            return {"success": False, "error": "Système non initialisé"}
        
        logger.info("🗑️ Vidage de la base vectorielle...")
        
        try:
            success = self.rag_pipeline.clear_vector_store()
            
            if success:
                self.documents_indexed = 0
                self.stats["documents_ingested"] = 0
                logger.info("✅ Base vectorielle vidée")
            
            return {"success": success}
            
        except Exception as e:
            logger.error(f"❌ Erreur vidage: {e}")
            return {"success": False, "error": str(e)}
    
    async def shutdown(self):
        """Arrêt propre du système"""
        logger.info("🛑 Arrêt du système RAG...")
        
        # Sauvegarder les statistiques
        stats_file = Path(self.config.log_file).parent / "system_stats.json"
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.get_system_stats(), f, indent=2, default=str)
            logger.info(f"📊 Statistiques sauvegardées: {stats_file}")
        except Exception as e:
            logger.warning(f"⚠️ Erreur sauvegarde stats: {e}")
        
        logger.info("✅ Arrêt terminé")

# ==================== Interface Simplifiée ====================

class SimpleRAGInterface:
    """Interface simplifiée pour une utilisation rapide"""
    
    def __init__(self, gemini_api_key: str, documents_path: str = "./documents"):
        self.config = RAGSystemConfig(
            gemini_api_key=gemini_api_key,
            documents_path=documents_path
        )
        self.orchestrator = RAGSystemOrchestrator(self.config)
        self.ready = False
    
    async def setup(self) -> bool:
        """Configuration rapide du système"""
        print("🚀 Configuration du système RAG...")
        
        # Initialisation
        init_result = await self.orchestrator.initialize()
        if not init_result["success"]:
            print(f"❌ Erreur initialisation: {init_result['error']}")
            return False
        
        # Ingestion automatique des documents
        print("📥 Ingestion des documents...")
        ingest_result = await self.orchestrator.ingest_documents()
        
        if ingest_result["successful"] > 0:
            print(f"✅ {ingest_result['successful']} documents indexés")
            self.ready = True
            return True
        else:
            print("⚠️ Aucun document indexé, mais le système est prêt pour les requêtes")
            self.ready = True
            return True
    
    async def ask(self, question: str) -> str:
        """Pose une question simple"""
        if not self.ready:
            return "❌ Système non configuré. Exécutez setup() d'abord."
        
        result = await self.orchestrator.query(question)
        
        if result["success"]:
            return result["answer"]
        else:
            return f"❌ Erreur: {result['error']}"
    
    async def ask_detailed(self, question: str) -> Dict[str, Any]:
        """Pose une question avec détails complets"""
        if not self.ready:
            return {"error": "Système non configuré"}
        
        return await self.orchestrator.query(question)
    
    def add_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """Ajoute des documents au système"""
        if not self.ready:
            return {"error": "Système non configuré"}
        
        return asyncio.run(self.orchestrator.ingest_documents(file_paths))
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtient les statistiques du système"""
        return self.orchestrator.get_system_stats()

# ==================== Exemples d'Utilisation ====================

async def demo_complete_system():
    """Démonstration complète du système"""
    
    # Configuration
    GEMINI_API_KEY = "your-gemini-api-key-here"  # À remplacer
    
    if GEMINI_API_KEY == "your-gemini-api-key-here":
        print("⚠️ Veuillez configurer votre clé API Gemini")
        return
    
    print("🎯 Démonstration du système RAG complet")
    print("=" * 50)
    
    # Interface simplifiée
    rag = SimpleRAGInterface(GEMINI_API_KEY, "./demo_documents")
    
    # Configuration
    success = await rag.setup()
    if not success:
        print("❌ Échec de la configuration")
        return
    
    # Questions de test
    questions = [
        "Qu'est-ce que l'intelligence artificielle?",
        "Calculez la moyenne de 10, 20, 30, 40, 50",
        "Comment optimiser les performances d'une application web?",
        "Analysez les tendances dans les données de vente",
        "Expliquez le fonctionnement du machine learning"
    ]
    
    print("\n🤖 Test des requêtes:")
    print("-" * 30)
    
    for question in questions:
        print(f"\n❓ {question}")
        
        # Requête détaillée
        result = await rag.ask_detailed(question)
        
        if result["success"]:
            print(f"🎯 Confiance: {result['confidence']:.3f}")
            print(f"⚙️ Agent: {result['agent_used']}")
            print(f"🔧 Moteurs: {result['metadata'].get('engines_used', ['standard'])}")
            print(f"💬 Réponse: {result['answer'][:200]}...")
        else:
            print(f"❌ Erreur: {result['error']}")
        
        await asyncio.sleep(1)
    
    # Statistiques finales
    print("\n📊 Statistiques du système:")
    print("-" * 30)
    stats = rag.get_stats()
    usage = stats["usage_stats"]
    print(f"📝 Requêtes traitées: {usage['queries_processed']}")
    print(f"📚 Documents indexés: {usage['documents_ingested']}")
    print(f"⏱️ Temps moyen: {usage['average_response_time']:.2f}s")

async def demo_advanced_orchestrator():
    """Démonstration avancée avec l'orchestrateur complet"""
    
    GEMINI_API_KEY = "your-gemini-api-key-here"  # À remplacer
    
    if GEMINI_API_KEY == "your-gemini-api-key-here":
        print("⚠️ Veuillez configurer votre clé API Gemini")
        return
    
    # Configuration avancée
    config = RAGSystemConfig(
        gemini_api_key=GEMINI_API_KEY,
        vector_store_type="chroma",
        enable_specialized_engines=True,
        confidence_threshold=0.5,
        documents_path="./advanced_documents"
    )
    
    orchestrator = RAGSystemOrchestrator(config)
    
    # Initialisation
    print("🚀 Initialisation avancée...")
    init_result = await orchestrator.initialize()
    
    if not init_result["success"]:
        print(f"❌ Échec: {init_result['error']}")
        return
    
    print("✅ Système initialisé")
    print(f"🔧 Composants: {init_result['components_loaded']}")
    
    # Test de requêtes complexes
    complex_queries = [
        "Analysez les performances financières et calculez le ROI",
        "Optimisez l'architecture système pour gérer 1M d'utilisateurs",
        "Quelle est la probabilité de succès basée sur les données historiques?"
    ]
    
    print("\n🧠 Test de requêtes complexes:")
    print("-" * 40)
    
    for query in complex_queries:
        print(f"\n🔍 {query}")
        result = await orchestrator.query(query, use_specialized_engines=True)
        
        if result["success"]:
            metadata = result["metadata"]
            print(f"🎯 Confiance: {result['confidence']:.3f}")
            print(f"⚙️ Agent: {result['agent_used']}")
            print(f"🧩 Moteurs spécialisés: {metadata.get('engines_used', [])}")
            print(f"🔄 Traitement spécialisé: {metadata.get('specialized_processing', False)}")
            print(f"📝 Réponse: {result['answer'][:150]}...")
        else:
            print(f"❌ Erreur: {result['error']}")
    
    # Statistiques finales
    print(f"\n📊 Statistiques: {orchestrator.get_system_stats()['usage_stats']}")

if __name__ == "__main__":
    print("🎯 Choisissez une démonstration:")
    print("1. Interface simple")
    print("2. Orchestrateur avancé")
    
    choice = input("Votre choix (1 ou 2): ").strip()
    
    if choice == "1":
        asyncio.run(demo_complete_system())
    elif choice == "2":
        asyncio.run(demo_advanced_orchestrator())
    else:
        print("❌ Choix invalide")