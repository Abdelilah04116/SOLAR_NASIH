#!/usr/bin/env python3
"""
Script de configuration et démarrage rapide pour le système RAG multimodal
Usage: python setup_and_run.py [commande] [options]
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
import json
import subprocess
from typing import Dict, Any, List

# ==================== Configuration et Validation ====================

def check_dependencies() -> Dict[str, bool]:
    """Vérifie que toutes les dépendances sont installées"""
    dependencies = {
        "torch": False,
        "transformers": False,
        "sentence_transformers": False,
        "chromadb": False,
        "fitz": False,  # PyMuPDF
        "google.generativeai": False,
        "langgraph": False,
        "PIL": False,  # Pillow
        "numpy": False,
        "pandas": False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies

def install_missing_dependencies(missing: List[str]) -> bool:
    """Installe les dépendances manquantes"""
    if not missing:
        return True
    
    print(f"📦 Installation de {len(missing)} dépendances manquantes...")
    
    # Mapping des noms de modules vers les packages pip
    pip_packages = {
        "torch": "torch",
        "transformers": "transformers",
        "sentence_transformers": "sentence-transformers",
        "chromadb": "chromadb",
        "fitz": "PyMuPDF",
        "google.generativeai": "google-generativeai",
        "langgraph": "langgraph",
        "PIL": "Pillow",
        "numpy": "numpy",
        "pandas": "pandas"
    }
    
    packages_to_install = [pip_packages.get(dep, dep) for dep in missing]
    
    try:
        cmd = [sys.executable, "-m", "pip", "install"] + packages_to_install
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dépendances installées avec succès")
            return True
        else:
            print(f"❌ Erreur installation: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def validate_environment() -> Dict[str, Any]:
    """Valide l'environnement complet"""
    validation = {
        "dependencies": True,
        "gemini_key": False,
        "directories": True,
        "permissions": True,
        "errors": []
    }
    
    # Vérifier les dépendances
    deps = check_dependencies()
    missing_deps = [dep for dep, installed in deps.items() if not installed]
    
    if missing_deps:
        validation["dependencies"] = False
        validation["errors"].append(f"Dépendances manquantes: {', '.join(missing_deps)}")
    
    # Vérifier la clé Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and len(gemini_key) > 10:
        validation["gemini_key"] = True
    else:
        validation["errors"].append("Variable GEMINI_API_KEY non configurée")
    
    # Vérifier les répertoires
    required_dirs = ["./documents", "./vector_store", "./logs"]
    for dir_path in required_dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            validation["directories"] = False
            validation["errors"].append(f"Impossible de créer {dir_path}: {e}")
    
    return validation

def create_sample_config() -> str:
    """Crée un fichier de configuration d'exemple"""
    config = {
        "gemini_api_key": "${GEMINI_API_KEY}",
        "vector_store_type": "chroma",
        "vector_store_path": "./vector_store",
        "documents_path": "./documents",
        "enable_specialized_engines": True,
        "enable_memory": True,
        "supported_formats": [".pdf", ".txt", ".md"],
        "log_level": "INFO",
        "gemini_model": "gemini-2.0-flash-exp",
        "gemini_temperature": 0.7,
        "max_chunks_per_query": 8,
        "confidence_threshold": 0.3
    }
    
    config_file = "rag_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config_file

# ==================== Commandes Principales ====================

async def cmd_setup(args):
    """Configure l'environnement complet"""
    print("🚀 Configuration du système RAG multimodal")
    print("=" * 50)
    
    # Étape 1: Validation de l'environnement
    print("🔍 Validation de l'environnement...")
    validation = validate_environment()
    
    if not validation["dependencies"]:
        print("❌ Dépendances manquantes détectées")
        
        if args.auto_install:
            deps = check_dependencies()
            missing = [dep for dep, installed in deps.items() if not installed]
            
            if install_missing_dependencies(missing):
                print("✅ Dépendances installées")
            else:
                print("❌ Échec de l'installation automatique")
                return False
        else:
            print("💡 Utilisez --auto-install pour installer automatiquement")
            print(f"   Ou installez manuellement: pip install {' '.join(missing)}")
            return False
    
    # Étape 2: Configuration Gemini
    if not validation["gemini_key"]:
        print("🔑 Configuration de l'API Gemini requise")
        
        if args.interactive:
            gemini_key = input("Entrez votre clé API Gemini: ").strip()
            if gemini_key:
                os.environ["GEMINI_API_KEY"] = gemini_key
                print("✅ Clé API configurée pour cette session")
        else:
            print("💡 Configurez la variable d'environnement GEMINI_API_KEY")
            print("   export GEMINI_API_KEY='votre-cle-api'")
            return False
    
    # Étape 3: Création de la configuration
    print("📄 Création du fichier de configuration...")
    config_file = create_sample_config()
    print(f"✅ Configuration créée: {config_file}")
    
    # Étape 4: Test du système
    if args.test_system:
        print("🧪 Test du système...")
        
        try:
            # Import et test rapide
            from rag_orchestrator import SimpleRAGInterface
            
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                print("⚠️ Test ignoré: clé API manquante")
                return True
            
            rag = SimpleRAGInterface(gemini_key)
            success = await rag.setup()
            
            if success:
                print("✅ Système testé avec succès")
                
                # Test d'une requête simple
                answer = await rag.ask("Bonjour, le système fonctionne-t-il?")
                print(f"🤖 Test de requête: {answer[:100]}...")
                
            else:
                print("⚠️ Test du système échoué")
                
        except Exception as e:
            print(f"⚠️ Erreur lors du test: {e}")
    
    print("\n🎉 Configuration terminée!")
    print("📋 Prochaines étapes:")
    print("   1. Placez vos documents dans ./documents/")
    print("   2. Exécutez: python setup_and_run.py ingest")
    print("   3. Testez: python setup_and_run.py query 'votre question'")
    
    return True

