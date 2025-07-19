"""
Script principal d'exemple pour utiliser la pipeline RAG multimodal
"""
import argparse
import sys
import subprocess
import os
from pathlib import Path
import json

from config import RAGPipelineConfig, load_config_from_file, save_config_to_file
from pipeline import create_pipeline
from models import SearchQuery

def main():
    parser = argparse.ArgumentParser(description="Pipeline RAG Multimodal")
    parser.add_argument("command", choices=["ingest", "search", "stats", "clear", "health", "visualize", "web"],
                       help="Commande à exécuter")
    
    # Arguments pour l'ingestion
    parser.add_argument("--file", "-f", type=str, help="Fichier à ingérer")
    parser.add_argument("--directory", "-d", type=str, help="Répertoire de fichiers à ingérer")
    
    # Arguments pour la recherche
    parser.add_argument("--query", "-q", type=str, help="Requête de recherche")
    parser.add_argument("--k", type=int, default=5, help="Nombre de résultats")
    parser.add_argument("--filters", type=str, help="Filtres JSON")
    
    # Arguments pour la visualisation
    parser.add_argument("--type", type=str, 
                       choices=["overview", "structure", "content", "positions", "embeddings", "report", "all"],
                       default="overview", help="Type de visualisation")
    parser.add_argument("--output-dir", type=str, default="./visualizations",
                       help="Répertoire de sortie pour les visualisations")
    
    # Configuration
    parser.add_argument("--config", "-c", type=str, help="Fichier de configuration")
    parser.add_argument("--vector-store", choices=["chroma", "faiss"], 
                       default="chroma", help="Type de base vectorielle")
    parser.add_argument("--store-path", type=str, default="./vector_store",
                       help="Chemin de la base vectorielle")
    
    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    parser.add_argument("--output", "-o", type=str, help="Fichier de sortie JSON")
    parser.add_argument("--port", type=int, default=8501, help="Port pour l'interface web")
    
    args = parser.parse_args()
    
    # Chargement de la configuration
    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = RAGPipelineConfig()
        config.vector_store.store_type = args.vector_store
        config.vector_store.store_path = args.store_path
    
    if args.verbose:
        config.log_level = "DEBUG"
    
    # Commande spéciale pour l'interface web
    if args.command == "web":
        return handle_web_interface(args.port)
    
    # Création de la pipeline
    try:
        pipeline = create_pipeline(config)
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la pipeline: {e}")
        sys.exit(1)
    
    # Exécution de la commande
    result = None
    
    if args.command == "ingest":
        result = handle_ingest(pipeline, args)
    elif args.command == "search":
        result = handle_search(pipeline, args)
    elif args.command == "visualize":
        result = handle_visualize(pipeline, args)
    elif args.command == "stats":
        result = handle_stats(pipeline)
    elif args.command == "clear":
        result = handle_clear(pipeline)
    elif args.command == "health":
        result = handle_health(pipeline)
    
    # Sauvegarde du résultat
    if args.output and result:
        save_result_to_file(result, args.output)
    
    return result

