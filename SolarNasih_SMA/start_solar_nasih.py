"""
Script de démarrage complet du système Solar Nasih SMA
Vérifie tous les composants avant le lancement
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Vérifie l'environnement et les dépendances"""
    
    logger.info("Verification de l'environnement...")
    
    # Vérification Python
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ requis")
        return False
    
    # Vérification variables d'environnement
    required_env = ['GEMINI_API_KEY', 'TAVILY_API_KEY']
    missing_env = []
    
    for env_var in required_env:
        if not os.getenv(env_var) or os.getenv(env_var) == f"your_{env_var.lower()}_here":
            missing_env.append(env_var)
    
    if missing_env:
        logger.error(f"Variables d'environnement manquantes: {missing_env}")
        logger.info("Creez un fichier .env avec vos cles API")
        return False
    
    # Vérification modules Python
    try:
        import fastapi
        import langchain
        import langgraph
        import tavily
        logger.info("Modules principaux disponibles")
    except ImportError as e:
        logger.error(f"Module manquant: {e}")
        logger.info("Executez: pip install -r requirements.txt")
        return False
    
    return True

async def test_agents():
    """Test rapide des agents"""
    
    logger.info("🤖 Test des agents...")
    
    try:
        from graph.workflow import SolarNasihWorkflow
        
        workflow = SolarNasihWorkflow()
        
        # Test simple
        result = await workflow.run(
            "Qu'est-ce que l'énergie solaire ?",
            {"test": True}
        )
        
        if result and result.get('response'):
            logger.info("✅ Agents fonctionnels")
            return True
        else:
            logger.error("❌ Problème dans le workflow")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test agents: {e}")
        return False

def main():
    """Fonction principale de démarrage"""
    
    print("🌞 SOLAR NASIH - SYSTÈME MULTI-AGENT 🌞")
    print("=" * 50)
    
    # Vérifications préalables
    if not check_environment():
        logger.error("❌ Échec des vérifications")
        sys.exit(1)
    
    # Test des agents
    if not asyncio.run(test_agents()):
        logger.error("❌ Échec du test des agents")
        sys.exit(1)
    
    logger.info("✅ Tous les tests sont passés!")
    logger.info("🚀 Démarrage du serveur...")
    
    # Démarrage du serveur
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du serveur")
    except Exception as e:
        logger.error(f"❌ Erreur serveur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