async def cmd_ingest(args):
    """Ingère des documents dans le système"""
    print("📥 Ingestion de documents")
    print("=" * 30)
    
    try:
        from rag_orchestrator import SimpleRAGInterface
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ Variable GEMINI_API_KEY non configurée")
            return False
        
        # Initialiser le système
        rag = SimpleRAGInterface(gemini_key, args.documents_path)
        
        if not await rag.setup():
            print("❌ Échec de l'initialisation")
            return False
        
        # Ingestion
        if args.files:
            # Fichiers spécifiques
            result = rag.add_documents(args.files)
        else:
            # Découverte automatique
            result = await rag.orchestrator.ingest_documents()
        
        # Affichage des résultats
        if result.get("successful", 0) > 0:
            print(f"✅ {result['successful']} documents ingérés avec succès")
            print(f"📊 {result['processing_summary']['total_chunks']} chunks créés")
            print(f"⏱️ Temps total: {result['processing_summary']['total_time']:.2f}s")
        else:
            print("❌ Aucun document ingéré")
            if result.get("failed", 0) > 0:
                print(f"🔥 {result['failed']} échecs")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ingestion: {e}")
        return False

async def cmd_query(args):
    """Traite une requête utilisateur"""
    if not args.question:
        print("❌ Question manquante. Utilisez: --question 'votre question'")
        return False
    
    print(f"🔍 Traitement de la requête: '{args.question}'")
    print("=" * 50)
    
    try:
        from rag_orchestrator import SimpleRAGInterface
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ Variable GEMINI_API_KEY non configurée")
            return False
        
        # Initialiser le système
        rag = SimpleRAGInterface(gemini_key, args.documents_path)
        
        if not await rag.setup():
            print("❌ Échec de l'initialisation")
            return False
        
        # Traiter la requête
        if args.detailed:
            result = await rag.ask_detailed(args.question)
            
            if result.get("success", False):
                print(f"🎯 Confiance: {result['confidence']:.3f}")
                print(f"⚙️ Agent utilisé: {result['agent_used']}")
                print(f"⏱️ Temps de traitement: {result['processing_time']:.2f}s")
                print(f"📚 Sources utilisées: {len(result.get('sources', []))}")
                
                metadata = result.get('metadata', {})
                if metadata.get('engines_used'):
                    print(f"🔧 Moteurs spécialisés: {metadata['engines_used']}")
                
                print(f"\n💬 Réponse:")
                print(f"{result['answer']}")
                
                if args.show_sources and result.get('sources'):
                    print(f"\n📖 Sources:")
                    for i, source in enumerate(result['sources'][:3], 1):
                        print(f"   {i}. Page {source.get('page_number', 'N/A')}: {source.get('content', '')[:100]}...")
                
            else:
                print(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
        else:
            # Requête simple
            answer = await rag.ask(args.question)
            print(f"💬 Réponse: {answer}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la requête: {e}")
        return False

async def cmd_interactive(args):
    """Mode interactif pour poser des questions"""
    print("🤖 Mode interactif du système RAG")
    print("=" * 35)
    print("💡 Tapez 'quit' pour quitter, 'stats' pour les statistiques")
    print()
    
    try:
        from rag_orchestrator import SimpleRAGInterface
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ Variable GEMINI_API_KEY non configurée")
            return False
        
        # Initialiser le système
        print("🚀 Initialisation du système...")
        rag = SimpleRAGInterface(gemini_key, args.documents_path)
        
        if not await rag.setup():
            print("❌ Échec de l'initialisation")
            return False
        
        print("✅ Système prêt!")
        print()
        
        session_count = 0
        
        while True:
            try:
                question = input("❓ Votre question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Au revoir!")
                    break
                
                elif question.lower() == 'stats':
                    stats = rag.get_stats()
                    usage = stats["usage_stats"]
                    print(f"📊 Statistiques:")
                    print(f"   📝 Requêtes: {usage['queries_processed']}")
                    print(f"   📚 Documents: {usage['documents_ingested']}")
                    print(f"   ⏱️ Temps moyen: {usage['average_response_time']:.2f}s")
                    continue
                
                elif not question:
                    continue
                
                session_count += 1
                print(f"🔍 Traitement... (#{session_count})")
                
                # Traiter la requête
                result = await rag.ask_detailed(question)
                
                if result.get("success", False):
                    print(f"🎯 Confiance: {result['confidence']:.3f}")
                    print(f"💬 {result['answer']}")
                else:
                    print(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Interruption utilisateur, au revoir!")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
                continue
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du mode interactif: {e}")
        return False

async def cmd_status(args):
    """Affiche le statut du système"""
    print("📊 Statut du système RAG")
    print("=" * 25)
    
    try:
        # Vérification de l'environnement
        validation = validate_environment()
        
        print("🔍 Environnement:")
        print(f"   Dependencies: {'✅' if validation['dependencies'] else '❌'}")
        print(f"   Clé Gemini: {'✅' if validation['gemini_key'] else '❌'}")
        print(f"   Répertoires: {'✅' if validation['directories'] else '❌'}")
        
        if validation["errors"]:
            print("❌ Erreurs:")
            for error in validation["errors"]:
                print(f"   - {error}")
        
        # Vérification des documents
        docs_path = Path(args.documents_path)
        if docs_path.exists():
            doc_files = list(docs_path.glob("**/*.pdf")) + list(docs_path.glob("**/*.txt"))
            print(f"📚 Documents disponibles: {len(doc_files)}")
        else:
            print("📚 Répertoire de documents: non trouvé")
        
        # Vérification du vector store
        vector_path = Path("./vector_store")
        if vector_path.exists():
            vector_files = list(vector_path.rglob("*"))
            print(f"🗄️ Vector store: {len(vector_files)} fichiers")
        else:
            print("🗄️ Vector store: non initialisé")
        
        # Test de connectivité Gemini
        print("\n🤖 Test Gemini...")
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = model.generate_content("Test de connectivité")
                print("✅ Gemini: Connecté")
            except Exception as e:
                print(f"❌ Gemini: Erreur - {e}")
        else:
            print("❌ Gemini: Clé API manquante")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

async def cmd_clear(args):
    """Vide le vector store"""
    print("🗑️ Vidage du vector store")
    
    if not args.force:
        confirm = input("Êtes-vous sûr de vouloir vider le vector store? (oui/non): ").strip().lower()
        if confirm not in ['oui', 'o', 'yes', 'y']:
            print("❌ Opération annulée")
            return True
    
    try:
        from rag_orchestrator import SimpleRAGInterface
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ Variable GEMINI_API_KEY non configurée")
            return False
        
        rag = SimpleRAGInterface(gemini_key)
        
        if await rag.setup():
            result = await rag.orchestrator.clear_vector_store()
            
            if result["success"]:
                print("✅ Vector store vidé avec succès")
            else:
                print(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
        else:
            print("❌ Impossible d'initialiser le système")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def cmd_demo(args):
    """Lance une démonstration du système"""
    print("🎯 Démonstration du système RAG multimodal")
    print("=" * 45)
    
    # Créer des documents d'exemple
    demo_dir = Path("./demo_documents")
    demo_dir.mkdir(exist_ok=True)
    
    # Document d'exemple sur l'IA
    ai_doc = demo_dir / "intelligence_artificielle.txt"
    if not ai_doc.exists():
        with open(ai_doc, 'w', encoding='utf-8') as f:
            f.write("""
Intelligence Artificielle - Guide Complet

L'intelligence artificielle (IA) est une technologie qui permet aux machines 
de simuler l'intelligence humaine. Elle comprend plusieurs domaines :

1. Machine Learning (Apprentissage Automatique)
   - Algorithmes qui apprennent à partir de données
   - Réseaux de neurones artificiels
   - Deep Learning pour les tâches complexes

2. Traitement du Langage Naturel (NLP)
   - Compréhension du texte
   - Génération de contenu
   - Traduction automatique

3. Vision par Ordinateur
   - Reconnaissance d'images
   - Détection d'objets
   - Analyse vidéo

Applications pratiques :
- Assistants virtuels (Siri, Alexa)
- Voitures autonomes
- Diagnostic médical
- Recommandations personnalisées
- Analyse prédictive

L'IA transforme de nombreux secteurs et continue d'évoluer rapidement.
            """)
    
    # Document d'exemple avec des données
    data_doc = demo_dir / "donnees_exemple.txt"
    if not data_doc.exists():
        with open(data_doc, 'w', encoding='utf-8') as f:
            f.write("""
Données de Ventes - Trimestre 1

Tableau des ventes par mois:
| Mois    | Ventes | Objectif | Écart |
|---------|--------|----------|-------|
| Janvier | 15000  | 12000    | +25%  |
| Février | 18000  | 15000    | +20%  |
| Mars    | 22000  | 18000    | +22%  |

Analyse:
- Croissance constante de 15% par mois
- Dépassement des objectifs sur tout le trimestre
- Performance exceptionnelle en mars

Métriques clés:
- Chiffre d'affaires total: 55,000€
- Croissance vs année précédente: +30%
- Nombre de clients: 450
- Panier moyen: 122€

Recommandations:
1. Maintenir la dynamique commerciale
2. Augmenter les objectifs du T2
3. Investir dans le marketing digital
            """)
    
    print(f"📁 Documents d'exemple créés dans {demo_dir}")
    print("🚀 Vous pouvez maintenant tester:")
    print("   python setup_and_run.py ingest --documents-path ./demo_documents")
    print("   python setup_and_run.py query --question 'Qu'est-ce que l'IA?'")
    print("   python setup_and_run.py interactive --documents-path ./demo_documents")
    
    return True

# ==================== Interface Ligne de Commande ====================

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Système RAG Multimodal avec LangGraph et Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Configuration initiale
  python setup_and_run.py setup --auto-install --interactive
  
  # Ingestion de documents
  python setup_and_run.py ingest --documents-path ./mes_documents
  
  # Requête simple
  python setup_and_run.py query --question "Qu'est-ce que l'intelligence artificielle?"
  
  # Mode interactif
  python setup_and_run.py interactive
  
  # Statut du système
  python setup_and_run.py status
  
  # Démonstration
  python setup_and_run.py demo
        """
    )
    
    # Commandes principales
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Setup
    setup_parser = subparsers.add_parser('setup', help='Configure le système')
    setup_parser.add_argument('--auto-install', action='store_true', 
                             help='Installe automatiquement les dépendances manquantes')
    setup_parser.add_argument('--interactive', action='store_true',
                             help='Mode interactif pour la configuration')
    setup_parser.add_argument('--test-system', action='store_true',
                             help='Test le système après configuration')
    
    # Ingest
    ingest_parser = subparsers.add_parser('ingest', help='Ingère des documents')
    ingest_parser.add_argument('--documents-path', default='./documents',
                              help='Chemin vers les documents')
    ingest_parser.add_argument('--files', nargs='+',
                              help='Fichiers spécifiques à ingérer')
    
    # Query
    query_parser = subparsers.add_parser('query', help='Pose une question')
    query_parser.add_argument('--question', '-q', required=True,
                             help='Question à poser')
    query_parser.add_argument('--documents-path', default='./documents',
                             help='Chemin vers les documents')
    query_parser.add_argument('--detailed', action='store_true',
                             help='Réponse détaillée avec métadonnées')
    query_parser.add_argument('--show-sources', action='store_true',
                             help='Affiche les sources utilisées')
    
    # Interactive
    interactive_parser = subparsers.add_parser('interactive', help='Mode interactif')
    interactive_parser.add_argument('--documents-path', default='./documents',
                                   help='Chemin vers les documents')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Statut du système')
    status_parser.add_argument('--documents-path', default='./documents',
                              help='Chemin vers les documents')
    
    # Clear
    clear_parser = subparsers.add_parser('clear', help='Vide le vector store')
    clear_parser.add_argument('--force', action='store_true',
                             help='Force le vidage sans confirmation')
    
    # Demo
    demo_parser = subparsers.add_parser('demo', help='Crée une démonstration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Dispatcher des commandes
    commands = {
        'setup': cmd_setup,
        'ingest': cmd_ingest,
        'query': cmd_query,
        'interactive': cmd_interactive,
        'status': cmd_status,
        'clear': cmd_clear,
        'demo': cmd_demo
    }
    
    command_func = commands.get(args.command)
    if not command_func:
        print(f"❌ Commande inconnue: {args.command}")
        return
    
    try:
        if asyncio.iscoroutinefunction(command_func):
            result = asyncio.run(command_func(args))
        else:
            result = command_func(args)
        
        if not result:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Interruption utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()