def handle_web_interface(port: int):
    """Lance l'interface web"""
    try:
        print(f"🚀 Lancement de l'interface web sur le port {port}")
        print(f"📱 Ouvrez votre navigateur à: http://localhost:{port}")
        print("💡 Appuyez sur Ctrl+C pour arrêter")
        
        # Vérifier si Streamlit est installé
        try:
            import streamlit
        except ImportError:
            print("❌ Streamlit n'est pas installé. Installer avec: pip install streamlit")
            return {"error": "Streamlit non installé"}
        
        # Lancer Streamlit
        env = os.environ.copy()
        env['STREAMLIT_SERVER_PORT'] = str(port)
        
        subprocess.run([
            "streamlit", "run", "web_interface.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ], env=env)
        
        return {"success": True}
        
    except FileNotFoundError:
        print("❌ Streamlit n'est pas installé. Installer avec: pip install streamlit")
        return {"error": "Streamlit non installé"}
    except KeyboardInterrupt:
        print("\n🛑 Interface web arrêtée")
        return {"success": True, "stopped": True}
    except Exception as e:
        print(f"❌ Erreur lors du lancement de l'interface web: {e}")
        return {"error": str(e)}

def handle_ingest(pipeline, args):
    """Gère la commande d'ingestion"""
    files_to_process = []
    
    if args.file:
        files_to_process.append(args.file)
    elif args.directory:
        directory = Path(args.directory)
        if not directory.exists():
            print(f"Erreur: Répertoire non trouvé: {args.directory}")
            return None
        
        # Recherche de fichiers supportés
        supported_extensions = ['.pdf', '.txt', '.md', '.rst']
        for ext in supported_extensions:
            files_to_process.extend(directory.glob(f"*{ext}"))
            files_to_process.extend(directory.glob(f"**/*{ext}"))
        
        files_to_process = [str(f) for f in files_to_process]
    else:
        print("Erreur: Spécifiez --file ou --directory")
        return None
    
    if not files_to_process:
        print("Aucun fichier à traiter")
        return None
    
    print(f"Ingestion de {len(files_to_process)} fichier(s)...")
    
    if len(files_to_process) == 1:
        result = pipeline.ingest_document(files_to_process[0])
        print_ingest_result(result)
        return result.to_dict()
    else:
        results = pipeline.ingest_multiple_documents(files_to_process)
        
        successful = sum(1 for r in results if r.success)
        print(f"\nRésultats: {successful}/{len(results)} documents traités avec succès")
        
        for result in results:
            if not result.success:
                print(f"Échec: {result.error_message}")
        
        return [r.to_dict() for r in results]

def handle_search(pipeline, args):
    """Gère la commande de recherche"""
    if not args.query:
        print("Erreur: Spécifiez une requête avec --query")
        return None
    # Parsing des filtres
    filters = None
    if args.filters:
        try:
            filters = json.loads(args.filters)
        except json.JSONDecodeError:
            print("Erreur: Filtres JSON invalides")
            return None
    print(f"Recherche: '{args.query}' (k={args.k})")
    # Détection automatique du type de requête
    from pipeline import is_image_query
    query_type = "image" if is_image_query(args.query) else "text"
    results = pipeline.search(args.query, args.k, filters, query_type=query_type)
    if not results:
        print("Aucun résultat trouvé")
        return []
    print(f"\n{len(results)} résultat(s) trouvé(s):")
    for i, result in enumerate(results, 1):
        print(f"\n--- Résultat {i} ---")
        print(f"ID: {result.chunk_id}")
        print(f"Type: {result.chunk_type.value}")
        print(f"Page: {result.page_number}")
        print(f"Score: {result.score:.4f}")
        print(f"Contenu: {result.content[:200]}...")
        # Affiche le chemin de l'image si présent
        image_path = result.metadata.get("image_path") or result.metadata.get("path") or None
        if image_path:
            print(f"Chemin de l'image: {image_path}")
            print(f"Pour ouvrir l'image: file://{image_path}")
        if result.metadata.get("questions"):
            questions = result.metadata["questions"].split(" | ")
            if questions:
                print(f"Questions: {questions[0][:100]}...")
    return [r.to_dict() for r in results]

def handle_visualize(pipeline, args):
    """Gère la commande de visualisation"""
    if not args.file:
        print("Erreur: Spécifiez un fichier avec --file")
        return None
    
    if not Path(args.file).exists():
        print(f"Erreur: Fichier non trouvé: {args.file}")
        return None
    
    try:
        # Vérifier les dépendances de visualisation
        missing_deps = []
        try:
            import matplotlib
        except ImportError:
            missing_deps.append("matplotlib")
        
        try:
            import seaborn
        except ImportError:
            missing_deps.append("seaborn")
        
        try:
            import plotly
        except ImportError:
            missing_deps.append("plotly")
        
        if missing_deps:
            print(f"❌ Dépendances manquantes: {', '.join(missing_deps)}")
            print("💡 Installer avec: pip install matplotlib seaborn plotly")
            return None
        
        from visualizer import ChunkVisualizer, visualize_document, create_quick_preview
        
        print(f"🎨 Génération de visualisations pour: {args.file}")
        
        # Récupérer le document depuis la pipeline (si déjà ingéré)
        # Sinon, l'ingérer d'abord
        print("📖 Vérification de l'ingestion...")
        result = pipeline.ingest_document(args.file)
        
        if not result.success:
            print(f"❌ Erreur lors de l'ingestion: {result.error_message}")
            return None
        
        document = result.document
        visualizer = ChunkVisualizer()
        visualizer.output_dir = Path(args.output_dir)
        visualizer.output_dir.mkdir(exist_ok=True)
        
        viz_results = {}
        
        if args.type == "overview" or args.type == "all":
            print("📊 Génération de la vue d'ensemble...")
            preview = create_quick_preview(document.chunks)
            print(preview)
            viz_results['preview'] = preview
        
        if args.type == "structure" or args.type == "all":
            print("🏗️ Génération de la structure...")
            path = visualizer.visualize_document_structure(document)
            viz_results['structure'] = path
            print(f"   Sauvegardé: {path}")
        
        if args.type == "content" or args.type == "all":
            print("📝 Génération du contenu...")
            path = visualizer.visualize_chunk_content(document.chunks)
            viz_results['content'] = path
            print(f"   Sauvegardé: {path}")
        
        if args.type == "positions" or args.type == "all":
            print("📍 Génération des positions...")
            path = visualizer.visualize_chunk_positions(document)
            viz_results['positions'] = path
            print(f"   Sauvegardé: {path}")
        
        if args.type == "embeddings" or args.type == "all":
            if any(c.embedding is not None for c in document.chunks):
                print("🧠 Génération de l'espace des embeddings...")
                try:
                    path = visualizer.visualize_embedding_space(document.chunks)
                    viz_results['embeddings'] = path
                    print(f"   Sauvegardé: {path}")
                except ImportError:
                    print("⚠️ UMAP non disponible, utilisation de PCA")
                    path = visualizer.visualize_embedding_space(document.chunks, method="pca")
                    viz_results['embeddings'] = path
                    print(f"   Sauvegardé: {path}")
            else:
                print("⚠️ Aucun embedding disponible")
        
        if args.type == "report" or args.type == "all":
            print("📋 Génération du rapport complet...")
            path = visualizer.create_chunk_report(document)
            viz_results['report'] = path
            print(f"   Rapport HTML: {path}")
        
        print(f"✅ Visualisations générées dans: {args.output_dir}")
        return viz_results
        
    except ImportError as e:
        print(f"❌ Dépendance manquante pour la visualisation: {e}")
        print("💡 Installer avec: pip install matplotlib seaborn plotly umap-learn")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la génération des visualisations: {e}")
        return None

def handle_stats(pipeline):
    """Gère la commande de statistiques"""
    stats = pipeline.get_statistics()
    
    print("=== Statistiques de la Pipeline ===")
    print(f"Documents traités: {stats['pipeline_state']['documents_processed']}")
    print(f"Chunks totaux: {stats['pipeline_state']['total_chunks']}")
    print(f"Embeddings: {stats['pipeline_state']['total_embeddings']}")
    print(f"Chunks texte: {stats['pipeline_state']['text_chunks']}")
    print(f"Chunks tableau: {stats['pipeline_state']['table_chunks']}")
    print(f"Chunks image: {stats['pipeline_state']['image_chunks']}")
    print(f"Vector store: {stats['vector_store_count']} documents")
    
    print(f"\nConfiguration:")
    for key, value in stats['config_summary'].items():
        print(f"  {key}: {value}")
    
    # Informations sur les embeddings
    embedding_dims = stats.get('embedding_dimensions', {})
    if embedding_dims:
        print(f"\nDimensions des embeddings:")
        for emb_type, dim in embedding_dims.items():
            print(f"  {emb_type}: {dim}")
    
    # Formats supportés
    supported_formats = stats.get('supported_formats', [])
    if supported_formats:
        print(f"\nFormats supportés: {', '.join(supported_formats)}")
    
    return stats

def handle_clear(pipeline):
    """Gère la commande de vidage"""
    print("Vidage de la base vectorielle...")
    
    # Demander confirmation
    response = input("Êtes-vous sûr de vouloir vider la base vectorielle ? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("Opération annulée")
        return {"success": False, "cancelled": True}
    
    success = pipeline.clear_vector_store()
    
    if success:
        print("✅ Base vectorielle vidée avec succès")
    else:
        print("❌ Erreur lors du vidage")
    
    return {"success": success}

def handle_health(pipeline):
    """Gère la commande de vérification de santé"""
    health = pipeline.health_check()
    
    print(f"Statut global: {health['status']}")
    
    print("\nComposants:")
    for component, status in health['components'].items():
        if status['status'] == 'ok':
            print(f"  ✅ {component}: OK")
            # Afficher des détails supplémentaires si disponibles
            if 'chunk_count' in status:
                print(f"     Chunks: {status['chunk_count']}")
            if 'embedding_dim' in status:
                print(f"     Dimension: {status['embedding_dim']}")
        else:
            print(f"  ❌ {component}: ERREUR")
            print(f"     {status['error']}")
    
    if health['errors']:
        print(f"\nErreurs détectées ({len(health['errors'])}):")
        for error in health['errors']:
            print(f"  - {error}")
    else:
        print("\n✅ Aucune erreur détectée")
    
    return health

def print_ingest_result(result):
    """Affiche le résultat d'ingestion"""
    if result.success:
        print(f"✅ Ingestion réussie en {result.processing_time:.2f}s")
        print(f"  Chunks créés: {result.chunks_created}")
        print(f"  Embeddings générés: {result.embeddings_generated}")
        
        if result.document:
            stats = result.document.get_statistics()
            print(f"  Pages: {stats['total_pages']}")
            print(f"  Types: {stats['chunk_types']}")
            print(f"  Questions: {stats['total_questions']}")
    else:
        print(f"❌ Échec de l'ingestion: {result.error_message}")
        if result.warnings:
            print("⚠️ Avertissements:")
            for warning in result.warnings:
                print(f"  - {warning}")

def save_result_to_file(result, output_file):
    """Sauvegarde le résultat dans un fichier JSON"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"📁 Résultat sauvegardé dans {output_file}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")

def create_sample_config():
    """Crée un fichier de configuration d'exemple"""
    config = RAGPipelineConfig()
    save_config_to_file(config, "config_example.json")
    print("📄 Fichier de configuration d'exemple créé: config_example.json")

def show_help():
    """Affiche l'aide détaillée"""
    help_text = """
🔍 Pipeline RAG Multimodal - Guide d'utilisation

=== COMMANDES PRINCIPALES ===

📤 INGESTION:
  python main.py ingest --file document.pdf
  python main.py ingest --directory ./documents --verbose

🔍 RECHERCHE:
  python main.py search --query "intelligence artificielle" --k 10
  python main.py search --query "machine learning" --filters '{"chunk_type": "text"}'

🎨 VISUALISATION:
  python main.py visualize --file doc.pdf --type overview
  python main.py visualize --file doc.pdf --type report --output-dir ./viz

🌐 INTERFACE WEB:
  python main.py web --port 8501

📊 STATISTIQUES:
  python main.py stats --verbose

🏥 SANTÉ:
  python main.py health

🗑️ NETTOYAGE:
  python main.py clear

=== OPTIONS DE VISUALISATION ===
  --type overview      Vue d'ensemble rapide (défaut)
  --type structure     Structure du document
  --type content       Contenu détaillé des chunks
  --type positions     Positions dans le document
  --type embeddings    Espace des embeddings
  --type report        Rapport HTML complet
  --type all           Toutes les visualisations

=== CONFIGURATION ===
  --config config.json          Fichier de configuration
  --vector-store chroma|faiss    Type de base vectorielle
  --store-path ./vector_store    Chemin de stockage
  --verbose                      Mode verbeux
  --output fichier.json          Sauvegarde des résultats

=== EXEMPLES AVANCÉS ===

# Pipeline complète avec visualisation
python main.py ingest --file rapport.pdf --verbose
python main.py visualize --file rapport.pdf --type all
python main.py search --query "résultats financiers" --k 5

# Configuration personnalisée
python main.py create-config  # Créer un exemple de config
python main.py ingest --config my_config.json --file doc.pdf

# Interface web avec port personnalisé
python main.py web --port 8080

# Recherche avec filtres complexes
python main.py search --query "tableaux" --filters '{
  "chunk_type": "table",
  "min_page": 5,
  "max_page": 20
}'

=== FORMATS SUPPORTÉS ===
  📄 PDF: Extraction complète (texte, tableaux, images)
  📝 TXT: Fichiers texte simples
  📋 MD:  Fichiers Markdown
  📃 RST: Fichiers reStructuredText

=== DÉPENDANCES OPTIONNELLES ===
  pip install umap-learn     # Pour visualisation UMAP
  pip install streamlit       # Pour interface web
  pip install scikit-learn    # Pour PCA, t-SNE

    """
    print(help_text)

if __name__ == "__main__":
    # Gestion des arguments spéciaux
    if len(sys.argv) > 1:
        if sys.argv[1] == "create-config":
            create_sample_config()
            sys.exit(0)
        elif sys.argv[1] == "help" or sys.argv[1] == "--help":
            show_help()
            sys.exit(0)
    
    try:
        result = main()
        if result is None:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)

# Exemple d'utilisation intégré
def example_usage():
    """Exemple d'utilisation de la pipeline avec visualisations"""
    print("🚀 Exemple d'utilisation de la Pipeline RAG Multimodal")
    
    # Configuration
    pipeline = create_pipeline()
    
    # Ingestion d'un document (exemple)
    example_file = "exemple_document.pdf"
    if Path(example_file).exists():
        print(f"📖 Ingestion de {example_file}")
        result = pipeline.ingest_document(example_file)
        
        if result.success:
            print(f"✅ Document traité: {result.chunks_created} chunks")
            
            # Aperçu rapide des chunks
            from visualizer import create_quick_preview
            preview = create_quick_preview(result.document.chunks[:10])
            print(preview)
            
            # Recherche de test
            search_results = pipeline.search("intelligence artificielle", k=3)
            print(f"\n🔍 Recherche: {len(search_results)} résultats")
            
            for i, res in enumerate(search_results, 1):
                print(f"  {i}. Score: {res.score:.3f} - {res.content[:50]}...")
            
            # Génération de visualisations
            try:
                from visualizer import visualize_document
                viz_results = visualize_document(result.document)
                print(f"\n🎨 Visualisations créées: {list(viz_results.keys())}")
                
            except ImportError:
                print("⚠️ Modules de visualisation non disponibles")
                print("💡 Installer avec: pip install matplotlib seaborn plotly")
        
        else:
            print(f"❌ Erreur: {result.error_message}")
    
    else:
        print(f"⚠️ Fichier d'exemple non trouvé: {example_file}")
        print("💡 Utilisez vos propres fichiers PDF/TXT")
    
    print("\n=== Commandes disponibles ===")
    print("🌐 Interface web:    python main.py web")
    print("📤 Ingestion:        python main.py ingest --file document.pdf")
    print("🔍 Recherche:        python main.py search --query 'votre requête'")
    print("🎨 Visualisation:    python main.py visualize --file doc.pdf --type report")
    print("📊 Statistiques:     python main.py stats")
    print("🏥 Santé système:    python main.py health")
    print("📋 Aide complète:    python main.py help")

# Point d'entrée alternatif pour les tests
if __name__ == "__main__" and len(sys.argv) == 1:
    print("🎯 Aucune commande spécifiée, lancement de l'exemple...")
    print("💡 Utilisez 'python main.py help' pour voir toutes les options")
    print("=" * 60)
    example_usage()